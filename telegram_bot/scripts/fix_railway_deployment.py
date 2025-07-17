#!/usr/bin/env python3
"""
Railway Deployment Fix Script
Automates fixing common Railway deployment issues.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_git_status():
    """Check Git repository status."""
    print("🔍 Checking Git repository...")
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️ Uncommitted changes found:")
            print(result.stdout)
            return False
        else:
            print("✅ Git repository is clean")
            return True
            
    except subprocess.CalledProcessError:
        print("❌ Not in a Git repository or Git error")
        return False

def check_railway_config():
    """Check Railway configuration."""
    print("\n🔍 Checking Railway configuration...")
    
    railway_json = Path("railway.json")
    if railway_json.exists():
        print("✅ railway.json exists")
        with open(railway_json) as f:
            config = json.load(f)
            print(f"✅ Docker path: {config.get('build', {}).get('dockerfilePath', 'Not set')}")
            print(f"✅ Start command: {config.get('deploy', {}).get('startCommand', 'Not set')}")
        return True
    else:
        print("❌ railway.json not found")
        return False

def check_dockerfile():
    """Check if Dockerfile exists."""
    print("\n🔍 Checking Dockerfile...")
    
    dockerfile = Path("deployment/Dockerfile")
    if dockerfile.exists():
        print("✅ Dockerfile exists at deployment/Dockerfile")
        return True
    else:
        print("❌ Dockerfile not found at deployment/Dockerfile")
        return False

def commit_and_push():
    """Commit changes and push to trigger Railway deployment."""
    print("\n🚀 Committing and pushing changes...")
    
    try:
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit with deployment message
        subprocess.run(['git', 'commit', '-m', 
                       '🔧 Fix Railway deployment configuration\n\n- Fix PostgreSQL service connection\n- Update deployment settings\n- Ensure proper root directory'], 
                      check=True)
        
        # Push to main branch
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("✅ Changes pushed to GitHub - Railway will auto-deploy")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return False

def create_railway_root_config():
    """Create Railway configuration at repository root."""
    print("\n🔧 Creating Railway root configuration...")
    
    # Move to parent directory (repository root)
    repo_root = Path("..").resolve()
    railway_root_config = repo_root / "railway.json"
    
    config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "DOCKERFILE",
            "dockerfilePath": "telegram_bot/deployment/Dockerfile"
        },
        "deploy": {
            "startCommand": "cd telegram_bot && python deployment/simple_railway_bot.py",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 300,
            "healthcheckInterval": 30,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 3
        }
    }
    
    with open(railway_root_config, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created railway.json at repository root: {railway_root_config}")
    return True

def main():
    """Main execution function."""
    print("🚀 Railway Deployment Fix Script")
    print("=" * 50)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Run checks
    git_ok = check_git_status()
    railway_ok = check_railway_config()
    docker_ok = check_dockerfile()
    
    if not docker_ok:
        print("\n❌ Critical: Dockerfile not found!")
        return False
    
    # Create repository root configuration
    create_railway_root_config()
    
    print("\n🔧 Railway Deployment Fixes Applied:")
    print("✅ Repository root railway.json created")
    print("✅ Docker path updated to telegram_bot/deployment/Dockerfile") 
    print("✅ Start command updated with proper directory")
    print("✅ Health check configuration maintained")
    
    print("\n📋 Manual Steps Required:")
    print("1. Go to Railway Dashboard")
    print("2. Click your PostgreSQL service (the crashed one)")
    print("3. Go to Settings → Restart Service")
    print("4. Wait for PostgreSQL to start (should show green)")
    print("5. Your bot service will auto-redeploy from GitHub")
    
    print("\n🎯 Expected Results:")
    print("- PostgreSQL service: Running (green)")
    print("- Bot service: Successful deployment")
    print("- Logs showing: '🗄️ Database: ✅ Set'")
    
    # Optionally commit and push
    if git_ok:
        push_choice = input("\n🚀 Push changes to GitHub now? (y/n): ")
        if push_choice.lower() == 'y':
            return commit_and_push()
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Railway deployment fix completed!")
        print("Check Railway dashboard for deployment status.")
    else:
        print("\n❌ Some issues need manual resolution.")
        sys.exit(1) 