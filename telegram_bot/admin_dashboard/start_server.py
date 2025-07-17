#!/usr/bin/env python3
"""
Railway Startup Script
Starts both the Telegram bot and the admin dashboard API server.
"""

import os
import sys
import asyncio
import subprocess
import threading
import time
from pathlib import Path

def setup_environment():
    """Set up the environment for both bot and dashboard"""
    
    # Add src directory to Python path
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    sys.path.insert(0, str(project_root))
    
    print("✅ Environment configured")

def build_frontend():
    """Build the React frontend for production"""
    
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    # Skip frontend build if dist already exists (Docker handles this)
    if os.path.exists("dist"):
        print("✅ Frontend already built")
        return
    
    print("📦 Installing frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], check=True, capture_output=True)
        print("✅ Frontend dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("Continuing with existing build...")
    
    print("🏗️  Building frontend...")
    try:
        subprocess.run(["npm", "run", "build"], check=True, capture_output=True)
        print("✅ Frontend built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build frontend: {e}")
        print("Continuing without frontend build...")

def start_bot():
    """Start the Telegram bot in a separate thread"""
    
    def run_bot():
        try:
            # Change to project root
            project_root = Path(__file__).parent.parent
            os.chdir(project_root)
            
            print("🤖 Starting Telegram bot...")
            
            # Try to import and run the bot
            try:
                sys.path.insert(0, "src")
                from bot import main as bot_main
                asyncio.run(bot_main())
            except ImportError as e:
                print(f"⚠️  Bot import failed: {e}")
                print("Running without bot (dashboard only)")
            except Exception as e:
                print(f"❌ Bot startup failed: {e}")
                print("Continuing with dashboard only...")
                
        except Exception as e:
            print(f"❌ Bot thread error: {e}")
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    print("✅ Bot thread started")
    
    return bot_thread

async def start_dashboard():
    """Start the admin dashboard API server"""
    
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    print("🌐 Starting admin dashboard...")
    
    # Import and run the dashboard API
    from api_server import main
    await main()

async def main():
    """Main startup function"""
    
    print("🚀 Starting Railway deployment...")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Build frontend (only if needed)
    if not os.path.exists(Path(__file__).parent / "dist"):
        build_frontend()
    
    # Start bot in background
    bot_thread = start_bot()
    
    # Give bot time to start
    await asyncio.sleep(3)
    
    # Start dashboard (this will run in foreground)
    print("🌐 Starting dashboard server on port", os.getenv("PORT", 8000))
    await start_dashboard()

if __name__ == "__main__":
    asyncio.run(main()) 