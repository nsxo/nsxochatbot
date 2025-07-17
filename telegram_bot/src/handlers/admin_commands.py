#!/usr/bin/env python3
"""
Comprehensive admin command system for the Telegram bot.
Professional admin panel with full menu system matching enterprise requirements.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from src import database
from src.config import settings
from src.error_handler import monitor_performance

logger = logging.getLogger(__name__)

# Conversation states for comprehensive admin system
(ADMIN_MENU, CONVERSATIONS_MENU, DASHBOARD_MENU, ANALYTICS_MENU, USER_MANAGEMENT_MENU, 
 PRODUCTS_MENU, BILLING_MENU, BROADCAST_MENU, MASS_GIFT_MENU, SETTINGS_MENU,
 SYSTEM_MENU, QUICK_REPLIES_MENU, SEARCH_MENU, STATUS_MENU) = range(14)

# Sub-states for specific operations
(EDIT_WELCOME, EDIT_COSTS, BAN_USER_INPUT, UNBAN_USER_INPUT, ADD_CREDITS_USER, 
 ADD_CREDITS_AMOUNT, BROADCAST_MESSAGE, GIFT_AMOUNT, SEARCH_INPUT, STATUS_INPUT) = range(14, 24)

# Admin status tracking
admin_status = {
    'status': 'online',
    'message': 'Available for support',
    'last_update': datetime.now()
}

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

def get_admin_status_emoji() -> str:
    """Get emoji for current admin status."""
    status_emojis = {
        'online': '🟢',
        'away': '🟡', 
        'busy': '🔴',
        'offline': '⚫'
    }
    return status_emojis.get(admin_status['status'], '🟢')

async def get_real_time_stats() -> Dict[str, int]:
    """Get real-time statistics for the admin panel."""
    stats = database.get_user_stats()
    
    # Get additional stats
    try:
        # Active conversations (messages in last 24 hours)
        active_convs = database.get_active_conversations_count()
        # Unread messages count
        unread_count = database.get_unread_messages_count()
        # Today's revenue
        today_revenue = database.get_today_revenue()
        # Today's new users
        today_users = database.get_today_new_users()
        
        stats.update({
            'active_conversations': active_convs,
            'unread_messages': unread_count,
            'today_revenue': today_revenue,
            'today_new_users': today_users
        })
    except Exception as e:
        logger.error(f"Error getting real-time stats: {e}")
        stats.update({
            'active_conversations': 0,
            'unread_messages': 0,
            'today_revenue': 0,
            'today_new_users': 0
        })
    
    return stats

# ========================= Main Admin Command =========================

@monitor_performance
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the comprehensive admin system."""
    if not is_admin(update):
        await safe_reply(update, "⛔ You are not authorized.")
        return ConversationHandler.END
    
    stats = await get_real_time_stats()
    status_emoji = get_admin_status_emoji()
    
    header = f"""👨‍💼 **Admin Panel** {status_emoji}

📊 **Quick Stats:**
👥 Users: {stats.get('total_users', 0)} | 🆕 Today: {stats.get('today_new_users', 0)}
💬 Active: {stats.get('active_conversations', 0)} | 📬 Unread: {stats.get('unread_messages', 0)}
💰 Today Revenue: ${stats.get('today_revenue', 0):.2f}

**Status:** {admin_status['status'].title()} - {admin_status['message']}"""

    keyboard = [
        [
            InlineKeyboardButton("💬 Conversations", callback_data='conversations'),
            InlineKeyboardButton("📊 Dashboard", callback_data='dashboard')
        ],
        [
            InlineKeyboardButton("📈 Analytics", callback_data='analytics'),
            InlineKeyboardButton("👥 Users", callback_data='user_management')
        ],
        [
            InlineKeyboardButton("🛒 Products", callback_data='products'),
            InlineKeyboardButton("💰 Billing", callback_data='billing')
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data='broadcast'),
            InlineKeyboardButton("🎁 Mass Gift", callback_data='mass_gift')
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
            InlineKeyboardButton("🔧 System", callback_data='system')
        ],
        [
            InlineKeyboardButton("📝 Quick Replies", callback_data='quick_replies'),
            InlineKeyboardButton("🔍 Search", callback_data='search')
        ],
        [
            InlineKeyboardButton(f"{status_emoji} Status", callback_data='status'),
            InlineKeyboardButton("🔄 Refresh", callback_data='refresh')
        ],
        [InlineKeyboardButton("❌ Close", callback_data='exit')]
    ]
    
    await safe_reply(update, header, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return ADMIN_MENU

# ========================= Conversations Menu =========================

async def conversations_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle conversations management menu."""
    stats = await get_real_time_stats()
    
    message = f"""💬 **Conversation Management**

📊 **Current Status:**
• Active Conversations: {stats.get('active_conversations', 0)}
• Unread Messages: {stats.get('unread_messages', 0)}
• High Priority: {stats.get('high_priority_convs', 0)}
• Archived: {stats.get('archived_convs', 0)}"""

    keyboard = [
        [
            InlineKeyboardButton("📋 All Conversations", callback_data='all_conversations'),
            InlineKeyboardButton("📬 Unread Only", callback_data='unread_conversations')
        ],
        [
            InlineKeyboardButton("🎯 High Priority", callback_data='priority_conversations'),
            InlineKeyboardButton("📦 Archived", callback_data='archived_conversations')
        ],
        [
            InlineKeyboardButton("📊 Conv Stats", callback_data='conversation_stats'),
            InlineKeyboardButton("⚙️ Conv Settings", callback_data='conversation_settings')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return CONVERSATIONS_MENU

# ========================= Dashboard Menu =========================

async def dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display comprehensive admin dashboard."""
    stats = await get_real_time_stats()
    
    # Calculate growth percentages
    yesterday_users = database.get_yesterday_new_users()
    user_growth = "+∞%" if yesterday_users == 0 else f"+{((stats.get('today_new_users', 0) - yesterday_users) / yesterday_users * 100):.1f}%"
    
    message = f"""📊 **Admin Dashboard**

👥 **User Metrics:**
• Total Users: {stats.get('total_users', 0)}
• New Today: {stats.get('today_new_users', 0)} ({user_growth})
• Banned Users: {stats.get('banned_users', 0)}
• Active Users (24h): {stats.get('active_users_24h', 0)}

💬 **Conversation Metrics:**
• Active Conversations: {stats.get('active_conversations', 0)}
• Unread Messages: {stats.get('unread_messages', 0)}
• Avg Response Time: {stats.get('avg_response_time', 'N/A')}
• Messages Today: {stats.get('messages_today', 0)}

💰 **Revenue Metrics:**
• Today Revenue: ${stats.get('today_revenue', 0):.2f}
• Month Revenue: ${stats.get('month_revenue', 0):.2f}
• Total Revenue: ${stats.get('total_revenue', 0):.2f}
• Avg Order Value: ${stats.get('avg_order_value', 0):.2f}

🔧 **System Status:**
• Bot Uptime: {stats.get('uptime', 'N/A')}
• Database Status: {'✅ Healthy' if stats.get('db_healthy') else '⚠️ Issues'}
• Webhook Status: {'✅ Active' if stats.get('webhook_active') else '❌ Inactive'}

📅 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    keyboard = [
        [
            InlineKeyboardButton("📈 Detailed Stats", callback_data='detailed_stats'),
            InlineKeyboardButton("📊 Export Data", callback_data='export_data')
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data='refresh_dashboard'),
            InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')
        ]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return DASHBOARD_MENU

# ========================= Analytics Menu =========================

async def analytics_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle analytics and reporting menu."""
    message = """📈 **Analytics & Reporting**

Get detailed insights into your bot's performance:"""

    keyboard = [
        [
            InlineKeyboardButton("📊 User Analytics", callback_data='user_analytics'),
            InlineKeyboardButton("💬 Conversation Analytics", callback_data='conversation_analytics')
        ],
        [
            InlineKeyboardButton("💰 Revenue Analytics", callback_data='revenue_analytics'),
            InlineKeyboardButton("⏱️ Performance Analytics", callback_data='performance_analytics')
        ],
        [
            InlineKeyboardButton("📈 Export Reports", callback_data='export_reports'),
            InlineKeyboardButton("📅 Custom Reports", callback_data='custom_reports')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return ANALYTICS_MENU

# ========================= User Management Menu =========================

async def user_management_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Enhanced user management with comprehensive functionality."""
    if not is_admin(update):
        await safe_reply(update, "❌ Admin access required.")
        return ConversationHandler.END

    users = database.get_all_users(limit=5)  # Get first 5 users for preview
    total_stats = database.get_user_stats()
    
    user_preview = "📋 **Recent Users:**\n"
    if users:
        for user in users[:5]:
            status = "🚫" if user.get('is_banned') else "✅"
            credits = user.get('message_credits', 0)
            username = user.get('username', 'No username')
            user_preview += f"• {status} @{username} - {credits} credits\n"
    else:
        user_preview += "No users found."
    
    message = f"""👥 **User Management**

📊 **Statistics:**
• Total Users: {total_stats.get('total_users', 0)}
• Banned Users: {total_stats.get('banned_users', 0)}
• VIP Users: {total_stats.get('vip_users', 0)}
• New Users (24h): {total_stats.get('new_users_24h', 0)}

{user_preview}"""
    
    keyboard = [
        [
            InlineKeyboardButton("👥 All Users", callback_data="all_users"),
            InlineKeyboardButton("🚫 Banned Users", callback_data="banned_users")
        ],
        [
            InlineKeyboardButton("⭐ VIP Users", callback_data="vip_users"),
            InlineKeyboardButton("🆕 New Users", callback_data="new_users")
        ],
        [
            InlineKeyboardButton("💰 Edit Credits", callback_data="edit_credits"),
            InlineKeyboardButton("🎁 Gift Credits", callback_data="gift_credits")
        ],
        [
            InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"),
            InlineKeyboardButton("✅ Unban User", callback_data="unban_user")
        ],
        [
            InlineKeyboardButton("📊 User Stats", callback_data="user_stats"),
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
        ]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return USER_MANAGEMENT_MENU

# ========================= Continue with more handlers... ========================= 

# ========================= Products Menu =========================

async def products_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle products management menu."""
    products = database.get_active_products()
    
    message = f"""🛒 **Product Management**

📊 **Current Products:** {len(products)}"""

    if products:
        message += "\n\n📋 **Active Products:**\n"
        for product in products[:5]:
            message += f"• {product.get('label', 'Unnamed')} - {product.get('amount', 0)} credits\n"

    keyboard = [
        [
            InlineKeyboardButton("🛒 Manage Products", callback_data='manage_products'),
            InlineKeyboardButton("➕ Create Product", callback_data='create_product')
        ],
        [
            InlineKeyboardButton("📊 Product Stats", callback_data='product_stats'),
            InlineKeyboardButton("💰 Pricing", callback_data='product_pricing')
        ],
        [
            InlineKeyboardButton("🔄 Sync Stripe", callback_data='sync_stripe'),
            InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')
        ]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return PRODUCTS_MENU

# ========================= Settings Menu =========================

async def settings_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle bot settings management."""
    current_welcome = database.get_setting('welcome_message', 'Welcome!')
    current_cost = database.get_setting('cost_text_message', '1')
    
    message = f"""⚙️ **Bot Settings**

📝 **Current Settings:**
• Welcome Message: "{current_welcome[:50]}..."
• Message Cost: {current_cost} credits
• Admin Status: {admin_status['status'].title()}"""

    keyboard = [
        [
            InlineKeyboardButton("📝 Edit Welcome", callback_data='edit_welcome'),
            InlineKeyboardButton("💰 Message Costs", callback_data='edit_costs')
        ],
        [
            InlineKeyboardButton("⏰ Time Sessions", callback_data='time_sessions'),
            InlineKeyboardButton("📤 Export Settings", callback_data='export_settings')
        ],
        [
            InlineKeyboardButton("📥 Import Settings", callback_data='import_settings'),
            InlineKeyboardButton("🔄 Reset Settings", callback_data='reset_settings')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return SETTINGS_MENU

# ========================= System Menu =========================

async def system_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle system monitoring and management."""
    stats = await get_real_time_stats()
    
    message = f"""🔧 **System Management**

🏥 **System Health:**
• Database: {'✅ Healthy' if stats.get('db_healthy', True) else '⚠️ Issues'}
• Webhook: {'✅ Active' if stats.get('webhook_active', True) else '❌ Inactive'}
• Bot Status: 🟢 Running
• Memory Usage: {stats.get('memory_usage', 'N/A')}

⏱️ **Performance:**
• Uptime: {stats.get('uptime', 'N/A')}
• Response Time: {stats.get('avg_response_time', 'N/A')}
• Messages/Hour: {stats.get('messages_per_hour', 0)}"""

    keyboard = [
        [
            InlineKeyboardButton("🔧 System Status", callback_data='system_status'),
            InlineKeyboardButton("📊 Performance", callback_data='performance_stats')
        ],
        [
            InlineKeyboardButton("🗄️ Database", callback_data='database_management'),
            InlineKeyboardButton("📝 Logs", callback_data='system_logs')
        ],
        [
            InlineKeyboardButton("💾 Backup", callback_data='system_backup'),
            InlineKeyboardButton("🛡️ Security", callback_data='security_settings')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return SYSTEM_MENU

# ========================= Status Management =========================

async def status_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle admin status management."""
    current_status = admin_status['status']
    status_emoji = get_admin_status_emoji()
    
    message = f"""📊 **Admin Status Management**

{status_emoji} **Current Status:** {current_status.title()}
💬 **Message:** {admin_status['message']}
🕐 **Last Updated:** {admin_status['last_update'].strftime('%H:%M:%S')}

Set your availability status for users:"""

    keyboard = [
        [
            InlineKeyboardButton("🟢 Online", callback_data='status_online'),
            InlineKeyboardButton("🟡 Away", callback_data='status_away')
        ],
        [
            InlineKeyboardButton("🔴 Busy", callback_data='status_busy'),
            InlineKeyboardButton("⚫ Offline", callback_data='status_offline')
        ],
        [
            InlineKeyboardButton("📝 Custom Message", callback_data='status_custom'),
            InlineKeyboardButton("⏰ Auto Status", callback_data='status_auto')
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_main')]
    ]
    
    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return STATUS_MENU

# ========================= User Management Actions =========================

async def ban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the ban user process."""
    await safe_reply(update, "🚫 **Ban User**\n\nPlease send the user ID to ban:")
    return BAN_USER_INPUT

async def unban_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the unban user process."""
    await safe_reply(update, "✅ **Unban User**\n\nPlease send the user ID to unban:")
    return UNBAN_USER_INPUT

async def process_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process user ban."""
    try:
        user_id = int(update.message.text.strip())
        success = database.ban_user(user_id, "Banned by admin")
        
        if success:
            await safe_reply(update, f"✅ User {user_id} has been banned successfully.")
        else:
            await safe_reply(update, f"❌ Failed to ban user {user_id}.")
            
    except ValueError:
        await safe_reply(update, "❌ Invalid user ID. Please send a valid number.")
    
    return await user_management_handler(update, context)

async def process_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process user unban."""
    try:
        user_id = int(update.message.text.strip())
        success = database.unban_user(user_id)
        
        if success:
            await safe_reply(update, f"✅ User {user_id} has been unbanned successfully.")
        else:
            await safe_reply(update, f"❌ Failed to unban user {user_id}.")
            
    except ValueError:
        await safe_reply(update, "❌ Invalid user ID. Please send a valid number.")
    
    return await user_management_handler(update, context)

# ========================= Navigation Handlers =========================

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to the main admin menu."""
    return await admin_command(update, context)

async def refresh_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Refresh the current menu."""
    return await admin_command(update, context)

async def exit_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exit the admin conversation."""
    await safe_reply(update, "👨‍💼 Admin panel closed. Type /admin to reopen.")
    return ConversationHandler.END

# ========================= Status Update Handlers =========================

async def set_admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE, status: str, message: str) -> int:
    """Set admin status."""
    admin_status['status'] = status
    admin_status['message'] = message
    admin_status['last_update'] = datetime.now()
    
    await safe_reply(update, f"✅ Status updated to: {get_admin_status_emoji()} {status.title()}")
    return await status_menu_handler(update, context)

# ========================= Placeholder Handlers =========================

async def placeholder_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Placeholder for unimplemented features."""
    await safe_reply(update, "🚧 This feature is coming soon!\n\nWe're working on implementing this functionality.")
    return await admin_command(update, context)

# ========================= Conversation Handler Setup =========================

def get_admin_conversation_handler() -> ConversationHandler:
    """Create the comprehensive admin conversation handler."""
    
    return ConversationHandler(
        entry_points=[CommandHandler("admin", admin_command)],
        states={
            ADMIN_MENU: [
                CallbackQueryHandler(conversations_menu_handler, pattern='^conversations$'),
                CallbackQueryHandler(dashboard_handler, pattern='^dashboard$'),
                CallbackQueryHandler(analytics_menu_handler, pattern='^analytics$'),
                CallbackQueryHandler(user_management_handler, pattern='^user_management$'),
                CallbackQueryHandler(products_menu_handler, pattern='^products$'),
                CallbackQueryHandler(placeholder_handler, pattern='^billing$'),
                CallbackQueryHandler(placeholder_handler, pattern='^broadcast$'),
                CallbackQueryHandler(placeholder_handler, pattern='^mass_gift$'),
                CallbackQueryHandler(settings_menu_handler, pattern='^settings$'),
                CallbackQueryHandler(system_menu_handler, pattern='^system$'),
                CallbackQueryHandler(placeholder_handler, pattern='^quick_replies$'),
                CallbackQueryHandler(placeholder_handler, pattern='^search$'),
                CallbackQueryHandler(status_menu_handler, pattern='^status$'),
                CallbackQueryHandler(refresh_menu, pattern='^refresh$'),
                CallbackQueryHandler(exit_conversation, pattern='^exit$'),
            ],
            USER_MANAGEMENT_MENU: [
                CallbackQueryHandler(ban_user_start, pattern='^ban_user$'),
                CallbackQueryHandler(unban_user_start, pattern='^unban_user$'),
                CallbackQueryHandler(placeholder_handler, pattern='^all_users$'),
                CallbackQueryHandler(placeholder_handler, pattern='^banned_users$'),
                CallbackQueryHandler(placeholder_handler, pattern='^vip_users$'),
                CallbackQueryHandler(placeholder_handler, pattern='^new_users$'),
                CallbackQueryHandler(placeholder_handler, pattern='^edit_credits$'),
                CallbackQueryHandler(placeholder_handler, pattern='^gift_credits$'),
                CallbackQueryHandler(placeholder_handler, pattern='^user_stats$'),
                CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$'),
            ],
            BAN_USER_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_ban_user)
            ],
            UNBAN_USER_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_unban_user)
            ],
            STATUS_MENU: [
                CallbackQueryHandler(lambda u, c: set_admin_status(u, c, 'online', 'Available for support'), pattern='^status_online$'),
                CallbackQueryHandler(lambda u, c: set_admin_status(u, c, 'away', 'Temporarily away'), pattern='^status_away$'),
                CallbackQueryHandler(lambda u, c: set_admin_status(u, c, 'busy', 'High workload'), pattern='^status_busy$'),
                CallbackQueryHandler(lambda u, c: set_admin_status(u, c, 'offline', 'Not available'), pattern='^status_offline$'),
                CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$'),
            ],
            # Add other menu states with placeholder handlers
            CONVERSATIONS_MENU: [CallbackQueryHandler(placeholder_handler, pattern='.*'), CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$')],
            DASHBOARD_MENU: [CallbackQueryHandler(placeholder_handler, pattern='.*'), CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$')],
            ANALYTICS_MENU: [CallbackQueryHandler(placeholder_handler, pattern='.*'), CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$')],
            PRODUCTS_MENU: [CallbackQueryHandler(placeholder_handler, pattern='.*'), CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$')],
            SETTINGS_MENU: [CallbackQueryHandler(placeholder_handler, pattern='.*'), CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$')],
            SYSTEM_MENU: [CallbackQueryHandler(placeholder_handler, pattern='.*'), CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$')],
        },
        fallbacks=[
            CallbackQueryHandler(exit_conversation, pattern='^exit$'),
            CommandHandler("cancel", exit_conversation),
        ],
        per_message=False
    )

def get_locked_content_handler() -> ConversationHandler:
    """Create a placeholder locked content handler."""
    return ConversationHandler(
        entry_points=[CommandHandler("lock", placeholder_handler)],
        states={},
        fallbacks=[CommandHandler("cancel", exit_conversation)],
        per_message=False
    ) 