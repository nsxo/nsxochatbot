#!/usr/bin/env python3
"""
Simplified Railway Startup Script
Starts the admin dashboard API server (bot runs separately if needed).
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Set environment variables for Railway
os.environ['DEFER_DB_INIT'] = 'false'  # Allow database initialization

def setup_environment():
    """Set up the environment for the dashboard"""
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    sys.path.insert(0, str(project_root))
    print("✅ Environment configured")

def build_frontend_if_needed():
    """Build the React frontend if not already built"""
    dashboard_dir = Path(__file__).parent
    dist_path = dashboard_dir / "dist"
    
    if dist_path.exists():
        print("✅ Frontend already built")
        return True
    
    print("🏗️  Building frontend...")
    try:
        os.chdir(dashboard_dir)
        
        # Install dependencies
        result = subprocess.run(["npm", "install"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm install failed: {result.stderr}")
            return False
        
        # Build the project
        result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ npm build failed: {result.stderr}")
            return False
            
        print("✅ Frontend built successfully")
        return True
        
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

async def start_dashboard():
    """Start the admin dashboard API server"""
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    print("🌐 Starting admin dashboard API...")
    
    try:
        # Import the API server
        from api_server import app
        import uvicorn
        
        # Get the port from Railway
        port = int(os.getenv("PORT", 8000))
        
        # Configure uvicorn
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        print(f"🚀 Dashboard starting on port {port}")
        await server.serve()
        
    except Exception as e:
        print(f"❌ Dashboard startup failed: {e}")
        raise

async def main():
    """Main startup function"""
    print("🚀 Starting Railway Admin Dashboard...")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Build frontend if needed
    if not build_frontend_if_needed():
        print("⚠️  Frontend build failed, continuing with existing files")
    
    # Start the dashboard
    print("🌐 Initializing dashboard server...")
    await start_dashboard()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1) 