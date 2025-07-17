#!/usr/bin/env python3
"""
Database Setup Verification Script
Checks if the database is properly configured with all required functionality.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    print("❌ psycopg2 not available")
    HAS_POSTGRES = False
    sys.exit(1)

def get_database_connection():
    """Get database connection."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return None
    
    try:
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def check_tables_exist(conn):
    """Check if all required tables exist."""
    print("🔍 Checking database tables...")
    
    required_tables = [
        'users',
        'conversations', 
        'bot_settings',
        'products',
        'payment_logs',
        'auto_recharge_settings'
    ]
    
    missing_tables = []
    existing_tables = []
    
    try:
        with conn.cursor() as cursor:
            for table in required_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    existing_tables.append(table)
                else:
                    missing_tables.append(table)
        
        print(f"✅ Existing tables: {', '.join(existing_tables)}")
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False
        else:
            print("✅ All required tables exist")
            return True
            
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def check_default_settings(conn):
    """Check if default bot settings are configured."""
    print("\n🔍 Checking bot settings...")
    
    required_settings = [
        'welcome_message',
        'cost_text_message',
        'cost_photo_message', 
        'cost_voice_message',
        'time_per_message_seconds',
        'min_content_price',
        'max_content_price',
        'admin_status',
        'low_credit_threshold',
        'low_time_threshold'
    ]
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT setting_key, setting_value FROM bot_settings")
            existing_settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
            
            missing_settings = []
            configured_settings = []
            
            for setting in required_settings:
                if setting in existing_settings:
                    configured_settings.append(f"{setting}={existing_settings[setting]}")
                else:
                    missing_settings.append(setting)
            
            print(f"✅ Configured settings ({len(configured_settings)}):")
            for setting in configured_settings:
                print(f"   {setting}")
            
            if missing_settings:
                print(f"⚠️ Missing settings ({len(missing_settings)}): {', '.join(missing_settings)}")
                return False, missing_settings
            else:
                print("✅ All required settings configured")
                return True, []
                
    except Exception as e:
        print(f"❌ Error checking settings: {e}")
        return False, []

def check_sample_products(conn):
    """Check if sample products exist for user purchases."""
    print("\n🔍 Checking sample products...")
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM products WHERE is_active = true")
            products = cursor.fetchall()
            
            if products:
                print(f"✅ Found {len(products)} active products:")
                for product in products:
                    print(f"   {product['label']} - {product['amount']} {product['item_type']}")
                return True
            else:
                print("⚠️ No active products found")
                print("💡 Users won't be able to purchase credits without products")
                return False
                
    except Exception as e:
        print(f"❌ Error checking products: {e}")
        return False

def check_additional_tables(conn):
    """Check for additional tables that might be needed."""
    print("\n🔍 Checking additional functionality tables...")
    
    optional_tables = [
        'quick_reply_templates',
        'locked_content', 
        'content_purchases'
    ]
    
    existing_optional = []
    missing_optional = []
    
    try:
        with conn.cursor() as cursor:
            for table in optional_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    existing_optional.append(table)
                else:
                    missing_optional.append(table)
        
        if existing_optional:
            print(f"✅ Optional tables found: {', '.join(existing_optional)}")
        
        if missing_optional:
            print(f"📝 Optional tables missing: {', '.join(missing_optional)}")
            print("💡 These tables will be created automatically when features are used")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking optional tables: {e}")
        return False

def insert_default_settings(conn, missing_settings):
    """Insert missing default settings."""
    default_values = {
        'welcome_message': 'Welcome to our paid messaging service!',
        'cost_text_message': '1',
        'cost_photo_message': '3',
        'cost_voice_message': '5',
        'time_per_message_seconds': '60',
        'min_content_price': '1',
        'max_content_price': '1000',
        'admin_status': 'online',
        'low_credit_threshold': '5',
        'low_time_threshold': '300'
    }
    
    try:
        with conn.cursor() as cursor:
            for setting in missing_settings:
                if setting in default_values:
                    cursor.execute("""
                        INSERT INTO bot_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                    """, (setting, default_values[setting]))
                    print(f"✅ Added default setting: {setting}={default_values[setting]}")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"❌ Error inserting default settings: {e}")
        conn.rollback()
        return False

def create_sample_products(conn):
    """Create sample products for testing."""
    sample_products = [
        {
            'label': '10 Message Credits',
            'amount': 10,
            'item_type': 'credits',
            'description': 'Perfect for occasional messaging'
        },
        {
            'label': '25 Message Credits',
            'amount': 25, 
            'item_type': 'credits',
            'description': 'Great value pack for regular users'
        },
        {
            'label': '50 Message Credits',
            'amount': 50,
            'item_type': 'credits', 
            'description': 'Best value - most popular choice'
        },
        {
            'label': '1 Hour Chat Session',
            'amount': 3600,
            'item_type': 'time',
            'description': 'Unlimited messages for 1 hour'
        }
    ]
    
    try:
        with conn.cursor() as cursor:
            for product in sample_products:
                cursor.execute("""
                    INSERT INTO products (label, amount, item_type, description, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    product['label'],
                    product['amount'],
                    product['item_type'],
                    product['description'],
                    True
                ))
                print(f"✅ Added sample product: {product['label']}")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample products: {e}")
        conn.rollback()
        return False

def main():
    """Main function."""
    print("🔍 Database Setup Verification")
    print("=" * 50)
    
    # Connect to database
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        # Check all components
        tables_ok = check_tables_exist(conn)
        settings_ok, missing_settings = check_default_settings(conn)
        products_ok = check_sample_products(conn)
        additional_ok = check_additional_tables(conn)
        
        print("\n" + "=" * 50)
        print("📋 DATABASE SETUP SUMMARY")
        print("=" * 50)
        
        if tables_ok:
            print("✅ Database Schema: Complete")
        else:
            print("❌ Database Schema: Missing tables")
            return False
        
        if settings_ok:
            print("✅ Bot Settings: Configured")
        else:
            print("⚠️ Bot Settings: Missing defaults")
            print("\n🔧 Auto-fixing missing settings...")
            if insert_default_settings(conn, missing_settings):
                print("✅ Default settings added successfully")
            else:
                print("❌ Failed to add default settings")
                return False
        
        if products_ok:
            print("✅ Sample Products: Available")
        else:
            print("⚠️ Sample Products: Missing")
            choice = input("\n🚀 Create sample products? (y/n): ")
            if choice.lower() == 'y':
                if create_sample_products(conn):
                    print("✅ Sample products created successfully")
                else:
                    print("❌ Failed to create sample products")
        
        if additional_ok:
            print("✅ Additional Features: Ready")
        
        print("\n🎉 Database setup verification completed!")
        print("🤖 Your bot should have full functionality available.")
        
        return True
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 