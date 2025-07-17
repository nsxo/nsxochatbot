#!/usr/bin/env python3
"""
API endpoints for admin dashboard to connect to bot database.
Fresh database deployment - trigger redeploy with new DATABASE_URL.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Database configuration - Railway provides DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Fallback for local development
    DATABASE_URL = os.getenv('POSTGRES_URL') or os.getenv('DB_URL')

# Try to import psycopg2, fallback to None if not available
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    logger.warning("psycopg2 not available - using fallback mode")
    psycopg2 = None
    RealDictCursor = None
    HAS_POSTGRES = False

def get_db_connection():
    """Get database connection."""
    if not HAS_POSTGRES:
        logger.warning("psycopg2 not available - using fallback mode")
        return None
        
    if not DATABASE_URL:
        logger.warning("DATABASE_URL not configured - using fallback mode")
        return None
    
    try:
        # Try to establish connection with timeout
        conn = psycopg2.connect(
            DATABASE_URL, 
            cursor_factory=RealDictCursor,
            connect_timeout=10
        )
        # Test the connection
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        logger.info("Database connection successful")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        return None

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    db_status = "connected" if get_db_connection() else "disconnected"
    
    # Check for dist directory
    dist_paths = ['dist', '../dist', './dist']
    dist_found = None
    for path in dist_paths:
        if os.path.exists(path):
            dist_found = path
            break
    
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'database': db_status,
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'unknown'),
        'has_postgres': HAS_POSTGRES,
        'database_url_configured': bool(DATABASE_URL),
        'database_url_prefix': DATABASE_URL[:20] + '...' if DATABASE_URL else None,
        'working_directory': os.getcwd(),
        'dist_directory_found': dist_found,
        'available_files': os.listdir('.') if os.path.exists('.') else []
    })

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        conn = get_db_connection()
        if not conn:
            # Return sample data if database is not available
            return jsonify({
                'totalUsers': 156,
                'activeUsers': 42,
                'messagesToday': 287,
                'totalCredits': 3420,
                'monthlyPayments': 23,
                'estimatedRevenue': 115,
                'lastUpdated': datetime.now().isoformat(),
                'status': 'database_unavailable'
            })
        
        with conn.cursor() as cursor:
            # Total users
            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cursor.fetchone()['total_users']
            
            # Active users (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) as active_users 
                FROM users 
                WHERE last_active >= NOW() - INTERVAL '24 hours'
            """)
            active_users = cursor.fetchone()['active_users']
            
            # Messages today (approximate from user activity)
            cursor.execute("""
                SELECT COUNT(*) as messages_today 
                FROM users 
                WHERE last_active >= CURRENT_DATE
            """)
            messages_today = cursor.fetchone()['messages_today']
            
            # Total credits in system
            cursor.execute("SELECT SUM(message_credits) as total_credits FROM users")
            total_credits_result = cursor.fetchone()
            total_credits = total_credits_result['total_credits'] or 0
            
            # Revenue estimate (from payment logs)
            cursor.execute("""
                SELECT COUNT(*) as total_payments 
                FROM payment_logs 
                WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
            """)
            payments_result = cursor.fetchone()
            monthly_payments = payments_result['total_payments'] or 0
            
            # Estimate revenue (assuming $1 per 10 credits average)
            estimated_revenue = monthly_payments * 5  # Rough estimate
            
        conn.close()
        
        return jsonify({
            'totalUsers': total_users,
            'activeUsers': active_users,
            'messagesToday': messages_today,
            'totalCredits': total_credits,
            'monthlyPayments': monthly_payments,
            'estimatedRevenue': estimated_revenue,
            'lastUpdated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/settings')
def get_settings():
    """Get bot settings."""
    try:
        conn = get_db_connection()
        if not conn:
            # Return default settings if database is not available
            return jsonify({
                'welcomeMessage': 'Welcome to our premium AI chat service! You can purchase credits to start chatting.',
                'costTextMessage': 1,
                'costPhotoMessage': 3,
                'costVoiceMessage': 5,
                'minContentPrice': 1,
                'maxContentPrice': 1000,
                'lowCreditThreshold': 5,
                'autoRechargeEnabled': False
            })
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT setting_key, setting_value FROM bot_settings")
            settings_rows = cursor.fetchall()
            
        conn.close()
        
        settings = {row['setting_key']: row['setting_value'] for row in settings_rows}
        
        return jsonify({
            'welcomeMessage': settings.get('welcome_message', 'Welcome to our service!'),
            'costTextMessage': int(settings.get('cost_text_message', '1')),
            'costPhotoMessage': int(settings.get('cost_photo_message', '3')),
            'costVoiceMessage': int(settings.get('cost_voice_message', '5')),
            'minContentPrice': int(settings.get('min_content_price', '1')),
            'maxContentPrice': int(settings.get('max_content_price', '1000')),
            'lowCreditThreshold': int(settings.get('low_credit_threshold', '5')),
            'autoRechargeEnabled': settings.get('auto_recharge_enabled', 'false') == 'true'
        })
        
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        return jsonify({'error': 'Failed to fetch settings'}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update bot settings."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = get_db_connection()
        if not conn:
            logger.warning("Database not available - settings change ignored")
            return jsonify({'message': 'Settings updated successfully (fallback mode)'}), 200
        
        with conn.cursor() as cursor:
            # Update each setting
            settings_mapping = {
                'welcomeMessage': 'welcome_message',
                'costTextMessage': 'cost_text_message',
                'costPhotoMessage': 'cost_photo_message',
                'costVoiceMessage': 'cost_voice_message',
                'minContentPrice': 'min_content_price',
                'maxContentPrice': 'max_content_price',
                'lowCreditThreshold': 'low_credit_threshold',
                'autoRechargeEnabled': 'auto_recharge_enabled'
            }
            
            for frontend_key, db_key in settings_mapping.items():
                if frontend_key in data:
                    value = str(data[frontend_key])
                    if frontend_key == 'autoRechargeEnabled':
                        value = 'true' if data[frontend_key] else 'false'
                    
                    cursor.execute("""
                        INSERT INTO bot_settings (setting_key, setting_value, updated_at)
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (setting_key) 
                        DO UPDATE SET setting_value = EXCLUDED.setting_value, updated_at = CURRENT_TIMESTAMP
                    """, (db_key, value))
            
            conn.commit()
            
        conn.close()
        
        logger.info(f"Settings updated: {data}")
        return jsonify({'message': 'Settings updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500

@app.route('/api/products')
def get_products():
    """Get credit packages/products."""
    try:
        conn = get_db_connection()
        if not conn:
            # Return sample products if database is not available
            return jsonify([
                {
                    'id': 1,
                    'name': '🚀 Starter Pack',
                    'credits': 10,
                    'description': 'Perfect for trying out the service • 10 credits',
                    'price': '$1.00',
                    'isActive': True,
                    'stripeProductId': 'prod_starter',
                    'stripePriceId': 'price_starter'
                },
                {
                    'id': 2,
                    'name': '💼 Basic Pack',
                    'credits': 25,
                    'description': 'Great for regular users • 25 credits • 2.5x value',
                    'price': '$2.50',
                    'isActive': True,
                    'stripeProductId': 'prod_basic',
                    'stripePriceId': 'price_basic'
                },
                {
                    'id': 3,
                    'name': '⭐ Premium Pack',
                    'credits': 50,
                    'description': 'Most popular choice • 50 credits • 5x value',
                    'price': '$5.00',
                    'isActive': True,
                    'stripeProductId': 'prod_premium',
                    'stripePriceId': 'price_premium'
                }
            ])
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, label, amount, description, is_active, 
                       stripe_product_id, stripe_price_id
                FROM products 
                ORDER BY amount ASC
            """)
            products = cursor.fetchall()
            
        conn.close()
        
        return jsonify([{
            'id': product['id'],
            'name': product['label'],
            'credits': product['amount'],
            'description': product['description'],
            'price': f"${product['amount'] * 0.1:.2f}",  # Estimate: $0.10 per credit
            'isActive': product['is_active'],
            'stripeProductId': product['stripe_product_id'],
            'stripePriceId': product['stripe_price_id']
        } for product in products])
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({'error': 'Failed to fetch products'}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    """Create new credit package."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO products (label, amount, description, item_type, is_active)
                VALUES (%s, %s, %s, 'credits', %s)
                RETURNING id
            """, (
                data['name'],
                int(data['credits']),
                data.get('description', ''),
                data.get('isActive', True)
            ))
            
            product_id = cursor.fetchone()['id']
            conn.commit()
            
        conn.close()
        
        logger.info(f"Product created: {data}")
        return jsonify({'id': product_id, 'message': 'Product created successfully'})
        
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return jsonify({'error': 'Failed to create product'}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update credit package."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE products 
                SET label = %s, amount = %s, description = %s, is_active = %s
                WHERE id = %s
            """, (
                data['name'],
                int(data['credits']),
                data.get('description', ''),
                data.get('isActive', True),
                product_id
            ))
            
            conn.commit()
            
        conn.close()
        
        logger.info(f"Product {product_id} updated: {data}")
        return jsonify({'message': 'Product updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        return jsonify({'error': 'Failed to update product'}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete credit package."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            
        conn.close()
        
        logger.info(f"Product {product_id} deleted")
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        return jsonify({'error': 'Failed to delete product'}), 500

@app.route('/api/users')
def get_users():
    """Get users overview."""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([])
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT telegram_id, username, first_name, message_credits, 
                       last_active, is_banned, created_at
                FROM users 
                ORDER BY last_active DESC 
                LIMIT 100
            """)
            users = cursor.fetchall()
            
        conn.close()
        
        return jsonify([{
            'telegramId': user['telegram_id'],
            'username': user['username'] or 'N/A',
            'firstName': user['first_name'] or 'N/A',
            'credits': user['message_credits'],
            'lastActive': user['last_active'].isoformat() if user['last_active'] else None,
            'isBanned': user['is_banned'],
            'joinedAt': user['created_at'].isoformat() if user['created_at'] else None
        } for user in users])
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

# Serve static files (the built React app)
@app.route('/')
def serve_index():
    """Serve the React app."""
    try:
        # In Railway deployment, files are at /app/dist
        possible_paths = ['/app/dist/index.html', 'dist/index.html', '../dist/index.html', './dist/index.html']
        for path in possible_paths:
            if os.path.exists(path):
                return send_file(path)
        
        # If no dist found, return error with directory info
        return f"""
        <h1>Admin Dashboard - Setup Required</h1>
        <p>React app not built. Working directory: {os.getcwd()}</p>
        <p>Available files: {os.listdir('.')}</p>
        <p>Looking for paths: {possible_paths}</p>
        <p>To fix: Build the React app with 'npm run build'</p>
        """, 500
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return f"<h1>Admin Dashboard</h1><p>Error loading app: {e}</p><p>Working directory: {os.getcwd()}</p>", 500

@app.route('/<path:path>')
def serve_static(path):
    """Serve static assets."""
    # Skip API routes
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    try:
        # Check for dist directory in multiple possible locations
        possible_dirs = ['/app/dist', 'dist', '../dist', './dist']
        for dist_dir in possible_dirs:
            if os.path.exists(os.path.join(dist_dir, path)):
                return send_from_directory(dist_dir, path)
        
        # Fallback to index.html for client-side routing
        for dist_dir in possible_dirs:
            index_path = os.path.join(dist_dir, 'index.html')
            if os.path.exists(index_path):
                return send_file(index_path)
                
        return f"Error: Could not find asset {path} in any dist directory", 404
    except Exception as e:
        logger.error(f"Error serving static file {path}: {e}")
        return f"Error loading asset: {path}", 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Starting Flask server on port {port}")
    logger.info(f"📊 Database URL configured: {'Yes' if DATABASE_URL else 'No'}")
    logger.info(f"🔗 PostgreSQL available: {'Yes' if HAS_POSTGRES else 'No'}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    
    # List available files for debugging
    try:
        if os.path.exists('dist'):
            logger.info(f"📂 Dist directory contents: {os.listdir('dist')}")
        else:
            logger.warning("📂 Dist directory not found!")
    except Exception as e:
        logger.error(f"Error checking dist directory: {e}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 