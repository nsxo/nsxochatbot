#!/usr/bin/env python3
"""
Enhanced User Interface with Beautiful Menu Integration
Professional user experience with styled buttons and rich interactions
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from src import database
from src.config import settings
from src.enhanced_menu_system import UserMenuSystem, MenuStyles, MenuHelpers, MenuGenerator
from src.error_handler import rate_limit, monitor_performance
from src.handlers.user_commands import safe_reply, format_balance_display
from src import stripe_utils

logger = logging.getLogger(__name__)


class EnhancedUserInterface:
    """Enhanced user interface with beautiful menus and rich interactions"""
    
    @staticmethod
    @rate_limit(max_calls=20, window_seconds=60)
    @monitor_performance
    async def enhanced_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Enhanced start command with beautiful welcome interface"""
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or "there"
        
        # Ensure user exists
        database.ensure_user_exists(user_id, username, update.effective_user.first_name)
        
        # Get user data
        user_credits = database.get_user_credits_optimized(user_id)
        user_tier = database.get_user_tier(user_id)
        user_stats = database.get_user_stats_individual(user_id)
        is_new_user = user_stats.get('total_messages', 0) == 0
        
        # Welcome header with personalization
        if is_new_user:
            # Give welcome bonus
            bonus_credits = 10
            database.add_user_credits(user_id, bonus_credits)
            user_credits += bonus_credits
            
            welcome_msg = f"""🎉 **Welcome to the Premium Bot Experience!**

Hi @{username}! You've just unlocked access to our premium messaging platform.

🎁 **Welcome Gift:** {bonus_credits} credits added to your account!

✨ **What you can do:**
• 💬 Send messages to our professional team
• 🔒 Access exclusive premium content
• 🏆 Earn tier benefits as you engage
• ⚙️ Customize your experience

{format_balance_display(user_credits)}

🚀 **Ready to get started?** Choose an option below:"""
        else:
            tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
            
            welcome_msg = f"""👋 **Welcome back, @{username}!**

{tier_emoji} **{user_tier} User** • Your premium experience awaits

{format_balance_display(user_credits)}

🎯 **Quick Actions:** Choose what you'd like to do:"""
        
        # Create beautiful keyboard
        keyboard = UserMenuSystem.create_main_menu(user_id, is_new_user)
        
        await safe_reply(update, welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def enhanced_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Enhanced button handler with beautiful menu transitions"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        callback_data = query.data
        
        # Route to appropriate handlers
        if callback_data == "quick_start":
            await EnhancedUserInterface._handle_quick_start(query, context)
        elif callback_data == "contact_support":
            await EnhancedUserInterface._handle_contact_support(query, context)
        elif callback_data == "buy_menu":
            await EnhancedUserInterface._handle_buy_menu(query, context)
        elif callback_data == "check_balance":
            await EnhancedUserInterface._handle_account_details(query, context)
        elif callback_data == "user_settings":
            await EnhancedUserInterface._handle_user_settings(query, context)
        elif callback_data == "content_store":
            await EnhancedUserInterface._handle_content_store(query, context)
        elif callback_data == "help_menu":
            await EnhancedUserInterface._handle_help_menu(query, context)
        elif callback_data.startswith("category_"):
            await EnhancedUserInterface._handle_package_category(query, context)
        elif callback_data.startswith("buy_"):
            await EnhancedUserInterface._handle_product_purchase(query, context)
        elif callback_data == "back_to_start":
            await EnhancedUserInterface._handle_back_to_start(query, context)
        else:
            # Handle other callbacks
            await EnhancedUserInterface._handle_generic_callback(query, context)
    
    @staticmethod
    async def _handle_quick_start(query, context) -> None:
        """Handle quick start tutorial"""
        quick_start_msg = """🚀 **Quick Start Guide**

**Step 1: Your Welcome Bonus** ✅
Perfect! You've already received your welcome credits.

**Step 2: Send Your First Message** 💬
Simply type any message and send it. Our team will respond professionally!

**Step 3: Explore Premium Features** ✨
• 🔒 Browse our exclusive content store
• ⚙️ Configure your preferences
• 🏆 Track your tier progress

**Step 4: Get More Credits** 💳
When you need more credits, our secure payment system makes it easy!

**Message Costs:**
• 💬 Text: 1 credit
• 📷 Photo: 2 credits  
• 🎥 Video: 3 credits
• 📄 Document: 2 credits

✨ **Pro Tip:** Send messages to unlock higher tiers and get discounts!

**Ready to begin?** Choose your next step:"""
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Send First Message", callback_data="contact_support"),
                InlineKeyboardButton("🔒 Explore Content", callback_data="content_store")
            ],
            [
                InlineKeyboardButton("💳 View Credit Packages", callback_data="buy_menu"),
                InlineKeyboardButton("⚙️ Customize Settings", callback_data="user_settings")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        await query.edit_message_text(quick_start_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_contact_support(query, context) -> None:
        """Handle contact support flow"""
        user_id = query.from_user.id
        user_tier = database.get_user_tier(user_id)
        user_credits = database.get_user_credits_optimized(user_id)
        
        tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
        discount = "20%" if user_tier == "VIP" else "10%" if user_tier == "Regular" else "0%"
        
        support_msg = f"""💬 **Contact Our Professional Team**

{tier_emoji} **Your Status:** {user_tier} User ({discount} discount)
💰 **Current Balance:** {user_credits} credits

**How it works:**
1. Type your message below and send it
2. Credits are automatically deducted
3. Our team responds professionally
4. Continue the conversation naturally

**Message Pricing:**
• 💬 Text: {database.apply_tier_discount(1, user_tier)} credits
• 📷 Photo: {database.apply_tier_discount(2, user_tier)} credits
• 🎥 Video: {database.apply_tier_discount(3, user_tier)} credits
• 📄 Document: {database.apply_tier_discount(2, user_tier)} credits

**What to ask:**
• ❓ Questions about our services
• 🛒 Product recommendations
• 🔒 Premium content requests
• 💡 Custom solutions

✨ **Your {user_tier} status gets you priority response!**

**Ready to message?** Type anything below! 👇"""
        
        keyboard = [
            [
                InlineKeyboardButton("💳 Need More Credits?", callback_data="buy_menu"),
                InlineKeyboardButton("📊 View Account", callback_data="check_balance")
            ],
            [
                InlineKeyboardButton("🎁 Get Free Credits", callback_data="earn_credits"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        await query.edit_message_text(support_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_buy_menu(query, context) -> None:
        """Handle credit purchase menu"""
        user_id = query.from_user.id
        user_credits = database.get_user_credits_optimized(user_id)
        user_tier = database.get_user_tier(user_id)
        
        tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
        
        buy_msg = f"""💳 **Premium Credit Store**

{format_balance_display(user_credits)}
{tier_emoji} **Your Tier:** {user_tier} User

🎯 **Recommended for you:**
{EnhancedUserInterface._get_package_recommendation(user_credits, user_tier)}

🛒 **Browse by category or choose quick options:**"""
        
        keyboard = UserMenuSystem.create_buy_menu()
        
        await query.edit_message_text(buy_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_account_details(query, context) -> None:
        """Handle detailed account information"""
        user_id = query.from_user.id
        user_info = database.get_user_info(user_id)
        user_credits = database.get_user_credits_optimized(user_id)
        user_tier = database.get_user_tier(user_id)
        user_stats = database.get_user_stats_individual(user_id)
        
        tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
        
        account_msg = f"""📊 **Account Dashboard**

{format_balance_display(user_credits)}

{tier_emoji} **Tier Status:** {user_tier} User
🎯 **Tier Benefits:** {('20%' if user_tier == 'VIP' else '10%' if user_tier == 'Regular' else '0%')} discount on all messages

📈 **Your Statistics:**
• 💬 Total Messages: {user_stats.get('total_messages', 0)}
• 📅 Member Since: {user_stats.get('member_since', 'Recently').strftime('%B %Y') if user_stats.get('member_since') else 'Recently'}
• 🏆 Tier Level: {user_tier}

💸 **Current Message Costs:**
• Text: {database.apply_tier_discount(1, user_tier)} credits
• Photo: {database.apply_tier_discount(2, user_tier)} credits  
• Video: {database.apply_tier_discount(3, user_tier)} credits
• Document: {database.apply_tier_discount(2, user_tier)} credits

🎯 **Next Tier:** {EnhancedUserInterface._get_next_tier_info(user_credits, user_tier)}"""
        
        keyboard = UserMenuSystem.create_account_menu(user_id)
        
        await query.edit_message_text(account_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_user_settings(query, context) -> None:
        """Handle user settings menu"""
        user_id = query.from_user.id
        auto_recharge = database.get_user_auto_recharge_settings(user_id)
        auto_status = "✅ Enabled" if auto_recharge and auto_recharge.get('enabled') else "❌ Disabled"
        
        settings_msg = f"""⚙️ **Personal Settings**

🔄 **Auto-Recharge:** {auto_status}
{f"💰 Amount: {auto_recharge.get('amount', 10)} credits" if auto_recharge and auto_recharge.get('enabled') else ""}
{f"📊 Threshold: {auto_recharge.get('threshold', 5)} credits" if auto_recharge and auto_recharge.get('enabled') else ""}

🔔 **Notifications:** Enabled
🌍 **Language:** English
🔐 **Privacy:** Standard

**Customize your experience:**"""
        
        keyboard = UserMenuSystem.create_settings_menu(user_id)
        
        await query.edit_message_text(settings_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_content_store(query, context) -> None:
        """Handle content store display"""
        content_msg = """🔒 **Premium Content Store**

**Exclusive Content Available:**

🎯 **How to Access Premium Content:**
1. Browse available content with admins
2. Use `/buy_content <content_id>` to purchase
3. Enjoy instant access to premium material
4. Content is yours forever!

🏆 **VIP Members Get:**
• Exclusive content previews
• Special member pricing
• Early access to new content
• Premium support

💡 **Content Types:**
• 📚 Educational materials
• 🎥 Video tutorials
• 📄 Professional documents
• 🎨 Creative resources

**Ask our team about available content!**"""
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Ask About Content", callback_data="contact_support"),
                InlineKeyboardButton("🏆 VIP Benefits", callback_data="vip_benefits")
            ],
            [
                InlineKeyboardButton("💳 Get More Credits", callback_data="buy_menu"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        await query.edit_message_text(content_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_help_menu(query, context) -> None:
        """Handle help and FAQ menu"""
        user_id = query.from_user.id
        user_tier = database.get_user_tier(user_id)
        tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
        
        help_msg = f"""❓ **Help & Support Center**

{tier_emoji} **Your Status:** {user_tier} User

**🚀 Getting Started:**
• Use `/start` for the main menu
• Purchase credits to send messages
• Earn tier benefits through usage

**💬 How Messaging Works:**
• Send any message to contact our team
• Credits deducted based on message type
• Get professional responses quickly
• Continue conversations naturally

**🏆 Tier System:**
• 🆕 New (0-49 credits): Standard pricing
• ⭐ Regular (50-99 credits): 10% discount
• 🏆 VIP (100+ credits): 20% discount

**💳 Payment & Credits:**
• Secure payments via Stripe
• Instant credit delivery
• Auto-recharge available
• Multiple package sizes

**🔒 Premium Content:**
• Ask admins for content IDs
• Use `/buy_content <id>` to purchase
• Instant access after payment

**📞 Need More Help?**
Our team is ready to assist you personally!"""
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Contact Support", callback_data="contact_support"),
                InlineKeyboardButton("📚 Quick Tutorial", callback_data="tutorial")
            ],
            [
                InlineKeyboardButton("💳 Buy Credits", callback_data="buy_menu"),
                InlineKeyboardButton("📊 My Account", callback_data="check_balance")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        await query.edit_message_text(help_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_package_category(query, context) -> None:
        """Handle package category selection"""
        category = query.data.replace("category_", "")
        products = database.get_active_products()
        user_credits = database.get_user_credits_optimized(query.from_user.id)
        
        # Filter products by category
        if category == "starter":
            filtered_products = [p for p in products if p['amount'] <= 25]
            title = "🚀 **Starter Packages**"
            description = "Perfect for new users and light messaging"
        elif category == "regular":
            filtered_products = [p for p in products if 26 <= p['amount'] <= 100]
            title = "💼 **Regular Packages**"
            description = "Great value for regular users"
        elif category == "premium":
            filtered_products = [p for p in products if p['amount'] > 100]
            title = "🏆 **Premium Packages**"
            description = "Best value with bonus credits and VIP benefits"
        else:
            filtered_products = products
            title = "💳 **All Packages**"
            description = "Choose the perfect package for your needs"
        
        if not filtered_products:
            await query.edit_message_text("❌ No packages available in this category.")
            return
        
        # Build package display
        message = f"{title}\n\n{description}\n\n"
        keyboard = []
        
        for product in filtered_products:
            # Add package info
            bonus_text = ""
            if product['amount'] >= 100:
                bonus_text = " (VIP Tier!)"
            elif product['amount'] >= 50:
                bonus_text = " (Regular Tier!)"
            
            message += f"• **{product['label']}** - {product['amount']} credits{bonus_text}\n"
            message += f"  {product.get('description', 'Premium credit package')}\n\n"
            
            # Add buy button
            keyboard.append([InlineKeyboardButton(
                f"{product['label']} - {product['amount']} credits",
                callback_data=f"buy_{product['id']}"
            )])
        
        keyboard.append([
            InlineKeyboardButton("🔙 Back to Store", callback_data="buy_menu"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
        ])
        
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _handle_product_purchase(query, context) -> None:
        """Handle individual product purchase"""
        product_id = int(query.data.split("_")[1])
        product = next((p for p in database.get_active_products() if p['id'] == product_id), None)
        
        if not product:
            await query.edit_message_text("❌ This product is no longer available.")
            return
        
        user_id = query.from_user.id
        customer_id = stripe_utils.get_or_create_stripe_customer(user_id, query.from_user.username)
        
        if not customer_id:
            await query.edit_message_text("❌ Could not create customer profile. Please contact support.")
            return
        
        try:
            import stripe
            success_url = f"https://t.me/{context.bot.username}?start=success"
            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{'price': product['stripe_price_id'], 'quantity': 1}],
                mode='payment',
                success_url=success_url,
                cancel_url=f"https://t.me/{context.bot.username}?start=cancel",
                client_reference_id=str(user_id),
                metadata={
                    'telegram_user_id': str(user_id),
                    'product_id': product['id'],
                    'amount': product['amount'],
                    'item_type': product['item_type'],
                }
            )
            
            purchase_msg = f"""🛒 **Purchase Confirmation**

**Selected Package:** {product['label']}
**Credits:** {product['amount']}
**Description:** {product.get('description', 'Premium credit package')}

🔐 **Secure Payment:** Your payment is processed securely through Stripe

✨ **What happens next:**
1. Complete your payment securely
2. Credits added instantly to your account
3. Start messaging immediately!

**Ready to proceed?**"""
            
            keyboard = [
                [InlineKeyboardButton("💳 Proceed to Checkout", url=checkout_session.url)],
                [
                    InlineKeyboardButton("🔙 Back to Store", callback_data="buy_menu"),
                    InlineKeyboardButton("❌ Cancel", callback_data="back_to_start")
                ]
            ]
            
            await query.edit_message_text(purchase_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Stripe error for user {user_id}: {e}")
            await query.edit_message_text("❌ Payment system temporarily unavailable. Please try again later.")
    
    @staticmethod
    async def _handle_back_to_start(query, context) -> None:
        """Handle return to main menu"""
        # Create a fake update object to reuse the start command
        fake_update = Update(
            update_id=0,
            effective_user=query.from_user,
            effective_chat=query.message.chat if query.message else None,
            message=query.message
        )
        
        await EnhancedUserInterface.enhanced_start_command(fake_update, context)
    
    @staticmethod
    async def _handle_generic_callback(query, context) -> None:
        """Handle other callback queries"""
        callback_data = query.data
        
        if callback_data == "vip_benefits":
            await EnhancedUserInterface._show_vip_benefits(query, context)
        elif callback_data == "earn_credits":
            await EnhancedUserInterface._show_earn_credits(query, context)
        elif callback_data == "quick_recharge":
            await EnhancedUserInterface._show_quick_recharge(query, context)
        elif callback_data == "tutorial":
            await EnhancedUserInterface._show_detailed_tutorial(query, context)
        else:
            await query.edit_message_text("🔧 Feature coming soon! Stay tuned for updates.")
    
    # Helper methods
    @staticmethod
    def _get_package_recommendation(credits: int, tier: str) -> str:
        """Get personalized package recommendation"""
        if credits < 5:
            return "⚡ **Urgent:** Low balance! We recommend the **Basic Pack** to get started."
        elif tier == "New":
            return "🚀 **For New Users:** Try the **Premium Pack** to unlock Regular tier benefits!"
        elif tier == "Regular":
            return "⭐ **For Regular Users:** The **Power Pack** unlocks VIP status and 20% discounts!"
        else:
            return "🏆 **For VIP Users:** The **Mega Pack** offers the best value with maximum credits!"
    
    @staticmethod
    def _get_next_tier_info(credits: int, current_tier: str) -> str:
        """Get next tier progression info"""
        if current_tier == "New":
            needed = 50 - credits
            return f"⭐ Regular tier in {needed} more credits (10% discount)"
        elif current_tier == "Regular":
            needed = 100 - credits
            return f"🏆 VIP tier in {needed} more credits (20% discount)" 
        else:
            return "🏆 You've reached VIP status! Enjoy maximum benefits!"
    
    @staticmethod
    async def _show_vip_benefits(query, context) -> None:
        """Show VIP benefits information"""
        vip_msg = """🏆 **VIP Member Benefits**

**Messaging Discounts:**
• 20% off all message types
• Priority response from our team
• Extended conversation history

**Exclusive Access:**
• VIP-only premium content
• Early access to new features
• Special promotional offers

**Enhanced Support:**
• Priority customer service
• Dedicated VIP support channel
• Personal account manager

**Additional Perks:**
• Monthly bonus credits
• Exclusive community access
• Special event invitations

**How to Become VIP:**
Reach 100+ total credits purchased and you're automatically upgraded!"""
        
        keyboard = [
            [
                InlineKeyboardButton("💳 Get VIP Status", callback_data="buy_menu"),
                InlineKeyboardButton("💬 Contact VIP Support", callback_data="contact_support")
            ],
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        await query.edit_message_text(vip_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _show_earn_credits(query, context) -> None:
        """Show ways to earn free credits"""
        earn_msg = """🎁 **Earn Free Credits**

**Daily Opportunities:**
• 🔄 Daily check-in bonus (coming soon)
• 📝 Complete profile for 5 credits
• 🎯 First message bonus (already claimed!)

**Referral Program:**
• 👥 Invite friends and earn credits
• Get 10 credits per successful referral
• Your friends get bonus credits too!

**Special Events:**
• 🎉 Holiday promotions
• 🏆 User milestone celebrations
• 📢 Community challenges

**Loyalty Rewards:**
• 💎 Regular user bonuses
• 🎖️ Long-term member benefits
• ⭐ Activity-based rewards

**Ready to earn more?**"""
        
        keyboard = [
            [
                InlineKeyboardButton("👥 Invite Friends", callback_data="invite_friends"),
                InlineKeyboardButton("📝 Complete Profile", callback_data="complete_profile")
            ],
            [
                InlineKeyboardButton("💳 Buy Credits Instead", callback_data="buy_menu"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        await query.edit_message_text(earn_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _show_quick_recharge(query, context) -> None:
        """Show quick recharge options"""
        products = database.get_active_products()
        small_packages = [p for p in products if p['amount'] <= 50]
        
        recharge_msg = """⚡ **Quick Recharge**

**Low Balance Alert!** Get credits fast with these popular options:

"""
        
        keyboard = []
        
        for product in small_packages[:3]:  # Show top 3 small packages
            recharge_msg += f"• **{product['label']}** - {product['amount']} credits\n"
            keyboard.append([InlineKeyboardButton(
                f"⚡ {product['label']} - Quick Buy",
                callback_data=f"buy_{product['id']}"
            )])
        
        recharge_msg += "\n🔄 **Or set up auto-recharge** to never run out again!"
        
        keyboard.extend([
            [InlineKeyboardButton("🔄 Setup Auto-Recharge", callback_data="setup_autorecharge")],
            [
                InlineKeyboardButton("💳 View All Packages", callback_data="buy_menu"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ])
        
        await query.edit_message_text(recharge_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    @staticmethod
    async def _show_detailed_tutorial(query, context) -> None:
        """Show detailed tutorial"""
        tutorial_msg = """📖 **Complete User Guide**

**1. Understanding Credits** 💰
Credits are your currency for premium messaging:
• Each message type has a different cost
• Higher tiers get automatic discounts
• Credits never expire

**2. Tier System** 🏆
• 🆕 New (0-49): Standard pricing
• ⭐ Regular (50-99): 10% discount
• 🏆 VIP (100+): 20% discount + perks

**3. Messaging** 💬
• Type any message and send normally
• Credits deducted automatically
• Professional team responds quickly
• Continue conversations naturally

**4. Premium Content** 🔒
• Exclusive materials available
• Purchase with `/buy_content <id>`
• Ask our team for content catalog
• Instant access after purchase

**5. Account Management** ⚙️
• Monitor balance and usage
• Set up auto-recharge
• Track tier progress
• Customize preferences

**Ready to become a power user?**"""
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Try Messaging Now", callback_data="contact_support"),
                InlineKeyboardButton("💳 Get More Credits", callback_data="buy_menu")
            ],
            [
                InlineKeyboardButton("⚙️ Customize Settings", callback_data="user_settings"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
            ]
        ]
        
        await query.edit_message_text(tutorial_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')


def get_enhanced_user_handlers():
    """Get all enhanced user command handlers"""
    return [
        CommandHandler("start", EnhancedUserInterface.enhanced_start_command),
        CallbackQueryHandler(EnhancedUserInterface.enhanced_button_handler),
    ] 