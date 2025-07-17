#!/usr/bin/env python3
"""
Debug script to check products table and fix API issues.
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    logger.error("psycopg2 not available")
    exit(1)

def main():
    """Debug products table."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not set")
        exit(1)
    
    logger.info(f"Connecting to database: {database_url[:30]}...")
    
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        
        with conn.cursor() as cursor:
            # Check if products table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'products'
                )
            """)
            table_exists = cursor.fetchone()[0]
            logger.info(f"Products table exists: {table_exists}")
            
            if table_exists:
                # Get table structure
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'products'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                logger.info("Products table columns:")
                for col in columns:
                    logger.info(f"  - {col['column_name']}: {col['data_type']}")
                
                # Get sample data
                cursor.execute("SELECT * FROM products LIMIT 5")
                products = cursor.fetchall()
                logger.info(f"Found {len(products)} products:")
                for product in products:
                    logger.info(f"  - {dict(product)}")
            else:
                logger.error("Products table does not exist!")
        
        conn.close()
        logger.info("Debug completed successfully")
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main() 