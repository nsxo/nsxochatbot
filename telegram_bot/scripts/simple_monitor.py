#!/usr/bin/env python3
"""
Simple HTTP-based monitor for Railway deployment health.
Checks the health endpoint and alerts if issues are detected.
"""

import requests
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEPLOYMENT_URL = "https://nsxochatbot-production.up.railway.app"
HEALTH_ENDPOINT = f"{DEPLOYMENT_URL}/api/health"
CHECK_INTERVAL = 300  # 5 minutes

def check_deployment_health():
    """Check if the deployment is healthy."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Deployment healthy - Database: {data.get('database', 'unknown')}")
            return True, data
        else:
            logger.error(f"❌ Health check failed - Status: {response.status_code}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Connection failed: {e}")
        return False, None

def check_api_endpoints():
    """Check if API endpoints are responding."""
    endpoints = [
        "/api/dashboard/stats",
        "/api/settings", 
        "/api/products"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            url = f"{DEPLOYMENT_URL}{endpoint}"
            response = requests.get(url, timeout=15)
            results[endpoint] = response.status_code == 200
            
            if response.status_code == 200:
                logger.info(f"✅ {endpoint} - OK")
            else:
                logger.warning(f"⚠️ {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ {endpoint} - Error: {e}")
            results[endpoint] = False
    
    return results

def monitor_deployment():
    """Main monitoring loop."""
    logger.info("🚀 Starting simple deployment monitor...")
    logger.info(f"📍 Monitoring: {DEPLOYMENT_URL}")
    logger.info(f"⏱️ Check interval: {CHECK_INTERVAL} seconds")
    
    while True:
        try:
            logger.info("🔍 Checking deployment health...")
            
            # Check health endpoint
            is_healthy, health_data = check_deployment_health()
            
            if is_healthy:
                # Check API endpoints
                api_results = check_api_endpoints()
                
                # Summary
                total_endpoints = len(api_results)
                healthy_endpoints = sum(api_results.values())
                
                logger.info(f"📊 API Status: {healthy_endpoints}/{total_endpoints} endpoints healthy")
                
                if healthy_endpoints == total_endpoints:
                    logger.info("🎉 All systems operational!")
                else:
                    logger.warning("⚠️ Some API endpoints have issues")
                    
            else:
                logger.error("💀 Deployment appears to be down!")
                
            # Wait for next check
            logger.info(f"⏰ Next check in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Monitor error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    monitor_deployment() 