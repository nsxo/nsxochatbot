#!/usr/bin/env python3
"""
Database migration script to add missing columns.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from src.database import db_manager
import logging

logger = logging.getLogger(__name__)

def migrate_database():
    """Add missing columns to existing tables."""
    migrations = [
        {
            'name': 'Add stripe_customer_id to users table',
            'query': """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255)
            """
        },
        {
            'name': 'Add subscription_status to users table',
            'query': """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'none'
            """
        },
        {
            'name': 'Add ban_reason to users table',
            'query': """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS ban_reason TEXT
            """
        }
    ]
    
    for migration in migrations:
        try:
            logger.info(f"Running migration: {migration['name']}")
            db_manager.execute_query(migration['query'])
            logger.info(f"✅ Migration successful: {migration['name']}")
        except Exception as e:
            logger.error(f"❌ Migration failed: {migration['name']} - {e}")
            # Continue with other migrations
    
    logger.info("🎉 Database migration completed!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    migrate_database() 