#!/usr/bin/env python3
"""
Railway Project Configuration Script
Ensures deployments target the correct Railway project ID.
"""

import os
import json
import subprocess
from pathlib import Path

# Target Railway project details
TARGET_PROJECT_ID = "1a667d5e-72d0-4930-ac5a-197fdc7506b3"
TARGET_PROJECT_NAME = "nsxomsgbot"
TARGET_ENVIRONMENT = "production"

def ensure_railway_cli():
    """Check if Railway CLI is installed."""
    try:
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Railway CLI installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI not found")
        print("📦 Install with: npm install -g @railway/cli")
        return False

def check_railway_login():
    """Check if user is logged into Railway."""
    try:
        result = subprocess.run(['railway', 'whoami'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Logged into Railway as: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Not logged into Railway")
        print("🔐 Run: railway login")
        return False

def link_to_project():
    """Link the repository to the specific Railway project."""
    print(f"\n🔗 Linking to Railway project: {TARGET_PROJECT_ID}")
    
    try:
        # Link to specific project
        result = subprocess.run([
            'railway', 'link', TARGET_PROJECT_ID
        ], capture_output=True, text=True, check=True)
        
        print(f"✅ Successfully linked to project: {TARGET_PROJECT_NAME}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to link to project: {e}")
        print(f"stderr: {e.stderr}")
        return False

def verify_project_link():
    """Verify we're linked to the correct project."""
    try:
        result = subprocess.run(['railway', 'status'], 
                              capture_output=True, text=True, check=True)
        
        if TARGET_PROJECT_ID in result.stdout or TARGET_PROJECT_NAME in result.stdout:
            print(f"✅ Confirmed linked to correct project: {TARGET_PROJECT_NAME}")
            return True
        else:
            print("⚠️ May not be linked to correct project")
            print(result.stdout)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Could not verify project link: {e}")
        return False

def create_project_config():
    """Create Railway project configuration file."""
    railway_dir = Path(".railway")
    railway_dir.mkdir(exist_ok=True)
    
    project_config = railway_dir / "project.json"
    
    config = {
        "projectId": TARGET_PROJECT_ID,
        "environmentId": TARGET_ENVIRONMENT
    }
    
    with open(project_config, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created Railway project config: {project_config}")
    return True

def deploy_to_railway():
    """Deploy the project to Railway."""
    print(f"\n🚀 Deploying to Railway project: {TARGET_PROJECT_NAME}")
    
    try:
        # Deploy using Railway CLI
        result = subprocess.run([
            'railway', 'up', '--detach'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Deployment initiated successfully")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """Main execution function."""
    print("🚀 Railway Project Configuration Script")
    print("=" * 50)
    print(f"🎯 Target Project: {TARGET_PROJECT_NAME}")
    print(f"🆔 Project ID: {TARGET_PROJECT_ID}")
    print(f"🌍 Environment: {TARGET_ENVIRONMENT}")
    
    # Check Railway CLI
    if not ensure_railway_cli():
        return False
    
    # Check login status
    if not check_railway_login():
        print("\n🔐 Please log in to Railway first:")
        print("   railway login")
        return False
    
    # Create local project configuration
    create_project_config()
    
    # Link to the specific project
    if not link_to_project():
        return False
    
    # Verify the link
    if not verify_project_link():
        print("⚠️ Project link verification failed, but continuing...")
    
    # Ask if user wants to deploy now
    deploy_choice = input(f"\n🚀 Deploy to {TARGET_PROJECT_NAME} now? (y/n): ")
    if deploy_choice.lower() == 'y':
        return deploy_to_railway()
    
    print("\n✅ Project configuration completed!")
    print(f"🔗 Repository is now linked to Railway project: {TARGET_PROJECT_NAME}")
    print("🚀 To deploy later, run: railway up")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Railway project configuration successful!")
    else:
        print("\n❌ Configuration failed - check Railway CLI setup")
        exit(1) 