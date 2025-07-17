#!/usr/bin/env python3
"""
Database initialization script for admin dashboard.
Creates all required tables and populates with default data.
"""

import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    logger.error("psycopg2 not available")
    HAS_POSTGRES = False
    exit(1)

def get_database_url() -> Optional[str]:
    """Get database URL from environment."""
    return os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')

def create_tables(conn):
    """Create all required tables."""
    logger.info("Creating database tables...")
    
    with conn.cursor() as cursor:
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(100),
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                message_credits INTEGER DEFAULT 0,
                is_banned BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bot settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                id SERIAL PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                credits INTEGER NOT NULL,
                price_cents INTEGER NOT NULL,
                stripe_product_id VARCHAR(100),
                stripe_price_id VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Payment logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_logs (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL,
                stripe_payment_intent_id VARCHAR(100),
                amount_cents INTEGER NOT NULL,
                credits_added INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_logs_telegram_id ON payment_logs(telegram_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_logs_timestamp ON payment_logs(timestamp)")
        
    conn.commit()
    logger.info("✅ Database tables created successfully")

def insert_default_settings(conn):
    """Insert default bot settings."""
    logger.info("Inserting default settings...")
    
    default_settings = [
        ('welcome_message', 'Welcome to NSXoChat! 🚀 This is a premium AI chat service. Purchase credits to start chatting with our advanced AI.'),
        ('cost_text_message', '1'),
        ('cost_photo_message', '3'),
        ('cost_voice_message', '5'),
        ('min_content_price', '1'),
        ('max_content_price', '1000'),
        ('low_credit_threshold', '5'),
        ('auto_recharge_enabled', 'false')
    ]
    
    with conn.cursor() as cursor:
        for key, value in default_settings:
            cursor.execute("""
                INSERT INTO bot_settings (setting_key, setting_value)
                VALUES (%s, %s)
                ON CONFLICT (setting_key) DO NOTHING
            """, (key, value))
    
    conn.commit()
    logger.info("✅ Default settings inserted")

def insert_sample_products(conn):
    """Insert sample credit packages."""
    logger.info("Inserting sample products...")
    
    sample_products = [
        ('Starter Pack', '50 credits for casual chatting', 50, 500, True),
        ('Power User', '200 credits for frequent use', 200, 1500, True),
        ('Premium Pack', '500 credits for heavy users', 500, 3000, True),
        ('Enterprise', '1000 credits for unlimited access', 1000, 5000, True)
    ]
    
    with conn.cursor() as cursor:
        for name, description, credits, price_cents, is_active in sample_products:
            cursor.execute("""
                INSERT INTO products (name, description, credits, price_cents, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (name, description, credits, price_cents, is_active))
    
    conn.commit()
    logger.info("✅ Sample products inserted")

def add_sample_users(conn):
    """Add some sample users for testing."""
    logger.info("Adding sample users...")
    
    sample_users = [
        (6781611639, 'nsxo', 'Admin', 'User', 1000, False),  # Your admin account
        (123456789, 'testuser1', 'Test', 'User1', 25, False),
        (987654321, 'testuser2', 'Test', 'User2', 75, False),
        (555666777, 'premiumuser', 'Premium', 'User', 500, False)
    ]
    
    with conn.cursor() as cursor:
        for telegram_id, username, first_name, last_name, credits, is_banned in sample_users:
            cursor.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name, message_credits, is_banned)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (telegram_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name
            """, (telegram_id, username, first_name, last_name, credits, is_banned))
    
    conn.commit()
    logger.info("✅ Sample users added")

def add_sample_payment_logs(conn):
    """Add some sample payment logs."""
    logger.info("Adding sample payment logs...")
    
    sample_payments = [
        (6781611639, 'pi_test_admin_payment', 500, 50, 'completed'),
        (123456789, 'pi_test_user1_payment', 1500, 200, 'completed'),
        (987654321, 'pi_test_user2_payment', 3000, 500, 'completed'),
        (555666777, 'pi_test_premium_payment', 5000, 1000, 'completed')
    ]
    
    with conn.cursor() as cursor:
        for telegram_id, payment_intent, amount_cents, credits, status in sample_payments:
            cursor.execute("""
                INSERT INTO payment_logs (telegram_id, stripe_payment_intent_id, amount_cents, credits_added, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (telegram_id, payment_intent, amount_cents, credits, status))
    
    conn.commit()
    logger.info("✅ Sample payment logs added")

def main():
    """Main initialization function."""
    logger.info("🚀 Starting database initialization...")
    
    database_url = get_database_url()
    if not database_url:
        logger.error("❌ No DATABASE_URL found in environment")
        exit(1)
    
    logger.info(f"📍 Connecting to database: {database_url[:30]}...")
    
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        logger.info("✅ Database connection successful")
        
        # Initialize database
        create_tables(conn)
        insert_default_settings(conn)
        insert_sample_products(conn)
        add_sample_users(conn)
        add_sample_payment_logs(conn)
        
        conn.close()
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("📊 Your admin dashboard is now ready with sample data")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        exit(1)

if __name__ == "__main__":
    main() 