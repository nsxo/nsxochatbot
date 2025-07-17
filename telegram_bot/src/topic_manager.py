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
    """Send and pin a user info card in the topic with enhanced details."""
    try:
        # Get comprehensive user information
        user_credits = database.get_user_credits_optimized(user_id)
        user_info = database.get_user_info(user_id)
        
        # Get purchase history and tier information
        tier_emoji, tier_text = get_user_tier_info(user_credits)
        total_purchases = get_user_purchase_count(user_id)
        join_date = user_info.get('created_at', 'Unknown') if user_info else 'Unknown'
        
        # Create enhanced info card matching the documentation specs
        display_name = f"{first_name or 'Unknown'}"
        username_text = f"@{username}" if username else "No username"
        
        info_text = f"""👤 **User Profile Card**

**📱 User Details:**
• Name: {display_name}
• Username: {username_text}
• User ID: `{user_id}`

**💰 Account Status:**
• Credits: {user_credits}
• Tier: {tier_emoji} {tier_text}
• Total Purchases: {total_purchases}
• Status: {'🚫 Banned' if user_info and user_info.get('is_banned') else '✅ Active'}

**📅 Account Info:**
• Joined: {format_join_date(join_date)}
• Last Active: Recent

**💬 Admin Actions:**
Reply to any message in this topic to send to user
Use admin commands for credit management
        """.strip()
        
        # Send the enhanced info card
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
            logger.info(f"📌 Pinned enhanced info card for user {user_id} in topic {topic_id}")
        except TelegramError as e:
            logger.warning(f"Could not pin info card: {e}")
            
    except Exception as e:
        logger.error(f"Error sending enhanced user info card: {e}")

async def handle_user_message_to_topic(bot: Bot, update: Update, context: ContextTypes.DEFAULT_TYPE, cost: int, discount_text: str = "", user_tier: str = "") -> bool:
    """Enhanced user message handling with all media types support."""
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
        
        # Forward message to topic with enhanced header
        try:
            # Get user information for header
            user_credits = database.get_user_credits_optimized(user_id)
            tier_emoji, tier_text = get_user_tier_info(user_credits)
            
            # Determine message type for header
            message_type = get_message_type(update.message)
            
            # Enhanced header with message type, tier, and discount info
            header = f"""💬 **New {message_type} message**
From: @{update.effective_user.username or 'Unknown'} {tier_emoji} {tier_text} (ID: `{user_id}`)
Cost: {cost} credits{discount_text} | Balance: {user_credits} credits
──────────────────────────────────"""
            
            await bot.send_message(
                chat_id=settings.ADMIN_GROUP_ID,
                text=header,
                message_thread_id=topic_id,
                parse_mode='Markdown'
            )
            
            # Forward the actual message (supports all media types)
            await update.message.forward(
                chat_id=settings.ADMIN_GROUP_ID,
                message_thread_id=topic_id
            )
            
            # Update conversation activity
            database.update_conversation_activity(user_id, topic_id)
            
            logger.info(f"✅ Forwarded {message_type} from user {user_id} to topic {topic_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to forward to topic {topic_id}: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in handle_user_message_to_topic: {e}")
        return False

async def handle_admin_topic_reply(bot: Bot, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Enhanced admin topic reply handling with all message types support."""
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
        
        # Forward admin's message to the user (supports all message types)
        try:
            # Handle different message types
            if update.message.text:
                # Check for quick reply keywords
                message_text = update.message.text.strip()
                quick_reply = database.get_quick_reply(message_text)
                
                if quick_reply:
                    # Send quick reply instead of original message
                    await bot.send_message(chat_id=target_user_id, text=quick_reply)
                    # Add reaction to show it was a quick reply
                    await update.message.add_reaction("🔄")
                else:
                    # Send original text
                    await bot.send_message(chat_id=target_user_id, text=update.message.text)
                    await update.message.add_reaction("✅")
            elif update.message.photo:
                await bot.send_photo(
                    chat_id=target_user_id,
                    photo=update.message.photo[-1].file_id,
                    caption=update.message.caption
                )
            elif update.message.video:
                await bot.send_video(
                    chat_id=target_user_id,
                    video=update.message.video.file_id,
                    caption=update.message.caption
                )
            elif update.message.document:
                await bot.send_document(
                    chat_id=target_user_id,
                    document=update.message.document.file_id,
                    caption=update.message.caption
                )
            elif update.message.voice:
                await bot.send_voice(
                    chat_id=target_user_id,
                    voice=update.message.voice.file_id
                )
            elif update.message.sticker:
                await bot.send_sticker(
                    chat_id=target_user_id,
                    sticker=update.message.sticker.file_id
                )
            else:
                # Fallback: copy the message
                await update.message.copy(chat_id=target_user_id)
            
            # Add checkmark reaction to confirm (enhanced UX)
            try:
                await update.message.add_reaction("✅")
            except:
                # Fallback: reply with checkmark if reactions not available
                await bot.send_message(
                    chat_id=settings.ADMIN_GROUP_ID,
                    text="✅ Message sent to user",
                    message_thread_id=topic_id,
                    reply_to_message_id=update.message.message_id
                )
                
            # Update conversation activity
            database.update_conversation_activity(target_user_id, topic_id)
            
            logger.info(f"✅ Forwarded admin reply from topic {topic_id} to user {target_user_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to forward admin reply to user {target_user_id}: {e}")
            await bot.send_message(
                chat_id=settings.ADMIN_GROUP_ID,
                text=f"❌ Failed to send message to user. Error: {str(e)[:100]}...",
                message_thread_id=topic_id,
                reply_to_message_id=update.message.message_id
            )
            return True  # Still handled, just failed
            
    except Exception as e:
        logger.error(f"Error in handle_admin_topic_reply: {e}")
        return False

# ========================= Helper Functions =========================

def get_user_tier_info(credits: int) -> tuple[str, str]:
    """Get user tier emoji and text based on credits."""
    if credits >= 100:
        return "🏆", "VIP"
    elif credits >= 50:
        return "⭐", "Regular"
    else:
        return "🆕", "New"

def get_user_purchase_count(user_id: int) -> int:
    """Get total purchase count for user."""
    # This would query payment_logs table
    try:
        return database.get_user_purchase_count(user_id)
    except:
        return 0

def get_message_type(message) -> str:
    """Determine message type for display."""
    if message.photo:
        return "photo"
    elif message.video:
        return "video"
    elif message.voice:
        return "voice"
    elif message.document:
        return "document"
    elif message.sticker:
        return "sticker"
    elif message.text:
        return "text"
    else:
        return "media"

def format_join_date(date_str) -> str:
    """Format join date for display."""
    try:
        # Add proper date formatting here
        return str(date_str)[:10] if date_str else "Unknown"
    except:
        return "Unknown"

def is_topic_enabled() -> bool:
    """Check if topic management is enabled and configured."""
    return bool(settings.ADMIN_GROUP_ID) 