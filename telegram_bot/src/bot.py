#!/usr/bin/env python3
"""
Main bot application with enhanced menu system integration.
"""

import asyncio
import logging
import sys

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Import handlers
from src.handlers import user_commands, admin_commands, message_handlers
from src import enhanced_admin_ui
from src.config import settings

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # Try to send error to admin if update is available
    if update and hasattr(update, 'effective_chat'):
        try:
            if update.effective_chat.id == settings.ADMIN_CHAT_ID:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ **Bot Error**\n\n`{str(context.error)[:500]}`",
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Failed to send error message to admin: {e}")


async def setup_webhook(application):
    """Set up webhook for production deployment."""
    try:
        webhook_url = f"https://{settings.RAILWAY_STATIC_URL}"
        logger.info(f"Setting webhook URL to: {webhook_url}")
        
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=settings.TELEGRAM_SECRET_TOKEN,
            drop_pending_updates=True
        )
        logger.info("✅ Webhook set successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")
        pass

async def main() -> None:
    """Initialize and run the bot in webhook mode."""
    logger.info("🚀 Starting Telegram Bot with Enhanced Menu System...")
    logger.info("Configuration loaded and validated successfully.")

    # Set up the application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Import and register enhanced interfaces
    try:
        from src.enhanced_user_interface import get_enhanced_user_handlers
        from src.enhanced_admin_interface import get_enhanced_admin_handlers
        
        # Register enhanced user interface (new beautiful menus)
        for handler in get_enhanced_user_handlers():
            application.add_handler(handler)
        
        # Register enhanced admin interface (new beautiful admin panel)
        application.add_handler(get_enhanced_admin_handlers())
        
        logger.info("✅ Enhanced menu interfaces loaded successfully")
        
    except ImportError as e:
        logger.warning(f"Enhanced interfaces not available, falling back to basic commands: {e}")
        
        # Fallback to basic user commands
        application.add_handler(CommandHandler("start", user_commands.start))
        application.add_handler(CommandHandler("balance", user_commands.balance_command))
        application.add_handler(CommandHandler("help", user_commands.help_command))
        application.add_handler(CommandHandler("buy", user_commands.buy_command))
        application.add_handler(CallbackQueryHandler(user_commands.button_handler))
    
    # Register additional commands
    application.add_handler(CommandHandler("buy_content", admin_commands.buy_content_command))
    application.add_handler(CallbackQueryHandler(admin_commands.handle_content_purchase, pattern=r"^purchase_"))
    
    # Register enhanced admin commands if available
    try:
        for handler in enhanced_admin_ui.get_enhanced_admin_commands():
            application.add_handler(handler)
        
        # Register enhanced user commands if available  
        for handler in enhanced_admin_ui.get_enhanced_user_commands():
            application.add_handler(handler)
    except (ImportError, AttributeError):
        logger.info("Enhanced admin UI not available, using basic admin commands")
    
    # Register conversation handlers
    try:
        application.add_handler(admin_commands.get_admin_conversation_handler())
        application.add_handler(admin_commands.get_locked_content_handler())
    except AttributeError:
        logger.warning("Some admin conversation handlers not available")
    
    # Register message handler (must be last)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handlers.master_message_handler))
    application.add_error_handler(error_handler)
    
    # The health check endpoint is now managed by the webserver library (e.g., uvicorn)
    # in combination with the webhook handling, not as a separate handler.
    # The presence of a webhook server that responds is the health check.

    # Start the bot
    webhook_url = f"https://{settings.RAILWAY_STATIC_URL}"
    logger.info(f"🌐 Bot starting in webhook mode, setting webhook to {webhook_url}")

    try:
        await application.run_webhook(
            listen="0.0.0.0",
            port=settings.WEBHOOK_PORT,
            secret_token=settings.TELEGRAM_SECRET_TOKEN,
            webhook_url=webhook_url
        )
    except Exception as e:
        logger.error(f"❌ Failed to start webhook server: {e}")
        raise

if __name__ == '__main__':
    # This script is not meant to be run directly anymore.
    logger.warning("⚠️ This script should be run via webhook server, not directly!")
    sys.exit(1) 