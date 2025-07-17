#!/usr/bin/env python3
"""
Topic management system for supergroup conversation threads.
Handles automatic topic creation, user info cards, and admin replies.
"""

import logging
from typing import Optional, Dict, Any
from telegram import Update, Bot, ForumTopic
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from src import database
from src.config import settings

logger = logging.getLogger(__name__)


async def get_or_create_user_topic(bot: Bot, user_id: int, username: str = None, first_name: str = None) -> Optional[int]:
    """Get existing topic for user or create a new one in the admin group."""
    try:
        # Check if admin group is configured
        if not settings.ADMIN_GROUP_ID:
            logger.warning("Admin group ID not configured, falling back to private chat")
            return None
        
        # Check if user already has a topic
        existing_topic_id = database.get_or_create_user_topic(user_id, username, first_name)
        if existing_topic_id:
            return existing_topic_id
        
        # Create new topic in the supergroup
        display_name = f"{first_name or 'User'}"
        if username:
            display_name = f"@{username}"
        
        topic_name = f"👤 {display_name} ({user_id})"
        
        try:
            # Create forum topic
            forum_topic = await bot.create_forum_topic(
                chat_id=settings.ADMIN_GROUP_ID,
                name=topic_name[:100]  # Telegram limit is 100 chars
            )
            
            topic_id = forum_topic.message_thread_id
            
            # Save topic to database
            if database.save_user_topic(user_id, topic_id):
                logger.info(f"✅ Created topic {topic_id} for user {user_id} ({display_name})")
                
                # Send user info card to the topic
                await send_user_info_card(bot, user_id, topic_id, username, first_name)
                
                return topic_id
            else:
                logger.error(f"Failed to save topic {topic_id} for user {user_id}")
                return None
                
        except TelegramError as e:
            if "not found" in str(e).lower() or "chat not found" in str(e).lower():
                logger.error(f"Admin group {settings.ADMIN_GROUP_ID} not found or bot not in group")
            elif "forum" in str(e).lower():
                logger.error(f"Admin group {settings.ADMIN_GROUP_ID} is not a forum group")
            else:
                logger.error(f"Failed to create forum topic: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error in get_or_create_user_topic: {e}")
        return None


async def send_user_info_card(bot: Bot, user_id: int, topic_id: int, username: str = None, first_name: str = None) -> None:
    """Send and pin a user info card in the topic."""
    try:
        # Get user information
        user_credits = database.get_user_credits_optimized(user_id)
        user_info = database.get_user_info(user_id)
        
        # Create info card
        display_name = f"{first_name or 'Unknown'}"
        username_text = f"@{username}" if username else "No username"
        
        info_text = f"""
👤 **User Profile**

**Name:** {display_name}
**Username:** {username_text}
**User ID:** `{user_id}`
**Credits:** {user_credits}
**Status:** {'🚫 Banned' if user_info and user_info.get('is_banned') else '✅ Active'}
**Joined:** {user_info.get('created_at', 'Unknown') if user_info else 'Unknown'}

💬 **Quick Actions:**
Reply to any message in this topic to send to user
        """.strip()
        
        # Send the info card
        message = await bot.send_message(
            chat_id=settings.ADMIN_GROUP_ID,
            text=info_text,
            message_thread_id=topic_id,
            parse_mode='Markdown'
        )
        
        # Pin the info card
        try:
            await bot.pin_chat_message(
                chat_id=settings.ADMIN_GROUP_ID,
                message_id=message.message_id
            )
            logger.info(f"📌 Pinned info card for user {user_id} in topic {topic_id}")
        except TelegramError as e:
            logger.warning(f"Could not pin info card: {e}")
            
    except Exception as e:
        logger.error(f"Error sending user info card: {e}")


async def handle_user_message_to_topic(bot: Bot, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle forwarding user message to their topic. Returns True if handled via topic."""
    try:
        user_id = update.effective_user.id
        
        # Skip if no admin group configured
        if not settings.ADMIN_GROUP_ID:
            return False
        
        # Get or create topic for user
        topic_id = await get_or_create_user_topic(
            bot,
            user_id,
            update.effective_user.username,
            update.effective_user.first_name
        )
        
        if not topic_id:
            logger.warning(f"Could not get/create topic for user {user_id}, falling back to private forwarding")
            return False
        
        # Forward message to topic
        try:
            # Send header with user info
            user_credits = database.get_user_credits_optimized(user_id)
            header = f"💬 New message (Balance: {user_credits} credits)"
            
            await bot.send_message(
                chat_id=settings.ADMIN_GROUP_ID,
                text=header,
                message_thread_id=topic_id
            )
            
            # Forward the actual message
            await update.message.forward(
                chat_id=settings.ADMIN_GROUP_ID,
                message_thread_id=topic_id
            )
            
            # Update conversation activity
            database.update_conversation_activity(user_id, topic_id)
            
            logger.info(f"✅ Forwarded message from user {user_id} to topic {topic_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to forward to topic {topic_id}: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in handle_user_message_to_topic: {e}")
        return False


async def handle_admin_topic_reply(bot: Bot, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handle admin replies in topics. Returns True if handled as topic reply."""
    try:
        # Check if this is in the admin group and has a message thread ID
        if (update.effective_chat.id != settings.ADMIN_GROUP_ID or 
            not hasattr(update.message, 'message_thread_id') or 
            not update.message.message_thread_id):
            return False
        
        # Check if this is an admin user
        if update.effective_user.id != settings.ADMIN_CHAT_ID:
            return False
        
        topic_id = update.message.message_thread_id
        
        # Get user ID for this topic
        target_user_id = database.get_user_by_topic_id(topic_id)
        if not target_user_id:
            logger.warning(f"No user found for topic {topic_id}")
            return False
        
        # Forward admin's message to the user
        try:
            await update.message.copy(chat_id=target_user_id)
            
            # Add checkmark reaction to confirm
            try:
                await update.message.add_reaction("✅")
            except:
                pass  # Reactions might not be available
                
            # Update conversation activity
            database.update_conversation_activity(target_user_id, topic_id)
            
            logger.info(f"✅ Forwarded admin reply from topic {topic_id} to user {target_user_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to forward admin reply to user {target_user_id}: {e}")
            await update.message.reply_text(f"❌ Failed to send message to user. Error: {e}")
            return True  # Still handled, just failed
            
    except Exception as e:
        logger.error(f"Error in handle_admin_topic_reply: {e}")
        return False


def is_topic_enabled() -> bool:
    """Check if topic management is enabled and configured."""
    return bool(settings.ADMIN_GROUP_ID) 