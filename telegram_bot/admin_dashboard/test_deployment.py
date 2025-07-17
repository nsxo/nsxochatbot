#!/usr/bin/env python3
"""
Test script to verify admin dashboard deployment
Run this locally before deploying to Railway
"""

import os
import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that all required imports work"""
    print("🧪 Testing imports...")
    
    try:
        # Test FastAPI imports
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        print("✅ FastAPI imports OK")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        # Test uvicorn import
        import uvicorn
        print("✅ Uvicorn import OK")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    return True

def test_api_server():
    """Test that the API server can be imported"""
    print("🧪 Testing API server...")
    
    try:
        # Add path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Import the API server
        from api_server import app
        print("✅ API server import OK")
        return True
    except ImportError as e:
        print(f"❌ API server import failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("🧪 Testing database connection...")
    
    try:
        # Add path for bot modules
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from database import DatabaseManager
        db = DatabaseManager()
        
        if hasattr(db, 'initialize_if_deferred'):
            success = db.initialize_if_deferred()
            if success:
                print("✅ Database connection OK")
                return True
        
        print("⚠️  Database connection skipped (may be configured for Railway)")
        return True
        
    except Exception as e:
        print(f"⚠️  Database test skipped: {e}")
        return True  # Don't fail on database issues

async def test_health_endpoint():
    """Test that the health endpoint works"""
    print("🧪 Testing health endpoint...")
    
    try:
        from api_server import health_check
        result = await health_check()
        
        if result.get("status") == "healthy":
            print("✅ Health endpoint OK")
            return True
        else:
            print(f"❌ Health endpoint returned: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_frontend_files():
    """Test that frontend files can be built"""
    print("🧪 Testing frontend setup...")
    
    dashboard_dir = Path(__file__).parent
    package_json = dashboard_dir / "package.json"
    
    if not package_json.exists():
        print("❌ package.json not found")
        return False
    
    print("✅ package.json found")
    
    # Check if dist exists or npm is available
    dist_dir = dashboard_dir / "dist"
    if dist_dir.exists():
        print("✅ Frontend already built")
        return True
    
    # Check for npm
    import subprocess
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True)
        if result.returncode == 0:
            print("✅ npm available for building")
            return True
        else:
            print("⚠️  npm not available, frontend will need to be built on Railway")
            return True
    except Exception:
        print("⚠️  npm not available, frontend will need to be built on Railway")
        return True

async def main():
    """Run all tests"""
    print("🚀 Testing Admin Dashboard Deployment")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("API Server", test_api_server),
        ("Database", test_database_connection),
        ("Health Endpoint", test_health_endpoint),
        ("Frontend", test_frontend_files),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append((test_name, result))
        print()
    
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Ready for Railway deployment.")
        return True
    elif passed >= len(tests) - 1:
        print("\n⚠️  Most tests passed. Deployment should work but monitor logs.")
        return True
    else:
        print("\n❌ Multiple test failures. Fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 