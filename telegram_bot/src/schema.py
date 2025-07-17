#!/usr/bin/env python3
"""
Database schema definitions and default settings.
"""

from typing import List, Tuple


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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_banned BOOLEAN DEFAULT FALSE
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
            notes TEXT
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