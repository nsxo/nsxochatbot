#!/usr/bin/env python3
"""
Set up Telegram webhook for Railway deployment.
This script configures the bot to receive updates via webhook instead of polling.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAILWAY_URL = "https://nsxomsgbot-production.up.railway.app"
WEBHOOK_URL = f"{RAILWAY_URL}/telegram-webhook"

def setup_webhook():
    """Set up the Telegram webhook."""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in environment variables")
        return False

    print("🔄 Setting up Telegram webhook...")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")

    # Set webhook
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {
        'url': WEBHOOK_URL,
        'allowed_updates': ['message', 'callback_query', 'inline_query']
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            print("✅ Webhook set successfully!")
            print(f"📊 Response: {result['description']}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result['description']}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return False

def check_webhook():
    """Check current webhook status."""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return

    print("\n🔍 Checking current webhook status...")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(url)

    if response.status_code == 200:
        result = response.json()['result']
        print(f"🌐 Current URL: {result.get('url', 'None (polling mode)')}")
        print(f"📊 Pending Updates: {result.get('pending_update_count', 0)}")
        print(f"📅 Last Error Date: {result.get('last_error_date', 'None')}")
        print(f"❌ Last Error: {result.get('last_error_message', 'None')}")
    else:
        print(f"❌ Failed to get webhook info: {response.status_code}")

def delete_webhook():
    """Delete the current webhook (switch back to polling)."""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return False

    print("🗑️ Deleting webhook (switching to polling mode)...")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.post(url)

    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            print("✅ Webhook deleted successfully!")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result['description']}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return False

def main():
    """Main function."""
    print("🤖 Telegram Bot Webhook Setup")
    print("=" * 40)

    # Check current status
    check_webhook()

    print("\nWhat would you like to do?")
    print("1. Set up webhook for Railway deployment")
    print("2. Delete webhook (switch to polling)")
    print("3. Just check status (no changes)")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        if setup_webhook():
            print("\n🎉 Webhook setup complete!")
            print("\n📋 Next steps:")
            print("1. Make sure your Railway bot deployment is running")
            print("2. Test by sending a message to @nsxochatbot")
            print("3. Check Railway logs for incoming webhook requests")
        else:
            print("\n❌ Webhook setup failed!")

    elif choice == "2":
        if delete_webhook():
            print("\n✅ Switched back to polling mode")
            print("📋 The bot will now work in development/local mode")
        else:
            print("\n❌ Failed to delete webhook")

    elif choice == "3":
        print("\n📊 Status check complete!")

    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()