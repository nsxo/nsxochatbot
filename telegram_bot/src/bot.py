#!/usr/bin/env python3
"""
Main entry point for the Telegram Bot application.
Initializes the bot, sets up handlers, and starts polling.
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
)

from src.config import settings
from src.error_handler import error_handler
from src.handlers import user_commands, admin_commands, message_handlers

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", # Simplified format
    level=settings.LOG_LEVEL.upper()
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Initialize and run the bot."""
    # Pydantic validates on initialization, so no need for a separate validate() call
    logger.info("Configuration loaded and validated successfully.")

    # Create the Application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # ========================= HANDLER REGISTRATION =========================

    # User-facing commands
    application.add_handler(CommandHandler("start", user_commands.start))
    application.add_handler(CommandHandler("balance", user_commands.balance_command))
    application.add_handler(CommandHandler("help", user_commands.help_command))
    application.add_handler(CommandHandler("buy", user_commands.buy_command))
    application.add_handler(CallbackQueryHandler(user_commands.button_handler))

    # Admin commands
    application.add_handler(admin_commands.get_admin_conversation_handler())
    application.add_handler(admin_commands.get_locked_content_handler())

    # Master message handler
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        message_handlers.master_message_handler
    ))

    # Error handler
    application.add_error_handler(error_handler)

    # ========================= BOT STARTUP =========================

    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main() 