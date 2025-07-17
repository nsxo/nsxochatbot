#!/usr/bin/env python3
"""
Enhanced admin UI components matching the professional preview design.
Provides visual enhancements and additional admin functionality.
"""

import logging
from typing import Dict, Any, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler

from src import database
from src.config import settings
from src.handlers.admin_commands import is_admin, safe_reply

logger = logging.getLogger(__name__)

# ========================= Direct Command Handlers =========================

async def conversations_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Direct access to conversations menu - /conversations"""
    if not is_admin(update):
        await safe_reply(update, "⛔ You are not authorized.")
        return
    
    conversations = database.get_all_conversations_with_details()
    
    if not conversations:
        message = """💬 **Active Conversations**

📭 No active conversations found.
New conversations will appear here when users send messages."""
    else:
        message = "💬 **Active Conversations**\n\n"
        
        for i, conv in enumerate(conversations[:8], 1):
            username = conv.get('username', 'Unknown')
            unread = conv.get('unread_count', 0)
            credits = conv.get('message_credits', 0)
            last_msg = conv.get('last_message', '')[:35] + '...' if conv.get('last_message') else 'No messages'
            
            # Tier indicators
            if credits >= 100:
                tier_emoji, tier_text = "🏆", "VIP"
            elif credits >= 50:
                tier_emoji, tier_text = "⭐", "Regular"
            else:
                tier_emoji, tier_text = "🆕", "New"
            
            # Priority indicators  
            priority_emoji = "📌🔥" if unread >= 3 else "📌" if unread > 0 else ""
            
            message += f"{priority_emoji} **{i}.** @{username} {tier_emoji} {tier_text}\n"
            message += f"    💬 {conv.get('total_messages', 0)} msgs"
            if unread > 0:
                message += f" ({unread})"
            message += f" • {conv.get('time_ago', 'Unknown')}\n"
            message += f"    _{last_msg}_\n\n"

    keyboard = [
        [
            InlineKeyboardButton("📌 Priority (3)", callback_data='priority_convs'),
            InlineKeyboardButton("📬 Unread (5)", callback_data='unread_convs')
        ],
        [
            InlineKeyboardButton("📋 View All", callback_data='all_convs'),
            InlineKeyboardButton("📦 Archived", callback_data='archived_convs')
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data='refresh_convs'),
            InlineKeyboardButton("⚙️ Conv Settings", callback_data='conv_settings')
        ]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced dashboard command - /dashboard"""
    if not is_admin(update):
        await safe_reply(update, "⛔ You are not authorized.")
        return
    
    stats = await database.get_enhanced_dashboard_stats()
    
    message = f"""📊 **Admin Dashboard**

👥 **User Metrics:**
• Total Users: {stats.get('total_users', 0)}
• ✅ Active Users: {stats.get('active_users', 0)}
• 🚫 Banned Users: {stats.get('banned_users', 0)}

💬 **Conversation Metrics:**
• Active Conversations: {stats.get('active_conversations', 0)}
• 📬 Unread Messages: {stats.get('unread_messages', 0)}

💰 **Credit Metrics:**
• Total Credits: {stats.get('total_credits', 0):,}
• ⏰ Total Time: {stats.get('total_time_hours', 0)}h

📈 **Activity**
• Today: {stats.get('today_users', 0)} users
• This Week: {stats.get('week_users', 0)} users"""

    keyboard = [
        [
            InlineKeyboardButton("💬 Conversations", callback_data='dash_conversations'),
            InlineKeyboardButton("📊 Detailed Stats", callback_data='detailed_stats')
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data='dash_broadcast'),
            InlineKeyboardButton("🎁 Mass Gift", callback_data='mass_gift')
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='dash_settings'),
            InlineKeyboardButton("🔄 Refresh", callback_data='refresh_dashboard')
        ]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced user management command - /users"""
    if not is_admin(update):
        await safe_reply(update, "⛔ You are not authorized.")
        return
    
    users = database.get_all_users(limit=10)
    stats = database.get_user_stats()
    
    message = f"""👥 **User Management**

📊 **Statistics:**
• Total Users: {stats.get('total_users', 0)}
• 🚫 Banned Users: {stats.get('banned_users', 0)}
• 🏆 VIP Users: {stats.get('vip_users', 0)}
• 🆕 New Users (24h): {stats.get('new_users_24h', 0)}

📋 **Recent Users:**"""

    if users:
        for user in users[:5]:
            username = user.get('username', 'No username')
            user_id = user.get('telegram_id')
            credits = user.get('message_credits', 0)
            status = "🚫 Banned" if user.get('is_banned') else "✅ Active"
            
            message += f"\n• @{username} ({user_id}) - {status}"
            message += f"\n  💰 {credits} credits"
    else:
        message += "\nNo users found."

    keyboard = [
        [
            InlineKeyboardButton("👥 All Users", callback_data='all_users'),
            InlineKeyboardButton("🚫 Banned Users", callback_data='banned_users')
        ],
        [
            InlineKeyboardButton("🏆 VIP Users", callback_data='vip_users'),
            InlineKeyboardButton("🆕 New Users", callback_data='new_users')
        ],
        [
            InlineKeyboardButton("💰 Edit Credits", callback_data='edit_credits'),
            InlineKeyboardButton("🎁 Gift Credits", callback_data='gift_credits')
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data='ban_user'),
            InlineKeyboardButton("✅ Unban User", callback_data='unban_user')
        ]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced settings command - /settings"""
    if not is_admin(update):
        await safe_reply(update, "⛔ You are not authorized.")
        return
    
    welcome_msg = database.get_setting('welcome_message', 'Welcome!')[:50] + '...'
    text_cost = database.get_setting('cost_text_message', '1')
    photo_cost = database.get_setting('cost_photo_message', '3')
    
    message = f"""⚙️ **Admin Settings Panel**

**Current Configuration:**
• Welcome: "{welcome_msg}"
• Text Cost: {text_cost} credits
• Photo Cost: {photo_cost} credits

What would you like to do?"""

    keyboard = [
        [
            InlineKeyboardButton("📝 Edit Welcome Message", callback_data='edit_welcome'),
            InlineKeyboardButton("💰 Edit Message Costs", callback_data='edit_costs')
        ],
        [
            InlineKeyboardButton("🏆 User Tier Settings", callback_data='tier_settings'),
            InlineKeyboardButton("🎁 Gift & Quick Buy Settings", callback_data='gift_settings')
        ],
        [
            InlineKeyboardButton("🔒 Content Price Limits", callback_data='price_limits'),
            InlineKeyboardButton("⏰ Time & Auto-Recharge", callback_data='time_settings')
        ],
        [
            InlineKeyboardButton("💬 Quick Reply Messages", callback_data='quick_replies'),
            InlineKeyboardButton("📦 Manage Products", callback_data='manage_products')
        ],
        [
            InlineKeyboardButton("👥 Manage Users", callback_data='manage_users'),
            InlineKeyboardButton("📊 View Statistics", callback_data='view_stats')
        ],
        [
            InlineKeyboardButton("📤 Export Settings", callback_data='export_settings'),
            InlineKeyboardButton("📥 Import Settings", callback_data='import_settings')
        ],
        [InlineKeyboardButton("❌ Close", callback_data='close_settings')]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# Add quick buy commands for users
async def buy10_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Quick buy 10 credits - /buy10"""
    user_id = update.effective_user.id
    
    message = """🚀 **Quick Buy - 10 Credits**

💰 **Package Details:**
• 10 message credits
• Instant delivery
• Perfect for light usage

💳 **Quick Purchase:**
Click below to buy instantly!"""

    keyboard = [
        [InlineKeyboardButton("💳 Buy 10 Credits Now", callback_data="buy_1")],
        [InlineKeyboardButton("📊 Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton("🛒 View All Packages", callback_data="view_packages")]
    ]
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def buy25_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Quick buy 25 credits - /buy25"""
    user_id = update.effective_user.id
    
    message = """💼 **Quick Buy - 25 Credits**

💰 **Package Details:**
• 25 message credits
• Best value for regular users
• Instant delivery

💳 **Quick Purchase:**
Click below to buy instantly!"""

    keyboard = [
        [InlineKeyboardButton("💳 Buy 25 Credits Now", callback_data="buy_2")],
        [InlineKeyboardButton("📊 Check Balance", callback_data="check_balance")],
        [InlineKeyboardButton("🛒 View All Packages", callback_data="view_packages")]
    ]
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def billing_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Customer billing portal - /billing"""
    user_id = update.effective_user.id
    user_credits = database.get_user_credits_optimized(user_id)
    
    message = f"""💳 **Customer Portal**

👤 **Your Account:**
• Current Balance: {user_credits} credits
• Account Status: ✅ Active
• Member Since: Recent

🎫 **Manage Your Account:**
Access your customer portal to:
• View purchase history
• Update payment methods  
• Manage subscriptions
• Download invoices"""

    keyboard = [
        [
            InlineKeyboardButton("🛒 Buy Credits", callback_data="buy_credits"),
            InlineKeyboardButton("📊 Balance Details", callback_data="balance_details")
        ],
        [
            InlineKeyboardButton("💳 Payment Methods", callback_data="payment_methods"),
            InlineKeyboardButton("📄 Invoice History", callback_data="invoice_history")
        ],
        [
            InlineKeyboardButton("🔄 Auto-Recharge", callback_data="auto_recharge"),
            InlineKeyboardButton("❓ Billing Help", callback_data="billing_help")
        ]
    ]
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def topic_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check topic system status - /topic_status (admin only)"""
    if not is_admin(update):
        await safe_reply(update, "⛔ You are not authorized.")
        return
    
    # Check topic system configuration
    admin_group_configured = bool(settings.ADMIN_GROUP_ID)
    topic_stats = database.get_topic_statistics()
    
    # Test admin group accessibility
    group_accessible = False
    forum_enabled = False
    if settings.ADMIN_GROUP_ID:
        try:
            chat = await context.bot.get_chat(settings.ADMIN_GROUP_ID)
            group_accessible = True
            forum_enabled = getattr(chat, 'is_forum', False)
        except Exception as e:
            logger.error(f"Cannot access admin group: {e}")
    
    # Generate status report
    status_emoji = "✅" if admin_group_configured and group_accessible and forum_enabled else "⚠️"
    
    message = f"""🎉 **Topic System Status** {status_emoji}

**🔧 Configuration:**
• Admin Group ID: {settings.ADMIN_GROUP_ID or 'Not configured'}
• Group Accessible: {'✅ Yes' if group_accessible else '❌ No'}
• Forum Enabled: {'✅ Yes' if forum_enabled else '❌ No'}

**📊 Statistics:**
• Total Topics Created: {topic_stats.get('total_topics', 0)}
• Active Conversations: {topic_stats.get('active_topics', 0)}
• System Status: {'🟢 Operational' if admin_group_configured and group_accessible else '🔴 Issues'}

**✅ Features Available:**
• Auto Topic Creation: {'✅' if admin_group_configured else '❌'}
• User Info Cards: {'✅' if admin_group_configured else '❌'}
• Direct Topic Replies: {'✅' if admin_group_configured and forum_enabled else '❌'}
• Media Support: ✅ All message types
• Fallback System: ✅ Private chat backup
• Admin Tools: ✅ Full integration

**🧪 Testing:**
To test the system:
1. Send a message to @nsxochatbot from another account
2. Check admin group for new topic creation
3. Reply in the topic to test admin responses

**📋 Requirements:**
• Admin group must be a forum/supergroup
• Bot must be admin with 'Manage Topics' permission
• Forum topics must be enabled in group settings"""

    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh Status", callback_data='refresh_topic_status'),
            InlineKeyboardButton("📊 View Topics", callback_data='view_all_topics')
        ],
        [
            InlineKeyboardButton("🧪 Test Topic Creation", callback_data='test_topic'),
            InlineKeyboardButton("⚙️ Topic Settings", callback_data='topic_settings')
        ]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def buy_content_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the process of buying locked content."""
    args = context.args
    if not args:
        await safe_reply(update, "Please provide a content ID. Usage: /buy_content <ID>")
        return
    
    try:
        content_id = int(args[0])
        content = database.get_locked_content(content_id)
        
        if not content or not content['is_active']:
            await safe_reply(update, "❌ Invalid or unavailable content ID.")
            return

        price = content['price']
        description = content['description']
        user_credits = database.get_user_credits_optimized(update.effective_user.id)
        
        message = f"""🖼️ **Premium Content**

**Description:** {description}
**Price:** {price} credits

Your current balance is {user_credits} credits.

Do you want to purchase this content?"""

        keyboard = [
            [
                InlineKeyboardButton(f"✅ Yes, buy for {price} credits", callback_data=f"purchase_{content_id}"),
                InlineKeyboardButton("❌ No, cancel", callback_data="cancel_purchase")
            ]
        ]
        
        await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        
    except ValueError:
        await safe_reply(update, "❌ Invalid content ID. Please provide a valid number.")

async def handle_content_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the purchase of locked content."""
    query = update.callback_query
    await query.answer()

    content_id = int(query.data.split("_")[1])
    user_id = query.from_user.id

    content = database.get_locked_content(content_id)
    if not content:
        await query.edit_message_text("❌ This content is no longer available.")
        return

    price = content['price']
    user_credits = database.get_user_credits_optimized(user_id)

    if user_credits < price:
        await query.edit_message_text(f"❌ Insufficient credits. You need {price} credits, but only have {user_credits}. Please /buy more.")
        return

    # Deduct credits and send content
    new_balance = database.decrement_user_credits_optimized(user_id, price)
    
    await query.edit_message_text(f"✅ Purchase successful! Your new balance is {new_balance} credits.")
    
    # Send the locked content to the user
    content_type = content['content_type']
    file_id = content['file_id']
    caption = content['description']
    
    try:
        if content_type == 'photo':
            await context.bot.send_photo(chat_id=user_id, photo=file_id, caption=caption)
        elif content_type == 'video':
            await context.bot.send_video(chat_id=user_id, video=file_id, caption=caption)
        elif content_type == 'document':
            await context.bot.send_document(chat_id=user_id, document=file_id, caption=caption)
    except Exception as e:
        logger.error(f"Error sending locked content {content_id} to user {user_id}: {e}")
        await query.message.reply_text("⚠️ There was an error sending the content. Please contact support.")

# ========================= Enhanced Visual Components =========================

def format_user_tier(credits: int) -> tuple[str, str]:
    """Get tier emoji and text based on credits."""
    if credits >= 100:
        return "🏆", "VIP"
    elif credits >= 50:
        return "⭐", "Regular"
    else:
        return "🆕", "New"

def format_priority_indicator(unread_count: int) -> str:
    """Get priority indicator based on unread messages."""
    if unread_count >= 3:
        return "📌🔥"
    elif unread_count > 0:
        return "📌"
    else:
        return ""

def format_time_ago(timestamp) -> str:
    """Format timestamp to human readable."""
    # Placeholder - implement actual time formatting
    return "5m ago"

# ========================= Command Registration =========================

def get_enhanced_admin_commands() -> List[CommandHandler]:
    """Get list of enhanced admin command handlers."""
    return [
        CommandHandler("conversations", conversations_command),
        CommandHandler("dashboard", dashboard_command),
        CommandHandler("users", users_command),
        CommandHandler("settings", settings_command),
        CommandHandler("topic_status", topic_status_command),  # Add topic status command
        CommandHandler("buy_content", buy_content_command),
    ] 

def get_enhanced_user_commands() -> List[CommandHandler]:
    """Get enhanced user command handlers."""
    return [
        CommandHandler("buy10", buy10_command),
        CommandHandler("buy25", buy25_command), 
        CommandHandler("billing", billing_command),
    ] 