#!/usr/bin/env python3
"""
Automated Railway Database Setup and Verification Script
This script helps automate the database setup process for Railway deployment.
"""

import os
import sys
import requests
import time
import json
from typing import Dict, Any, Optional

def check_railway_project_status() -> Dict[str, Any]:
    """Check Railway project status and services."""
    print("🔍 Checking Railway project status...")
    
    # Note: This would require Railway API access
    # For now, we'll provide manual instructions
    return {
        "postgresql_service": "manual_check_required",
        "bot_service": "manual_check_required",
        "instructions": [
            "1. Go to railway.app and log in",
            "2. Navigate to your project",
            "3. Check if PostgreSQL service exists",
            "4. If not, click '+ New Service' → 'PostgreSQL'"
        ]
    }

def verify_environment_variables() -> Dict[str, bool]:
    """Verify all required environment variables are set."""
    print("🔧 Verifying environment variables...")
    
    required_vars = {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'ADMIN_CHAT_ID': os.getenv('ADMIN_CHAT_ID'),
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'STRIPE_API_KEY': os.getenv('STRIPE_API_KEY'),
        'ADMIN_GROUP_ID': os.getenv('ADMIN_GROUP_ID')
    }
    
    status = {}
    for var, value in required_vars.items():
        status[var] = bool(value)
        print(f"   {var}: {'✅ Set' if value else '❌ Missing'}")
    
    return status

def test_database_connection() -> bool:
    """Test database connection."""
    print("🗄️ Testing database connection...")
    
    try:
        import psycopg2
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("   ❌ DATABASE_URL not set")
            return False
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"   ✅ PostgreSQL connection successful: {version[0]}")
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("   ⚠️ psycopg2 not available - this is normal for local testing")
        return False
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_railway_health_endpoint(domain: str = None) -> bool:
    """Test Railway health endpoint."""
    print("🏥 Testing Railway health endpoint...")
    
    if not domain:
        print("   ⚠️ Railway domain not provided, skipping health check")
        return False
    
    try:
        response = requests.get(f"https://{domain}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data.get('status', 'unknown')}")
            print(f"   🤖 Bot ready: {data.get('bot_app_ready', 'unknown')}")
            print(f"   🗄️ Database ready: {data.get('database_url_set', 'unknown')}")
            return True
        else:
            print(f"   ❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_bot_commands() -> bool:
    """Test bot commands via Telegram API."""
    print("🤖 Testing bot commands...")
    
    bot_token = os.getenv('BOT_TOKEN')
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    
    if not bot_token or not admin_chat_id:
        print("   ⚠️ BOT_TOKEN or ADMIN_CHAT_ID not set, skipping bot test")
        return False
    
    try:
        # Test bot info
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        if response.status_code == 200:
            bot_info = response.json()
            print(f"   ✅ Bot API accessible: @{bot_info['result']['username']}")
            
            # Test sending a message
            test_message = "🧪 Database setup verification test - bot is working!"
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={
                    "chat_id": admin_chat_id,
                    "text": test_message,
                    "parse_mode": "Markdown"
                }
            )
            
            if response.status_code == 200:
                print("   ✅ Bot can send messages successfully")
                return True
            else:
                print(f"   ❌ Failed to send test message: {response.text}")
                return False
        else:
            print(f"   ❌ Bot API test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Bot test error: {e}")
        return False

def generate_railway_setup_commands() -> str:
    """Generate Railway CLI commands for automation."""
    return """
# Railway CLI Setup Commands (run these manually)

# 1. Install Railway CLI (if not installed)
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Link to existing project
railway link

# 4. Add PostgreSQL service (run in project directory)
railway add --service postgresql

# 5. Set environment variables
railway variables set BOT_TOKEN="{bot_token}"
railway variables set ADMIN_CHAT_ID="{admin_chat_id}"
railway variables set ADMIN_GROUP_ID="{admin_group_id}"
railway variables set STRIPE_API_KEY="{stripe_api_key}"
railway variables set WEBHOOK_PORT="8000"

# 6. Deploy
railway up

# 7. Check status
railway status
""".format(
        bot_token=os.getenv('BOT_TOKEN', 'your_bot_token_here'),
        admin_chat_id=os.getenv('ADMIN_CHAT_ID', 'your_admin_chat_id_here'),
        admin_group_id=os.getenv('ADMIN_GROUP_ID', 'your_admin_group_id_here'),
        stripe_api_key=os.getenv('STRIPE_API_KEY', 'your_stripe_api_key_here')
    )

def main():
    """Main automation script."""
    print("🚀 Railway Database Setup Automation")
    print("=" * 50)
    
    # Step 1: Check environment variables
    env_status = verify_environment_variables()
    
    # Step 2: Check Railway project
    railway_status = check_railway_project_status()
    
    # Step 3: Test database connection
    db_connected = test_database_connection()
    
    # Step 4: Test Railway health endpoint
    railway_domain = input("\n🌐 Enter your Railway domain (e.g., yourapp-production.up.railway.app) or press Enter to skip: ").strip()
    if railway_domain:
        health_ok = test_railway_health_endpoint(railway_domain)
    else:
        health_ok = False
    
    # Step 5: Test bot commands
    bot_ok = test_bot_commands()
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("📊 SETUP SUMMARY REPORT")
    print("=" * 50)
    
    print(f"🔧 Environment Variables: {'✅ Complete' if all(env_status.values()) else '⚠️ Incomplete'}")
    for var, status in env_status.items():
        print(f"   {var}: {'✅' if status else '❌'}")
    
    print(f"🗄️ Database Connection: {'✅ Working' if db_connected else '❌ Failed'}")
    print(f"🏥 Health Endpoint: {'✅ Working' if health_ok else '⚠️ Skipped/Failed'}")
    print(f"🤖 Bot Commands: {'✅ Working' if bot_ok else '⚠️ Skipped/Failed'}")
    
    # Provide next steps
    print("\n📋 NEXT STEPS:")
    
    if not all(env_status.values()):
        print("1. ⚠️ Set missing environment variables in Railway dashboard")
    
    if not db_connected and not os.getenv('DATABASE_URL'):
        print("2. 🗄️ Add PostgreSQL service to Railway project:")
        print("   → Railway Dashboard → Your Project → '+ New Service' → 'PostgreSQL'")
    
    if env_status.get('BOT_TOKEN') and env_status.get('ADMIN_CHAT_ID'):
        print("3. 🧪 Test your bot by sending /start command")
    
    # Save Railway CLI commands
    cli_commands = generate_railway_setup_commands()
    with open('railway_setup_commands.txt', 'w') as f:
        f.write(cli_commands)
    print("4. 💾 Railway CLI commands saved to 'railway_setup_commands.txt'")
    
    print("\n🎉 Run this script again after making changes to verify setup!")

if __name__ == "__main__":
    main() 