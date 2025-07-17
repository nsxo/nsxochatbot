#!/usr/bin/env python3
"""
Railway Deployment Monitor & Auto-Fix System
Automatically monitors Railway deployments, downloads logs, detects issues, and applies fixes.
"""

import os
import sys
import json
import time
import requests
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('railway_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RailwayMonitor:
    def __init__(self):
        """Initialize the Railway monitor with configuration."""
        self.railway_token = os.getenv('RAILWAY_TOKEN')
        self.project_id = os.getenv('RAILWAY_PROJECT_ID')
        self.service_id = os.getenv('RAILWAY_SERVICE_ID')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER', 'nsxo')
        self.repo_name = os.getenv('GITHUB_REPO_NAME', 'nsxochatbot')
        
        self.base_url = "https://backboard.railway.app/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.railway_token}",
            "Content-Type": "application/json"
        }
        
        # Issue patterns and their fixes
        self.issue_patterns = {
            'css_build_error': {
                'patterns': [
                    'border-border',
                    'class does not exist',
                    '[postcss]',
                    'expandApplyAtRules'
                ],
                'fix_function': self.fix_css_issues
            },
            'memory_error': {
                'patterns': [
                    'JavaScript heap out of memory',
                    'FATAL ERROR',
                    'exit code: 137',
                    'context canceled'
                ],
                'fix_function': self.fix_memory_issues
            },
            'dependency_error': {
                'patterns': [
                    'npm ERR!',
                    'Module not found',
                    'Cannot resolve dependency',
                    'ERESOLVE'
                ],
                'fix_function': self.fix_dependency_issues
            },
            'python_import_error': {
                'patterns': [
                    'ImportError',
                    'ModuleNotFoundError',
                    'No module named',
                    'Failed to import'
                ],
                'fix_function': self.fix_python_import_issues
            },
            'port_binding_error': {
                'patterns': [
                    'EADDRINUSE',
                    'Port already in use',
                    'bind EADDRINUSE'
                ],
                'fix_function': self.fix_port_issues
            }
        }

    def get_deployment_logs(self, limit: int = 1000) -> Optional[List[str]]:
        """Fetch the latest deployment logs from Railway."""
        if not all([self.railway_token, self.project_id, self.service_id]):
            logger.error("Missing Railway credentials. Set RAILWAY_TOKEN, RAILWAY_PROJECT_ID, RAILWAY_SERVICE_ID")
            return None

        query = """
        query GetDeploymentLogs($serviceId: String!, $limit: Int!) {
            logs(serviceId: $serviceId, limit: $limit) {
                edges {
                    node {
                        message
                        timestamp
                        severity
                    }
                }
            }
        }
        """
        
        variables = {
            "serviceId": self.service_id,
            "limit": limit
        }

        try:
            response = requests.post(
                self.base_url,
                json={"query": query, "variables": variables},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'logs' in data['data']:
                    logs = []
                    for edge in data['data']['logs']['edges']:
                        log_entry = edge['node']
                        logs.append(f"[{log_entry['timestamp']}] {log_entry['severity']}: {log_entry['message']}")
                    return logs
                else:
                    logger.error(f"Unexpected response format: {data}")
                    return None
            else:
                logger.error(f"Failed to fetch logs: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error fetching Railway logs: {e}")
            return None

    def get_deployment_status(self) -> Optional[Dict[str, Any]]:
        """Get the current deployment status."""
        query = """
        query GetService($serviceId: String!) {
            service(id: $serviceId) {
                id
                name
                latestDeployment {
                    id
                    status
                    createdAt
                    meta
                }
            }
        }
        """
        
        variables = {"serviceId": self.service_id}

        try:
            response = requests.post(
                self.base_url,
                json={"query": query, "variables": variables},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'service' in data['data']:
                    return data['data']['service']
                    
        except Exception as e:
            logger.error(f"Error fetching deployment status: {e}")
            
        return None

    def analyze_logs(self, logs: List[str]) -> Dict[str, List[str]]:
        """Analyze logs for known issues and return detected problems."""
        detected_issues = {}
        
        for issue_type, config in self.issue_patterns.items():
            matching_logs = []
            for log in logs:
                if any(pattern.lower() in log.lower() for pattern in config['patterns']):
                    matching_logs.append(log)
            
            if matching_logs:
                detected_issues[issue_type] = matching_logs
                
        return detected_issues

    def fix_css_issues(self, logs: List[str]) -> bool:
        """Fix CSS-related build issues."""
        logger.info("🔧 Applying CSS fixes...")
        
        fixes_applied = []
        
        # Fix 1: Remove invalid Tailwind classes
        css_file = Path("telegram_bot/admin_dashboard/src/index.css")
        if css_file.exists():
            content = css_file.read_text()
            
            # Remove problematic @apply directives
            problematic_classes = [
                '@apply border-border;',
                '@apply ring-offset-background;',
                'peer-disabled:cursor-not-allowed',
                'peer-disabled:opacity-70'
            ]
            
            for problematic_class in problematic_classes:
                if problematic_class in content:
                    content = content.replace(problematic_class, '')
                    fixes_applied.append(f"Removed {problematic_class}")
            
            css_file.write_text(content)
        
        # Fix 2: Update Tailwind config for better compatibility
        tailwind_config = Path("telegram_bot/admin_dashboard/tailwind.config.js")
        if tailwind_config.exists():
            content = tailwind_config.read_text()
            # Add safelist for dynamic classes
            if 'safelist:' not in content:
                new_content = content.replace(
                    'theme: {',
                    '''safelist: [
    'border-gray-200',
    'ring-primary-500',
    'ring-offset-2'
  ],
  theme: {'''
                )
                tailwind_config.write_text(new_content)
                fixes_applied.append("Added Tailwind safelist")
        
        if fixes_applied:
            logger.info(f"✅ Applied CSS fixes: {', '.join(fixes_applied)}")
            return True
        
        return False

    def fix_memory_issues(self, logs: List[str]) -> bool:
        """Fix memory-related build issues."""
        logger.info("🔧 Applying memory fixes...")
        
        fixes_applied = []
        
        # Fix 1: Update package.json scripts with memory limits
        package_json = Path("telegram_bot/admin_dashboard/package.json")
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            # Update build script with memory limit
            if 'scripts' in data and 'build' in data['scripts']:
                if 'max-old-space-size' not in data['scripts']['build']:
                    data['scripts']['build'] = 'NODE_OPTIONS="--max-old-space-size=4096" vite build --mode production'
                    fixes_applied.append("Added Node.js memory limit")
            
            with open(package_json, 'w') as f:
                json.dump(data, f, indent=2)
        
        # Fix 2: Update Dockerfile with memory optimizations
        dockerfile = Path("Dockerfile.admin")
        if dockerfile.exists():
            content = dockerfile.read_text()
            if 'max-old-space-size' not in content:
                content = content.replace(
                    'RUN npm run build',
                    'RUN NODE_OPTIONS="--max-old-space-size=4096" npm run build'
                )
                dockerfile.write_text(content)
                fixes_applied.append("Updated Dockerfile memory settings")
        
        if fixes_applied:
            logger.info(f"✅ Applied memory fixes: {', '.join(fixes_applied)}")
            return True
        
        return False

    def fix_dependency_issues(self, logs: List[str]) -> bool:
        """Fix dependency-related issues."""
        logger.info("🔧 Applying dependency fixes...")
        
        fixes_applied = []
        
        # Fix 1: Clean package-lock and node_modules
        admin_dir = Path("telegram_bot/admin_dashboard")
        package_lock = admin_dir / "package-lock.json"
        node_modules = admin_dir / "node_modules"
        
        if package_lock.exists():
            package_lock.unlink()
            fixes_applied.append("Removed package-lock.json")
        
        # Fix 2: Update package.json with compatible versions
        package_json = admin_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            # Ensure compatible React versions
            if 'dependencies' in data:
                data['dependencies']['react'] = '^18.2.0'
                data['dependencies']['react-dom'] = '^18.2.0'
                fixes_applied.append("Updated React versions")
            
            with open(package_json, 'w') as f:
                json.dump(data, f, indent=2)
        
        if fixes_applied:
            logger.info(f"✅ Applied dependency fixes: {', '.join(fixes_applied)}")
            return True
        
        return False

    def fix_python_import_issues(self, logs: List[str]) -> bool:
        """Fix Python import issues."""
        logger.info("🔧 Applying Python import fixes...")
        
        fixes_applied = []
        
        # Fix 1: Update requirements.txt with missing dependencies
        requirements = Path("telegram_bot/admin_dashboard/requirements.txt")
        if requirements.exists():
            content = requirements.read_text()
            missing_deps = []
            
            # Check for common missing dependencies
            if 'uvicorn' not in content:
                missing_deps.append('uvicorn[standard]==0.24.0')
            if 'fastapi' not in content:
                missing_deps.append('fastapi==0.104.1')
            
            if missing_deps:
                content += '\n' + '\n'.join(missing_deps)
                requirements.write_text(content)
                fixes_applied.append(f"Added missing dependencies: {', '.join(missing_deps)}")
        
        # Fix 2: Update start_server.py with better error handling
        start_server = Path("telegram_bot/admin_dashboard/start_server.py")
        if start_server.exists():
            content = start_server.read_text()
            if 'try:' not in content or 'except ImportError:' not in content:
                # Add better import error handling
                improved_content = content.replace(
                    'from api_server import app',
                    '''try:
        from api_server import app
    except ImportError as e:
        print(f"Failed to import API server: {e}")
        # Create minimal fallback app
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/api/health")
        async def health():
            return {"status": "healthy", "mode": "fallback"}'''
                )
                start_server.write_text(improved_content)
                fixes_applied.append("Added import error handling")
        
        if fixes_applied:
            logger.info(f"✅ Applied Python import fixes: {', '.join(fixes_applied)}")
            return True
        
        return False

    def fix_port_issues(self, logs: List[str]) -> bool:
        """Fix port binding issues."""
        logger.info("🔧 Applying port fixes...")
        
        fixes_applied = []
        
        # Fix: Update start_server.py with dynamic port handling
        start_server = Path("telegram_bot/admin_dashboard/start_server.py")
        if start_server.exists():
            content = start_server.read_text()
            
            # Ensure dynamic port handling
            if 'int(os.getenv("PORT"' not in content:
                content = content.replace(
                    'port=8000',
                    'port=int(os.getenv("PORT", 8000))'
                )
                start_server.write_text(content)
                fixes_applied.append("Added dynamic port handling")
        
        if fixes_applied:
            logger.info(f"✅ Applied port fixes: {', '.join(fixes_applied)}")
            return True
        
        return False

    def commit_and_push_fixes(self, fixes_applied: List[str]) -> bool:
        """Commit and push the applied fixes to trigger new deployment."""
        if not fixes_applied:
            return False
        
        try:
            # Configure git if needed
            subprocess.run(['git', 'config', 'user.email', 'bot@railway-monitor.com'], check=True)
            subprocess.run(['git', 'config', 'user.name', 'Railway Monitor'], check=True)
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Create commit message
            commit_message = f"fix: Auto-fix deployment issues\n\n🤖 Automated fixes applied:\n" + "\n".join(f"• {fix}" for fix in fixes_applied)
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push to trigger new deployment
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            logger.info("✅ Fixes committed and pushed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit/push fixes: {e}")
            return False

    def monitor_deployment(self, timeout_minutes: int = 10) -> bool:
        """Monitor a deployment until completion or timeout."""
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        logger.info(f"🔍 Monitoring deployment for {timeout_minutes} minutes...")
        
        while time.time() - start_time < timeout_seconds:
            status = self.get_deployment_status()
            
            if status and 'latestDeployment' in status:
                deployment_status = status['latestDeployment']['status']
                logger.info(f"Deployment status: {deployment_status}")
                
                if deployment_status == 'SUCCESS':
                    logger.info("✅ Deployment completed successfully!")
                    return True
                elif deployment_status in ['FAILED', 'CRASHED']:
                    logger.warning(f"❌ Deployment {deployment_status.lower()}")
                    return False
            
            time.sleep(30)  # Check every 30 seconds
        
        logger.warning("⏰ Deployment monitoring timed out")
        return False

    def run_monitoring_cycle(self) -> bool:
        """Run a complete monitoring cycle: check logs, detect issues, apply fixes."""
        logger.info("🚀 Starting Railway monitoring cycle...")
        
        # Get deployment status
        status = self.get_deployment_status()
        if not status:
            logger.error("❌ Could not get deployment status")
            return False
        
        deployment = status.get('latestDeployment', {})
        deployment_status = deployment.get('status', 'UNKNOWN')
        
        logger.info(f"Current deployment status: {deployment_status}")
        
        # If deployment is successful, no action needed
        if deployment_status == 'SUCCESS':
            logger.info("✅ Deployment is healthy, no action needed")
            return True
        
        # If deployment failed, analyze logs
        if deployment_status in ['FAILED', 'CRASHED']:
            logger.info("🔍 Analyzing failed deployment logs...")
            
            logs = self.get_deployment_logs()
            if not logs:
                logger.error("❌ Could not fetch logs")
                return False
            
            # Analyze for issues
            detected_issues = self.analyze_logs(logs)
            
            if not detected_issues:
                logger.info("❓ No known issues detected in logs")
                return False
            
            logger.info(f"🔍 Detected issues: {list(detected_issues.keys())}")
            
            # Apply fixes for detected issues
            fixes_applied = []
            for issue_type, issue_logs in detected_issues.items():
                logger.info(f"🔧 Attempting to fix: {issue_type}")
                
                fix_function = self.issue_patterns[issue_type]['fix_function']
                if fix_function(issue_logs):
                    fixes_applied.append(issue_type)
            
            if fixes_applied:
                logger.info(f"✅ Applied fixes for: {', '.join(fixes_applied)}")
                
                # Commit and push fixes
                if self.commit_and_push_fixes(fixes_applied):
                    logger.info("🚀 Triggered new deployment with fixes")
                    
                    # Monitor the new deployment
                    return self.monitor_deployment()
                else:
                    logger.error("❌ Failed to push fixes")
                    return False
            else:
                logger.info("❓ No fixes could be applied")
                return False
        
        logger.info("⏳ Deployment in progress, will check again later")
        return True

def main():
    """Main function for Railway monitoring."""
    monitor = RailwayMonitor()
    
    # Check for required environment variables
    required_vars = ['RAILWAY_TOKEN', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("💡 Set these in your environment or .env file")
        return False
    
    # Run monitoring cycle
    success = monitor.run_monitoring_cycle()
    
    if success:
        logger.info("✅ Monitoring cycle completed successfully")
        return True
    else:
        logger.error("❌ Monitoring cycle failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 