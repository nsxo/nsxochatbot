#!/usr/bin/env python3
"""
Railway Deployment Script
This script is the single entry point for the Railway deployment.
It performs pre-flight checks and runs the main bot application.
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = str(project_root / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import the health check
from src.database import check_database_health

# Configure basic logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Performs startup checks and launches the bot application."""
    logger.info("🔬 Performing pre-flight health checks...")

    # 1. Database Health Check
    db_health = check_database_health()
    if db_health.get('status') != 'healthy':
        logger.critical(f"❌ Database health check failed: {db_health.get('error')}")
        sys.exit(1)
    logger.info("✅ Database health check successful.")

    logger.info("🚀 Launching bot application...")
    
    # Import and run the bot using the synchronous approach
    from telegram.ext import Application
    from src.config import settings
    from src.error_handler import error_handler
    from src.handlers import user_commands, admin_commands, message_handlers
    from telegram import Update
    from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
    
    # Set up the application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Register all handlers
    application.add_handler(CommandHandler("start", user_commands.start))
    application.add_handler(CommandHandler("balance", user_commands.balance_command))
    application.add_handler(CommandHandler("help", user_commands.help_command))
    application.add_handler(CommandHandler("buy", user_commands.buy_command))
    application.add_handler(CallbackQueryHandler(user_commands.button_handler))
    application.add_handler(admin_commands.get_admin_conversation_handler())
    application.add_handler(admin_commands.get_locked_content_handler())
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handlers.master_message_handler))
    application.add_error_handler(error_handler)

    # Start the bot using the synchronous webhook method
    webhook_url = f"https://{settings.RAILWAY_STATIC_URL}"
    logger.info(f"Bot starting in webhook mode, setting webhook to {webhook_url}")

    # Use the synchronous run_webhook method
    application.run_webhook(
        listen="0.0.0.0",
        port=settings.WEBHOOK_PORT,
        secret_token=settings.TELEGRAM_SECRET_TOKEN,
        webhook_url=webhook_url
    )


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(f"❌ Bot application failed to launch: {e}", exc_info=True)
        # Exit with a non-zero code to signal failure to Railway
        sys.exit(1)