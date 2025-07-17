#!/usr/bin/env python3
"""
Admin-facing command handlers for the Telegram bot, including conversation handlers for settings.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from src import database
from src.config import settings
from src.error_handler import monitor_performance

logger = logging.getLogger(__name__)

# Conversation states for the main admin menu
ADMIN_MENU, SETTINGS_MENU, USER_MANAGEMENT = range(3)
# Conversation states for settings submenu
EDIT_WELCOME, EDIT_COSTS = range(3, 5)

# ========================= Helper Functions =========================

def is_admin(update: Update) -> bool:
    """Check if the user is the bot admin."""
    return update.effective_user.id == settings.ADMIN_CHAT_ID

async def safe_reply(update: Update, text: str, **kwargs):
    """Safely reply or edit a message."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, **kwargs)
    else:
        await update.message.reply_text(text, **kwargs)

# ========================= Main Admin Command =========================

@monitor_performance
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the admin conversation handler."""
    if not is_admin(update):
        await safe_reply(update, "⛔ You are not authorized.")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton("📊 Dashboard", callback_data='dashboard')],
        [InlineKeyboardButton("⚙️ Bot Settings", callback_data='settings')],
        [InlineKeyboardButton("👥 User Management", callback_data='users')],
        [InlineKeyboardButton("❌ Exit", callback_data='exit')]
    ]
    await safe_reply(update, "👨‍💼 *Admin Panel*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return ADMIN_MENU

# ========================= Top-Level Menu Handlers =========================

async def dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the admin dashboard."""
    stats = database.get_user_stats()
    stats_text = f"📊 *Dashboard*\n\n- Total Users: {stats.get('total_users', 0)}\n- Banned Users: {stats.get('banned_users', 0)}"
    await safe_reply(update, stats_text, parse_mode='Markdown')
    return ADMIN_MENU

async def settings_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the settings menu."""
    keyboard = [
        [InlineKeyboardButton("📝 Edit Welcome Message", callback_data='edit_welcome')],
        [InlineKeyboardButton("💰 Edit Message Costs", callback_data='edit_costs')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_admin_menu')]
    ]
    await safe_reply(update, "⚙️ *Bot Settings*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return SETTINGS_MENU

async def user_management_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Placeholder for user management."""
    await safe_reply(update, "👥 User management coming soon.", parse_mode='Markdown')
    return ADMIN_MENU

# ========================= Settings Sub-Menu Handlers =========================

async def ask_for_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the admin for the new welcome message."""
    await safe_reply(update, "Please send the new welcome message.")
    return EDIT_WELCOME

async def set_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set the new welcome message in the database."""
    database.set_setting('welcome_message', update.message.text)
    await safe_reply(update, "✅ Welcome message updated successfully!")
    await settings_menu_handler(update, context) # Show settings menu again
    return SETTINGS_MENU

async def ask_for_costs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the admin for new message costs."""
    await safe_reply(update, "Please send the new cost for a text message (e.g., '1').")
    return EDIT_COSTS

async def set_costs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set the new message costs in the database."""
    try:
        cost = int(update.message.text)
        database.set_setting('cost_text_message', str(cost))
        await safe_reply(update, f"✅ Text message cost updated to {cost} credits.")
    except ValueError:
        await safe_reply(update, "❌ Invalid number. Please send a valid integer.")
    
    await settings_menu_handler(update, context) # Show settings menu again
    return SETTINGS_MENU

# ========================= Back and Exit Handlers =========================

async def back_to_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to the main admin menu."""
    return await admin_command(update, context)

async def exit_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exit the admin conversation."""
    await safe_reply(update, "Exiting admin panel.")
    return ConversationHandler.END

# ========================= Conversation Handler Setup =========================

def get_admin_conversation_handler() -> ConversationHandler:
    """Create the main admin conversation handler with nested settings handler."""
    
    settings_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(settings_menu_handler, pattern='^settings$')],
        states={
            SETTINGS_MENU: [
                CallbackQueryHandler(ask_for_welcome_message, pattern='^edit_welcome$'),
                CallbackQueryHandler(ask_for_costs, pattern='^edit_costs$'),
                CallbackQueryHandler(back_to_admin_menu, pattern='^back_to_admin_menu$'),
            ],
            EDIT_WELCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_welcome_message)],
            EDIT_COSTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_costs)],
        },
        fallbacks=[CallbackQueryHandler(exit_conversation, pattern='^exit$')],
        map_to_parent={
            # After settings are handled, return to the main admin menu
            ADMIN_MENU: ADMIN_MENU,
            # If settings conversation is exited, exit the main conversation too
            ConversationHandler.END: ConversationHandler.END
        }
    )
    
    main_admin_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_command)],
        states={
            ADMIN_MENU: [
                CallbackQueryHandler(dashboard_handler, pattern='^dashboard$'),
                CallbackQueryHandler(user_management_handler, pattern='^users$'),
                settings_handler, # Nest the settings handler
            ],
        },
        fallbacks=[CallbackQueryHandler(exit_conversation, pattern='^exit$')],
    )
    
    return main_admin_handler 