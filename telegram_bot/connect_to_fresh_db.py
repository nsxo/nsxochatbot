#!/usr/bin/env python3
"""
Script to connect your Telegram bot to the same fresh database as the admin dashboard.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def update_env_file():
    """Update the .env file with the fresh database URL."""
    
    # The same DATABASE_URL from Railway
    fresh_database_url = "postgresql://postgres:MLAlHoYVzlBJavPOejpYISXTBzsXTYEJ@postgres.railway.internal:5432/railway"
    
    env_file_path = project_root / '.env'
    
    print("🔧 Updating bot configuration to use fresh database...")
    
    # Read existing .env file or create new one
    env_lines = []
    if env_file_path.exists():
        with open(env_file_path, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add DATABASE_URL
    database_url_found = False
    for i, line in enumerate(env_lines):
        if line.startswith('DATABASE_URL='):
            env_lines[i] = f'DATABASE_URL={fresh_database_url}\n'
            database_url_found = True
            break
    
    if not database_url_found:
        env_lines.append(f'DATABASE_URL={fresh_database_url}\n')
    
    # Write updated .env file
    with open(env_file_path, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Updated {env_file_path}")
    print(f"📍 Database URL: {fresh_database_url[:50]}...")

def test_database_connection():
    """Test if the bot can connect to the fresh database."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        database_url = "postgresql://postgres:MLAlHoYVzlBJavPOejpYISXTBzsXTYEJ@postgres.railway.internal:5432/railway"
        
        print("\n🔍 Testing database connection...")
        
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        
        with conn.cursor() as cursor:
            # Test connection
            cursor.execute("SELECT version();")
            version = cursor.fetchone()['version']
            print(f"✅ PostgreSQL version: {version}")
            
            # Check if bot tables exist
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'bot_settings', 'products', 'payment_logs')
            """)
            tables = cursor.fetchall()
            table_names = [t['table_name'] for t in tables]
            print(f"✅ Bot tables found: {table_names}")
            
            # Check some sample data
            cursor.execute("SELECT COUNT(*) as user_count FROM users")
            user_count = cursor.fetchone()['user_count']
            print(f"✅ Users in database: {user_count}")
            
            cursor.execute("SELECT COUNT(*) as settings_count FROM bot_settings")
            settings_count = cursor.fetchone()['settings_count']
            print(f"✅ Settings in database: {settings_count}")
            
        conn.close()
        print("✅ Database connection test successful!")
        return True
        
    except ImportError:
        print("❌ psycopg2 not available - install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Connecting Telegram Bot to Fresh Database")
    print("=" * 50)
    
    # Update environment file
    update_env_file()
    
    # Test database connection
    if test_database_connection():
        print("\n🎉 SUCCESS!")
        print("\n📋 Next Steps:")
        print("1. Your bot is now configured to use the same database as the admin dashboard")
        print("2. Restart your bot to apply the new database connection")
        print("3. Test your bot by sending /start")
        print("4. Check the admin dashboard for live user data")
        print("\n🌐 Admin Dashboard: https://nsxochatbot-production.up.railway.app")
    else:
        print("\n❌ Database connection failed")
        print("Please check the database URL and try again")

if __name__ == "__main__":
    main() 