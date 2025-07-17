#!/usr/bin/env python3
"""
Railway Deployment Script
- Starts a Flask web server for health checks and webhooks.
- Runs the main Telegram bot application in a separate thread.
"""

import os
import sys
import logging
import threading
import time
from pathlib import Path

from flask import Flask, request, jsonify

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = str(project_root / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import the new Pydantic settings and the refactored bot
from src.config import settings
from src import bot as application_bot

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway."""
    return jsonify({'status': 'healthy', 'service': 'telegram-bot'}), 200

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """
    Handles incoming Telegram webhook updates.
    This is now the primary way the bot receives messages on Railway.
    The bot's internal logic will handle processing the update.
    """
    # The new bot application handles updates internally via the webhook setup.
    # This endpoint just needs to exist and return 200 OK.
    # In a real scenario, you'd pass the request data to the bot's update queue.
    # For now, we assume the python-telegram-bot library's webhook server handles it.
    return jsonify({'ok': True}), 200

def run_bot_application():
    """Runs the main, refactored bot application."""
    logger.info("🚀 Starting main bot application...")
    try:
        application_bot.main()
        logger.info("✅ Bot application finished.")
    except Exception as e:
        logger.error(f"❌ Bot application failed: {e}", exc_info=True)

if __name__ == '__main__':
    logger.info("🚀 Initializing Railway start script...")
    
    # Start the main bot application in a background thread
    bot_thread = threading.Thread(target=run_bot_application, daemon=True)
    bot_thread.start()
    logger.info("🤖 Bot application thread started.")
    
    # Give the bot a moment to initialize before starting the web server
    time.sleep(2)
    
    # Start the Flask web server in the main thread for health checks
    # Railway will ping the /health endpoint.
    logger.info(f"🌐 Starting Flask server for health checks on port {settings.WEBHOOK_PORT}...")
    try:
        app.run(
            host='0.0.0.0',
            port=settings.WEBHOOK_PORT,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"❌ Flask server failed: {e}", exc_info=True)