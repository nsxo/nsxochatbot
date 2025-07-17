#!/usr/bin/env python3
"""
API endpoints for admin dashboard to connect to bot database.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

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

def get_db_connection():
    """Get database connection."""
    try:
        if not DATABASE_URL:
            logger.error("No database URL found in environment variables")
            return None
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    db_status = "connected" if get_db_connection() else "disconnected"
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'database': db_status,
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'unknown')
    })

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        conn = get_db_connection()
        if not conn:
            # Return sample data if database is not available
            return jsonify({
                'totalUsers': 0,
                'activeUsers': 0,
                'messagesToday': 0,
                'totalCredits': 0,
                'monthlyPayments': 0,
                'estimatedRevenue': 0,
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
                'welcomeMessage': 'Welcome to our service!',
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
            return jsonify({'error': 'Database connection failed'}), 500
        
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
                    'description': 'Perfect for trying out the service',
                    'price': '$1.00',
                    'isActive': True,
                    'stripeProductId': 'prod_starter',
                    'stripePriceId': 'price_starter'
                },
                {
                    'id': 2,
                    'name': '💼 Basic Pack',
                    'credits': 25,
                    'description': 'Great for regular users',
                    'price': '$2.50',
                    'isActive': True,
                    'stripeProductId': 'prod_basic',
                    'stripePriceId': 'price_basic'
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
        return send_file('dist/index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return f"<h1>Admin Dashboard</h1><p>Error loading app: {e}</p>", 500

@app.route('/<path:path>')
def serve_static(path):
    """Serve static assets."""
    try:
        return send_from_directory('dist', path)
    except Exception as e:
        # Fallback to index.html for client-side routing
        try:
            return send_file('dist/index.html')
        except:
            return f"Error loading asset: {path}", 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"Database URL configured: {'Yes' if DATABASE_URL else 'No'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 