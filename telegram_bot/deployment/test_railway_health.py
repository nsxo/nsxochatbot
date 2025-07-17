#!/usr/bin/env python3
"""
Test script to verify Railway deployment health check works.
This can be run locally or on Railway to test the health endpoint.
"""

import os
import sys
import time
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def test_health_endpoint():
    """Test the health endpoint."""
    print("🧪 Testing Railway Health Check...")
    
    # Set minimal environment variables for testing
    os.environ.setdefault('BOT_TOKEN', 'test_token_for_health_check')
    os.environ.setdefault('ADMIN_CHAT_ID', '123456789')
    os.environ.setdefault('PORT', '8000')
    
    try:
        # Import Flask app
        from flask import Flask
        print("✅ Flask imported successfully")
        
        # Test if we can create the app
        test_app = Flask(__name__)
        
        @test_app.route('/health')
        def health():
            return {
                'status': 'healthy',
                'service': 'telegram-bot-webhook',
                'timestamp': time.time(),
                'test_mode': True
            }
        
        # Test the health endpoint
        with test_app.test_client() as client:
            response = client.get('/health')
            print(f"✅ Health endpoint responds: {response.status_code}")
            print(f"✅ Health response: {response.get_json()}")
            
        if response.status_code == 200:
            print("🎉 Health check test PASSED!")
            return True
        else:
            print("❌ Health check test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_railway_bot_import():
    """Test if the Railway bot can be imported."""
    print("🧪 Testing Railway bot import...")
    
    try:
        # Set environment variables
        os.environ.setdefault('BOT_TOKEN', 'test_token')
        os.environ.setdefault('ADMIN_CHAT_ID', '123456789')
        os.environ.setdefault('PORT', '8000')
        
        # Try to import the bot script
        import simple_railway_bot
        print("✅ simple_railway_bot imported successfully")
        
        # Check if Flask app exists
        if hasattr(simple_railway_bot, 'app'):
            print("✅ Flask app exists")
            
            # Test health endpoint
            with simple_railway_bot.app.test_client() as client:
                response = client.get('/health')
                print(f"✅ Health endpoint: {response.status_code}")
                print(f"✅ Response: {response.get_json()}")
                
            return response.status_code == 200
        else:
            print("❌ Flask app not found")
            return False
            
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Railway Health Check Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test 1: Basic health endpoint
    print("\n📍 Test 1: Basic Health Endpoint")
    if not test_health_endpoint():
        success = False
    
    # Test 2: Railway bot import
    print("\n📍 Test 2: Railway Bot Import")
    if not test_railway_bot_import():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Railway deployment should work.")
    else:
        print("❌ SOME TESTS FAILED! Check the issues above.")
        sys.exit(1) 