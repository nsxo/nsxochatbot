#!/usr/bin/env python3
"""
Enhanced Menu System with Beautiful Telegram Inline Keyboard Buttons
Professional menu design matching modern Telegram bot standards
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src import database
from src.config import settings

logger = logging.getLogger(__name__)


class MenuStyles:
    """Beautiful button styles with emojis and rounded appearance"""
    
    # Primary action buttons (main functions)
    PRIMARY = {
        'send_message': '💬 Send Message',
        'buy_credits': '💳 Buy Credits', 
        'check_balance': '📊 My Balance',
        'content_store': '🔒 Content Store',
        'settings': '⚙️ Settings',
        'help': '❓ Help & Support'
    }
    
    # Secondary action buttons (supporting functions)
    SECONDARY = {
        'tutorial': '📖 Quick Tutorial',
        'profile': '👤 My Profile',
        'history': '📋 Purchase History',
        'notifications': '🔔 Notifications',
        'auto_recharge': '🔄 Auto-Recharge',
        'referrals': '👥 Invite Friends'
    }
    
    # Admin menu buttons
    ADMIN = {
        'dashboard': '📊 Dashboard',
        'conversations': '💬 Conversations', 
        'users': '👥 User Management',
        'products': '🛒 Product Manager',
        'analytics': '📈 Analytics',
        'billing': '💰 Billing & Revenue',
        'broadcast': '📢 Broadcast Message',
        'settings': '⚙️ Bot Settings',
        'system': '🔧 System Status',
        'reports': '📋 Reports'
    }
    
    # Navigation buttons
    NAVIGATION = {
        'back': '◀️ Back',
        'main_menu': '🏠 Main Menu',
        'close': '❌ Close',
        'refresh': '🔄 Refresh',
        'next': '▶️ Next',
        'previous': '◀️ Previous'
    }
    
    # Status buttons
    STATUS = {
        'online': '🟢 Online',
        'away': '🟡 Away', 
        'busy': '🔴 Busy',
        'offline': '⚫ Offline',
        'maintenance': '🔧 Maintenance'
    }
    
    # Credit package buttons
    PACKAGES = {
        'starter': '🚀 Starter Pack',
        'basic': '💼 Basic Pack',
        'premium': '⭐ Premium Pack', 
        'power': '🏆 Power Pack',
        'mega': '💎 Mega Pack',
        'enterprise': '🌟 Enterprise Pack'
    }


class UserMenuSystem:
    """Enhanced user menu system with beautiful layouts"""
    
    @staticmethod
    def create_main_menu(user_id: int, is_new_user: bool = False) -> List[List[InlineKeyboardButton]]:
        """Create the main user menu with priority-based layout"""
        user_credits = database.get_user_credits_optimized(user_id)
        user_tier = database.get_user_tier(user_id)
        
        keyboard = []
        
        # Row 1: Primary actions (most important)
        if is_new_user:
            keyboard.append([
                InlineKeyboardButton("🚀 Get Started!", callback_data="quick_start"),
                InlineKeyboardButton("📖 Tutorial", callback_data="tutorial")
            ])
        
        # Row 2: Core functionality 
        keyboard.append([
            InlineKeyboardButton("💬 Send Message", callback_data="contact_support"),
            InlineKeyboardButton("💳 Buy Credits", callback_data="buy_menu")
        ])
        
        # Row 3: Account & content
        keyboard.append([
            InlineKeyboardButton("📊 My Account", callback_data="check_balance"),
            InlineKeyboardButton("🔒 Content Store", callback_data="content_store")
        ])
        
        # Row 4: Settings & help
        keyboard.append([
            InlineKeyboardButton("⚙️ Settings", callback_data="user_settings"),
            InlineKeyboardButton("❓ Help & FAQ", callback_data="help_menu")
        ])
        
        # Row 5: Special features for different user types
        if user_tier == "VIP":
            keyboard.append([
                InlineKeyboardButton("🏆 VIP Benefits", callback_data="vip_benefits"),
                InlineKeyboardButton("👥 Refer Friends", callback_data="referral_program")
            ])
        elif user_credits < 5:
            keyboard.append([
                InlineKeyboardButton("⚡ Quick Recharge", callback_data="quick_recharge"),
                InlineKeyboardButton("🎁 Free Credits", callback_data="earn_credits")
            ])
        
        return keyboard
    
    @staticmethod 
    def create_buy_menu() -> List[List[InlineKeyboardButton]]:
        """Create the enhanced credit purchase menu"""
        products = database.get_active_products()
        keyboard = []
        
        # Group products by type/size
        starter_products = [p for p in products if p['amount'] <= 25]
        regular_products = [p for p in products if 26 <= p['amount'] <= 100] 
        premium_products = [p for p in products if p['amount'] > 100]
        
        # Quick buy section (most popular)
        keyboard.append([
            InlineKeyboardButton("⚡ Quick Buy", callback_data="quick_buy_menu")
        ])
        
        # Package categories
        if starter_products:
            keyboard.append([
                InlineKeyboardButton("🚀 Starter Packs", callback_data="category_starter")
            ])
        
        if regular_products:
            keyboard.append([
                InlineKeyboardButton("💼 Regular Packs", callback_data="category_regular")
            ])
            
        if premium_products:
            keyboard.append([
                InlineKeyboardButton("🏆 Premium Packs", callback_data="category_premium")
            ])
        
        # Special offers
        keyboard.append([
            InlineKeyboardButton("🎁 Special Offers", callback_data="special_offers"),
            InlineKeyboardButton("📊 Compare Plans", callback_data="compare_plans")
        ])
        
        # Tools and navigation
        keyboard.append([
            InlineKeyboardButton("💰 Value Calculator", callback_data="value_calculator"),
            InlineKeyboardButton("❓ Help Me Choose", callback_data="help_choose")
        ])
        
        keyboard.append([
            InlineKeyboardButton("🔄 Auto-Recharge", callback_data="setup_autorecharge"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
        ])
        
        return keyboard
    
    @staticmethod
    def create_settings_menu(user_id: int) -> List[List[InlineKeyboardButton]]:
        """Create user settings menu"""
        auto_recharge = database.get_user_auto_recharge_settings(user_id)
        auto_status = "✅ Enabled" if auto_recharge and auto_recharge.get('enabled') else "❌ Disabled"
        
        keyboard = [
            [
                InlineKeyboardButton(f"🔄 Auto-Recharge {auto_status}", callback_data="toggle_autorecharge"),
                InlineKeyboardButton("🔔 Notifications", callback_data="notification_settings")
            ],
            [
                InlineKeyboardButton("👤 Edit Profile", callback_data="edit_profile"),
                InlineKeyboardButton("📋 Message History", callback_data="message_history")
            ],
            [
                InlineKeyboardButton("🏆 Tier Progress", callback_data="tier_progress"),
                InlineKeyboardButton("📊 Usage Stats", callback_data="usage_stats")
            ],
            [
                InlineKeyboardButton("🔐 Privacy Settings", callback_data="privacy_settings"),
                InlineKeyboardButton("🌍 Language", callback_data="language_settings")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        return keyboard
    
    @staticmethod
    def create_account_menu(user_id: int) -> List[List[InlineKeyboardButton]]:
        """Create detailed account information menu"""
        user_credits = database.get_user_credits_optimized(user_id)
        user_tier = database.get_user_tier(user_id)
        
        keyboard = [
            [
                InlineKeyboardButton("💰 Credit Balance", callback_data="detailed_balance"),
                InlineKeyboardButton("🏆 Tier Status", callback_data="tier_details")
            ],
            [
                InlineKeyboardButton("📋 Transaction History", callback_data="transaction_history"),
                InlineKeyboardButton("📊 Usage Statistics", callback_data="usage_statistics")
            ],
            [
                InlineKeyboardButton("🎯 Spending Analysis", callback_data="spending_analysis"),
                InlineKeyboardButton("📈 Activity Report", callback_data="activity_report")
            ],
            [
                InlineKeyboardButton("💳 Payment Methods", callback_data="payment_methods"),
                InlineKeyboardButton("🧾 Invoices", callback_data="invoices")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        return keyboard


class AdminMenuSystem:
    """Enhanced admin menu system with comprehensive controls"""
    
    @staticmethod
    def create_main_admin_menu() -> List[List[InlineKeyboardButton]]:
        """Create the main admin control panel"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Dashboard", callback_data="dashboard"),
                InlineKeyboardButton("💬 Conversations", callback_data="conversations")
            ],
            [
                InlineKeyboardButton("👥 User Management", callback_data="user_management"),
                InlineKeyboardButton("🛒 Product Manager", callback_data="products")
            ],
            [
                InlineKeyboardButton("📈 Analytics", callback_data="analytics"),
                InlineKeyboardButton("💰 Billing & Revenue", callback_data="billing")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
                InlineKeyboardButton("🎁 Mass Actions", callback_data="mass_actions")
            ],
            [
                InlineKeyboardButton("⚙️ Bot Settings", callback_data="settings"),
                InlineKeyboardButton("🔧 System Status", callback_data="system")
            ],
            [
                InlineKeyboardButton("📝 Quick Replies", callback_data="quick_replies"),
                InlineKeyboardButton("🔍 Search & Reports", callback_data="search")
            ],
            [
                InlineKeyboardButton("📊 Live Status", callback_data="status"),
                InlineKeyboardButton("🔄 Refresh Data", callback_data="refresh")
            ],
            [
                InlineKeyboardButton("❌ Close Panel", callback_data="exit")
            ]
        ]
        
        return keyboard
    
    @staticmethod
    def create_user_management_menu() -> List[List[InlineKeyboardButton]]:
        """Create user management submenu"""
        keyboard = [
            [
                InlineKeyboardButton("👥 All Users", callback_data="all_users"),
                InlineKeyboardButton("🆕 New Users", callback_data="new_users")
            ],
            [
                InlineKeyboardButton("⭐ VIP Users", callback_data="vip_users"),
                InlineKeyboardButton("🚫 Banned Users", callback_data="banned_users")
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
                InlineKeyboardButton("📊 User Analytics", callback_data="user_analytics"),
                InlineKeyboardButton("📤 Export Users", callback_data="export_users")
            ],
            [
                InlineKeyboardButton("🔍 Search Users", callback_data="search_users"),
                InlineKeyboardButton("👑 Promote to VIP", callback_data="promote_vip")
            ],
            [
                InlineKeyboardButton("🏠 Admin Menu", callback_data="back_to_main")
            ]
        ]
        
        return keyboard
    
    @staticmethod
    def create_product_management_menu() -> List[List[InlineKeyboardButton]]:
        """Create product management submenu"""
        keyboard = [
            [
                InlineKeyboardButton("➕ Create Product", callback_data="create_product"),
                InlineKeyboardButton("✏️ Edit Product", callback_data="edit_product")
            ],
            [
                InlineKeyboardButton("👁️ View All Products", callback_data="view_all_products"),
                InlineKeyboardButton("🔄 Toggle Status", callback_data="toggle_product_status")
            ],
            [
                InlineKeyboardButton("🗑️ Delete Product", callback_data="delete_product"),
                InlineKeyboardButton("📊 Product Analytics", callback_data="product_analytics")
            ],
            [
                InlineKeyboardButton("💳 Sync Stripe", callback_data="sync_stripe"),
                InlineKeyboardButton("📤 Export Products", callback_data="export_products")
            ],
            [
                InlineKeyboardButton("🎯 Set Featured", callback_data="set_featured"),
                InlineKeyboardButton("🏷️ Manage Categories", callback_data="manage_categories")
            ],
            [
                InlineKeyboardButton("🏠 Admin Menu", callback_data="back_to_main")
            ]
        ]
        
        return keyboard
    
    @staticmethod
    def create_analytics_menu() -> List[List[InlineKeyboardButton]]:
        """Create analytics and reporting menu"""
        keyboard = [
            [
                InlineKeyboardButton("📊 User Analytics", callback_data="user_analytics"),
                InlineKeyboardButton("💬 Message Analytics", callback_data="message_analytics")
            ],
            [
                InlineKeyboardButton("💰 Revenue Analytics", callback_data="revenue_analytics"),
                InlineKeyboardButton("⏱️ Performance Metrics", callback_data="performance_metrics")
            ],
            [
                InlineKeyboardButton("📈 Growth Analytics", callback_data="growth_analytics"),
                InlineKeyboardButton("🎯 Conversion Metrics", callback_data="conversion_metrics")
            ],
            [
                InlineKeyboardButton("📋 Custom Reports", callback_data="custom_reports"),
                InlineKeyboardButton("📤 Export Data", callback_data="export_analytics")
            ],
            [
                InlineKeyboardButton("📅 Daily Report", callback_data="daily_report"),
                InlineKeyboardButton("📆 Weekly Summary", callback_data="weekly_summary")
            ],
            [
                InlineKeyboardButton("🔔 Set Alerts", callback_data="set_alerts"),
                InlineKeyboardButton("📊 Live Dashboard", callback_data="live_dashboard")
            ],
            [
                InlineKeyboardButton("🏠 Admin Menu", callback_data="back_to_main")
            ]
        ]
        
        return keyboard
    
    @staticmethod
    def create_broadcast_menu() -> List[List[InlineKeyboardButton]]:
        """Create broadcast and communication menu"""
        keyboard = [
            [
                InlineKeyboardButton("📢 Broadcast All", callback_data="broadcast_all"),
                InlineKeyboardButton("🎯 Targeted Broadcast", callback_data="broadcast_targeted")
            ],
            [
                InlineKeyboardButton("⭐ Message VIPs", callback_data="broadcast_vips"),
                InlineKeyboardButton("🆕 Message New Users", callback_data="broadcast_new")
            ],
            [
                InlineKeyboardButton("🔔 Send Announcement", callback_data="send_announcement"),
                InlineKeyboardButton("⚠️ Emergency Alert", callback_data="emergency_alert")
            ],
            [
                InlineKeyboardButton("📋 Message Templates", callback_data="message_templates"),
                InlineKeyboardButton("📊 Broadcast History", callback_data="broadcast_history")
            ],
            [
                InlineKeyboardButton("🎁 Promotional Message", callback_data="promo_message"),
                InlineKeyboardButton("📈 Campaign Analytics", callback_data="campaign_analytics")
            ],
            [
                InlineKeyboardButton("⏰ Schedule Message", callback_data="schedule_message"),
                InlineKeyboardButton("🔄 Recurring Messages", callback_data="recurring_messages")
            ],
            [
                InlineKeyboardButton("🏠 Admin Menu", callback_data="back_to_main")
            ]
        ]
        
        return keyboard
    
    @staticmethod
    def create_system_menu() -> List[List[InlineKeyboardButton]]:
        """Create system management menu"""
        keyboard = [
            [
                InlineKeyboardButton("🔧 System Status", callback_data="system_status"),
                InlineKeyboardButton("📊 Performance Monitor", callback_data="performance_monitor")
            ],
            [
                InlineKeyboardButton("🗄️ Database Health", callback_data="database_health"),
                InlineKeyboardButton("📡 API Status", callback_data="api_status")
            ],
            [
                InlineKeyboardButton("🔄 Restart Services", callback_data="restart_services"),
                InlineKeyboardButton("🧹 Clean Cache", callback_data="clean_cache")
            ],
            [
                InlineKeyboardButton("💾 Backup Database", callback_data="backup_database"),
                InlineKeyboardButton("📥 Restore Backup", callback_data="restore_backup")
            ],
            [
                InlineKeyboardButton("📋 System Logs", callback_data="system_logs"),
                InlineKeyboardButton("⚠️ Error Reports", callback_data="error_reports")
            ],
            [
                InlineKeyboardButton("🔐 Security Audit", callback_data="security_audit"),
                InlineKeyboardButton("📊 Resource Usage", callback_data="resource_usage")
            ],
            [
                InlineKeyboardButton("🏠 Admin Menu", callback_data="back_to_main")
            ]
        ]
        
        return keyboard


class MenuGenerator:
    """Helper class to generate menus dynamically"""
    
    @staticmethod
    def create_confirmation_menu(action: str, item_id: str = None) -> List[List[InlineKeyboardButton]]:
        """Create a confirmation dialog menu"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{item_id}" if item_id else f"confirm_{action}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")
            ]
        ]
        return keyboard
    
    @staticmethod
    def create_pagination_menu(page: int, total_pages: int, base_callback: str) -> List[List[InlineKeyboardButton]]:
        """Create pagination controls"""
        keyboard = []
        
        # Navigation row
        nav_row = []
        if page > 1:
            nav_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"{base_callback}_page_{page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
        
        if page < total_pages:
            nav_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"{base_callback}_page_{page+1}"))
        
        keyboard.append(nav_row)
        
        # Quick jump options for large lists
        if total_pages > 5:
            keyboard.append([
                InlineKeyboardButton("⏮️ First", callback_data=f"{base_callback}_page_1"),
                InlineKeyboardButton("⏭️ Last", callback_data=f"{base_callback}_page_{total_pages}")
            ])
        
        return keyboard
    
    @staticmethod
    def create_quick_actions_menu() -> List[List[InlineKeyboardButton]]:
        """Create quick actions for power users"""
        keyboard = [
            [
                InlineKeyboardButton("⚡ Quick Buy 50", callback_data="quick_buy_50"),
                InlineKeyboardButton("🔄 Auto-Recharge", callback_data="toggle_autorecharge")
            ],
            [
                InlineKeyboardButton("📊 Quick Stats", callback_data="quick_stats"),
                InlineKeyboardButton("💬 Last Messages", callback_data="recent_messages")
            ],
            [
                InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"),
                InlineKeyboardButton("👥 Invite Friend", callback_data="invite_friend")
            ]
        ]
        return keyboard
    
    @staticmethod
    def create_filter_menu(filters: Dict[str, str]) -> List[List[InlineKeyboardButton]]:
        """Create filter options menu"""
        keyboard = []
        
        # Create rows of 2 filters each
        filter_items = list(filters.items())
        for i in range(0, len(filter_items), 2):
            row = []
            for j in range(i, min(i + 2, len(filter_items))):
                key, label = filter_items[j]
                row.append(InlineKeyboardButton(label, callback_data=f"filter_{key}"))
            keyboard.append(row)
        
        # Clear filters option
        keyboard.append([
            InlineKeyboardButton("🔄 Clear Filters", callback_data="clear_filters"),
            InlineKeyboardButton("✅ Apply Filters", callback_data="apply_filters")
        ])
        
        return keyboard


class MenuHelpers:
    """Helper functions for menu operations"""
    
    @staticmethod
    def get_user_context_menu(user_id: int) -> List[List[InlineKeyboardButton]]:
        """Get contextual menu based on user state"""
        user_credits = database.get_user_credits_optimized(user_id)
        user_tier = database.get_user_tier(user_id)
        
        if user_credits < 5:
            # Low balance menu
            return [
                [InlineKeyboardButton("⚡ Quick Recharge", callback_data="quick_recharge")],
                [InlineKeyboardButton("🎁 Get Free Credits", callback_data="earn_credits")],
                [InlineKeyboardButton("💳 Buy Credits", callback_data="buy_menu")]
            ]
        elif user_tier == "VIP":
            # VIP menu
            return [
                [InlineKeyboardButton("🏆 VIP Benefits", callback_data="vip_benefits")],
                [InlineKeyboardButton("👑 Exclusive Content", callback_data="vip_content")],
                [InlineKeyboardButton("📊 Premium Analytics", callback_data="premium_analytics")]
            ]
        else:
            # Regular menu
            return UserMenuSystem.create_main_menu(user_id)
    
    @staticmethod
    def get_admin_quick_actions() -> List[List[InlineKeyboardButton]]:
        """Get quick actions for admins"""
        return [
            [
                InlineKeyboardButton("🔥 Live Activity", callback_data="live_activity"),
                InlineKeyboardButton("💰 Today's Revenue", callback_data="today_revenue")
            ],
            [
                InlineKeyboardButton("📊 User Count", callback_data="user_count"),
                InlineKeyboardButton("📈 Growth Rate", callback_data="growth_rate")
            ]
        ]
    
    @staticmethod
    def create_dynamic_keyboard(
        items: List[Dict[str, str]], 
        callback_prefix: str,
        cols: int = 2,
        add_navigation: bool = True
    ) -> List[List[InlineKeyboardButton]]:
        """Create dynamic keyboard from item list"""
        keyboard = []
        
        # Create rows based on column count
        for i in range(0, len(items), cols):
            row = []
            for j in range(i, min(i + cols, len(items))):
                item = items[j]
                button_text = item.get('text', f"Item {j}")
                callback_data = f"{callback_prefix}_{item.get('id', j)}"
                row.append(InlineKeyboardButton(button_text, callback_data=callback_data))
            keyboard.append(row)
        
        # Add navigation if requested
        if add_navigation:
            keyboard.append([
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ])
        
        return keyboard


# Export main classes for use in other modules
__all__ = [
    'MenuStyles', 
    'UserMenuSystem', 
    'AdminMenuSystem', 
    'MenuGenerator', 
    'MenuHelpers'
] 