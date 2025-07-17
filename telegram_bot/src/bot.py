#!/usr/bin/env python3
"""
Main entry point for the Telegram Bot application.
Initializes the bot, sets up handlers, and starts the webhook server.
"""

import logging
import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    BaseHandler
)
from telegram.request import HTTPXRequest

from src.config import settings
from src.error_handler import error_handler
from src.handlers import user_commands, admin_commands, message_handlers
from src import enhanced_admin_ui

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=settings.LOG_LEVEL.upper()
)
logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHandler):
    """A custom handler for the /health endpoint."""
    def __init__(self):
        super().__init__(self.handle_health_check)

    def check_update(self, update):
        return isinstance(update, str) and update == '/health'

    async def handle_update(self, update, application, check_result, context):
        # This is a dummy method to satisfy the abstract class
        pass

    async def handle_health_check(self, update, context):
        # This method is not directly used by PTB but can be called manually
        # In PTB v20+, web apps handle this outside the handler system
        pass

async def main() -> None:
    """Initialize and run the bot in webhook mode."""
    logger.info("Configuration loaded and validated successfully.")

    # Set up the application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Register basic user commands
    application.add_handler(CommandHandler("start", user_commands.start))
    application.add_handler(CommandHandler("balance", user_commands.balance_command))
    application.add_handler(CommandHandler("help", user_commands.help_command))
    application.add_handler(CommandHandler("buy", user_commands.buy_command))
    application.add_handler(CommandHandler("buy_content", admin_commands.buy_content_command))
    application.add_handler(CallbackQueryHandler(user_commands.button_handler))
    application.add_handler(CallbackQueryHandler(admin_commands.handle_content_purchase, pattern=r"^purchase_"))
    
    # Register enhanced admin commands
    for handler in enhanced_admin_ui.get_enhanced_admin_commands():
        application.add_handler(handler)
    
    # Register enhanced user commands
    for handler in enhanced_admin_ui.get_enhanced_user_commands():
        application.add_handler(handler)
    
    # Register conversation handlers
    application.add_handler(admin_commands.get_admin_conversation_handler())
    application.add_handler(admin_commands.get_locked_content_handler())
    
    # Register message handler
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handlers.master_message_handler))
    application.add_error_handler(error_handler)
    
    # The health check endpoint is now managed by the webserver library (e.g., uvicorn)
    # in combination with the webhook handling, not as a separate handler.
    # The presence of a webhook server that responds is the health check.

    # Start the bot
    webhook_url = f"https://{settings.RAILWAY_STATIC_URL}"
    logger.info(f"Bot starting in webhook mode, setting webhook to {webhook_url}")

    await application.run_webhook(
        listen="0.0.0.0",
        port=settings.WEBHOOK_PORT,
        secret_token=settings.TELEGRAM_SECRET_TOKEN, # It's good practice to have a secret token
        webhook_url=webhook_url
    )

if __name__ == '__main__':
    # This script is not meant to be run directly anymore.
    # The deployment script will run the main() coroutine.
    pass 