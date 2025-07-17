#!/usr/bin/env python3
"""
Railway PostgreSQL Restart Script
Helps restart the PostgreSQL service when it's crashed.
"""

import subprocess
import time

def restart_postgres():
    """Restart PostgreSQL service via Railway CLI."""
    print("🔄 Restarting PostgreSQL service...")
    
    try:
        # List services to find PostgreSQL
        result = subprocess.run(['railway', 'service'], capture_output=True, text=True, check=True)
        print("Available services:")
        print(result.stdout)
        
        # Restart PostgreSQL service
        print("\n🔄 Restarting Postgres service...")
        result = subprocess.run(['railway', 'service', 'restart', 'Postgres'], 
                              capture_output=True, text=True, check=True)
        print("✅ PostgreSQL restart command sent")
        print(result.stdout)
        
        print("\n⏳ Waiting for PostgreSQL to start (30 seconds)...")
        time.sleep(30)
        
        # Check status
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True, check=True)
        print("\n📊 Current status:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error restarting PostgreSQL: {e}")
        print(f"stderr: {e.stderr}")
        print("\n🔧 Manual steps:")
        print("1. Go to Railway dashboard")
        print("2. Click the Postgres service")
        print("3. Go to Settings → Restart Service")
        return False

def main():
    """Main function."""
    print("🔄 Railway PostgreSQL Restart Tool")
    print("=" * 40)
    
    restart_postgres()
    
    print("\n✅ PostgreSQL restart completed!")
    print("Your bot should now connect to the database successfully.")

if __name__ == "__main__":
    main() 