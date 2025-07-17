#!/usr/bin/env python3
"""
Simple database connection test for admin dashboard.
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check environment variables
print("=== Environment Check ===")
print(f"DATABASE_URL configured: {bool(os.getenv('DATABASE_URL'))}")
print(f"POSTGRES_URL configured: {bool(os.getenv('POSTGRES_URL'))}")
print(f"Railway environment: {os.getenv('RAILWAY_ENVIRONMENT', 'unknown')}")

database_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
if database_url:
    print(f"Database URL prefix: {database_url[:30]}...")
else:
    print("No database URL found")

print("\n=== Testing psycopg2 ===")
try:
    import psycopg2
    print("✅ psycopg2 import successful")
    
    if database_url:
        print("\n=== Testing Database Connection ===")
        try:
            conn = psycopg2.connect(database_url, connect_timeout=10)
            print("✅ Database connection successful")
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"✅ PostgreSQL version: {version}")
                
                # Test if bot tables exist
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('users', 'bot_settings', 'products', 'payment_logs')
                """)
                tables = cursor.fetchall()
                print(f"✅ Bot tables found: {[t[0] for t in tables]}")
                
            conn.close()
            print("✅ All database tests passed!")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
    else:
        print("❌ No database URL to test")
        
except ImportError as e:
    print(f"❌ psycopg2 import failed: {e}")

print("\n=== Test Complete ===") 