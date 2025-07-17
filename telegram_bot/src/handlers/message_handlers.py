#!/usr/bin/env python3
"""
Master message handler for the Telegram bot with topic management support.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from src import database
from src.config import settings
from src.error_handler import rate_limit, monitor_performance
from src.handlers.user_commands import safe_reply, format_time_remaining # Re-use helpers
from src import topic_manager

logger = logging.getLogger(__name__)

@rate_limit(max_calls=100, window_seconds=60)
@monitor_performance
async def master_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Master handler for all messages, routing them between users, admin, and topics."""
    message = update.message
    user_id = update.effective_user.id
    admin_chat_id = settings.ADMIN_CHAT_ID

    # --- Topic Reply Handling (Priority 1) ---
    # Check if this is an admin reply in a topic
    if await topic_manager.handle_admin_topic_reply(context.bot, update, context):
        return  # Handled as topic reply

    # --- Admin Private Chat Reply Logic (Priority 2) ---
    # Handle replies in admin's private chat (fallback system)
    if user_id == admin_chat_id and message.reply_to_message:
        original_message_id = message.reply_to_message.message_id
        target_user_id = context.bot_data.get('message_map', {}).get(str(original_message_id))

        if target_user_id:
            try:
                # Forward the admin's reply to the user
                await context.bot.copy_message(chat_id=target_user_id, from_chat_id=admin_chat_id, message_id=message.message_id)
                await message.add_reaction("✅")
                logger.info(f"✅ Forwarded admin private reply to user {target_user_id}")
            except Exception as e:
                logger.error(f"Failed to send reply to user {target_user_id}: {e}")
                await message.reply_text("❌ Failed to send message. The user may have blocked the bot.")
        else:
            await message.reply_text("⚠️ Could not find the original user for this reply.")
        return

    # --- Regular User Message Logic (Priority 3) ---
    if user_id != admin_chat_id:
        # Check if user is banned
        if database.is_user_banned(user_id):
            await safe_reply(update, "🚫 You are banned from using this bot and cannot send messages.")
            return
        
        # Simplified cost logic, can be expanded with database.get_setting
        cost = 1 
        
        # Decrement credits
        new_balance = database.decrement_user_credits_optimized(user_id, cost)
        
        if new_balance == -1:
            current_balance = database.get_user_credits_optimized(user_id)
            await safe_reply(update, f"❌ Insufficient credits. You need {cost} credits but only have {current_balance}. Please /buy more.")
            return
        
        # Try topic forwarding first (preferred method)
        topic_handled = await topic_manager.handle_user_message_to_topic(context.bot, update, context)
        
        if not topic_handled:
            # Fallback to private chat forwarding
            try:
                header = f"📩 New message from: @{update.effective_user.username} (ID: {user_id})\nBalance: {new_balance} credits"
                await context.bot.send_message(chat_id=admin_chat_id, text=header)
                forwarded_message = await message.forward(chat_id=admin_chat_id)
                
                # Map forwarded message ID to user ID for replies
                if 'message_map' not in context.bot_data:
                    context.bot_data['message_map'] = {}
                context.bot_data['message_map'][str(forwarded_message.message_id)] = user_id
                
                logger.info(f"✅ Forwarded message from user {user_id} to admin private chat (fallback)")
                
            except Exception as e:
                logger.error(f"Failed to forward message from {user_id} to admin: {e}")
                # Refund credits on failure
                database.add_user_credits(user_id, cost) 
                await safe_reply(update, "⚠️ Sorry, there was an error sending your message. Your credits have been refunded.")

    # --- Admin Group Messages (non-topic) ---
    # Skip processing other admin group messages that aren't topic replies
    if user_id == admin_chat_id and update.effective_chat.id == settings.ADMIN_GROUP_ID:
        # This is an admin message in the group but not in a topic thread
        logger.debug(f"Skipping admin group message (not in topic): {message.message_id}") 