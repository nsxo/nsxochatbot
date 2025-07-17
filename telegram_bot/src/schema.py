#!/usr/bin/env python3
"""
Database schema definitions and default settings.
"""

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def get_schema_queries() -> List[str]:
    """Get database schema creation queries."""
    return [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            user_id BIGINT,
            username VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            message_credits INTEGER DEFAULT 0,
            time_credits INTEGER DEFAULT 0,
            time_credits_seconds INTEGER DEFAULT 0,
            stripe_customer_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_banned BOOLEAN DEFAULT FALSE,
            ban_reason TEXT,
            last_low_balance_notification TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            auto_recharge_enabled BOOLEAN DEFAULT false,
            auto_recharge_amount INTEGER DEFAULT 10,
            auto_recharge_threshold INTEGER DEFAULT 5
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            topic_id INTEGER,
            status VARCHAR(50) DEFAULT 'active',
            priority INTEGER DEFAULT 0,
            last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_pinned BOOLEAN DEFAULT FALSE,
            notes TEXT,
            UNIQUE(user_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS bot_settings (
            id SERIAL PRIMARY KEY,
            setting_key VARCHAR(255) UNIQUE NOT NULL,
            setting_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            stripe_product_id VARCHAR(255),
            stripe_price_id VARCHAR(255),
            label VARCHAR(255) NOT NULL,
            amount INTEGER NOT NULL,
            item_type VARCHAR(50) NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS locked_content (
            id SERIAL PRIMARY KEY,
            content_type VARCHAR(50) NOT NULL,
            file_id VARCHAR(255) NOT NULL,
            price INTEGER NOT NULL,
            description TEXT,
            created_by BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            thumbnail_file_id VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS payment_logs (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            credit_type VARCHAR(50),
            amount INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            stripe_session_id VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS auto_recharge_settings (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            stripe_customer_id VARCHAR(255),
            stripe_payment_method_id VARCHAR(255),
            enabled BOOLEAN DEFAULT FALSE,
            threshold INTEGER DEFAULT 5,
            amount INTEGER DEFAULT 25,
            monthly_limit DECIMAL(10,2) DEFAULT 100.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS quick_replies (
            id SERIAL PRIMARY KEY,
            keyword VARCHAR(100) UNIQUE NOT NULL,
            response TEXT NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]


def get_default_settings() -> List[Tuple[str, str]]:
    """Get default bot settings."""
    return [
        ('welcome_message', 'Welcome to our paid messaging service!'),
        ('cost_text_message', '1'),
        ('cost_photo_message', '3'),
        ('cost_voice_message', '5'),
        ('time_per_message_seconds', '60'),
        ('min_content_price', '1'),
        ('max_content_price', '1000'),
        ('admin_status', 'online'),
        ('auto_recharge_enabled', 'false'),
        ('low_credit_threshold', '5'),
        ('low_time_threshold', '300')
    ]

def get_default_products() -> List[Tuple]:
    """Get enhanced default products with better value propositions."""
    return [
        ('prod_starter', 'price_starter', '🚀 Starter Pack', 10, 'credits', 'Perfect for trying out the service • 10 credits', True),
        ('prod_basic', 'price_basic', '💼 Basic Pack', 25, 'credits', 'Great for regular users • 25 credits • 2.5x value', True),
        ('prod_premium', 'price_premium', '⭐ Premium Pack', 50, 'credits', 'Most popular choice • 50 credits • 5x value', True),
        ('prod_power', 'price_power', '🏆 Power Pack', 100, 'credits', 'Best value for heavy users • 100 credits • 10x value', True),
        ('prod_mega', 'price_mega', '💎 Mega Pack', 200, 'credits', 'Ultimate package • 200 credits • 25% bonus • VIP status', True),
        ('prod_enterprise', 'price_enterprise', '🌟 Enterprise Pack', 500, 'credits', 'For power users • 500 credits • 40% bonus • VIP perks', True),
    ]

def initialize_default_data():
    """Initialize database with default settings and products."""
    try:
        # Import here to avoid circular imports
        from src.database import db_manager
        
        # Insert default settings
        for key, value in get_default_settings():
            query = """
                INSERT INTO bot_settings (setting_key, setting_value) 
                VALUES (%s, %s) 
                ON CONFLICT (setting_key) DO NOTHING
            """ if db_manager._db_type == 'postgresql' else """
                INSERT OR IGNORE INTO bot_settings (setting_key, setting_value) 
                VALUES (?, ?)
            """
            db_manager.execute_query(query, (key, value))
        
        # Insert default products
        for product in get_default_products():
            query = """
                INSERT INTO products (stripe_product_id, stripe_price_id, label, amount, item_type, description, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT DO NOTHING
            """ if db_manager._db_type == 'postgresql' else """
                INSERT OR IGNORE INTO products (stripe_product_id, stripe_price_id, label, amount, item_type, description, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            db_manager.execute_query(query, product)
            
        logger.info("✅ Default data initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing default data: {e}")

def ensure_default_data():
    """Ensure default data exists in the database."""
    try:
        initialize_default_data()
    except Exception as e:
        logger.error(f"Failed to ensure default data: {e}")

# Add this call to the DatabaseManager initialization