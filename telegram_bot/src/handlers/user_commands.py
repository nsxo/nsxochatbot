#!/usr/bin/env python3
"""
User-facing command handlers for the Telegram bot.
"""

import logging
from typing import Dict, List
import stripe
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src import database, config, stripe_utils
from src.error_handler import rate_limit, monitor_performance

logger = logging.getLogger(__name__)

# Import buy_content function from admin_commands
from src.handlers.admin_commands import buy_content_command

# Helper functions (as they were, no changes needed)
def safe_reply(update, text, reply_markup=None, parse_mode='Markdown', **kwargs):
    if hasattr(update, 'message') and update.message:
        return update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode, **kwargs)
    elif hasattr(update, 'callback_query') and update.callback_query:
        if update.callback_query.message:
            return update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode, **kwargs)
    return None

def format_time_remaining(seconds: int) -> str:
    if seconds <= 0: return "No time remaining"
    days, r = divmod(seconds, 86400); hours, r = divmod(r, 3600); minutes, secs = divmod(r, 60)
    parts = [f"{d}d" for d in [days] if d] + [f"{h}h" for h in [hours] if h] + [f"{m}m" for m in [minutes] if m]
    return " ".join(parts) or f"{secs}s"

def format_balance_display(user_credits: int, max_credits: int = 100) -> str:
    if max_credits <= 0: max_credits = 100
    p = min(user_credits / max_credits, 1.0); filled = int(p * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled); emoji = "💰" if p > 0.7 else "💵" if p > 0.3 else "⚠️"
    return f"{emoji} *Balance: {user_credits} credits*\n{bar} {int(p*100)}%"

# ========================= FULLY RESTORED USER COMMANDS =========================

@rate_limit(max_calls=20, window_seconds=60)
@monitor_performance
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced start command with personalized welcome and feature showcase."""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name or "there"
    
    # Ensure user exists in database
    database.ensure_user_exists(user_id, username, update.effective_user.first_name)
    
    # Get user data
    user_credits = database.get_user_credits_optimized(user_id)
    user_tier = database.get_user_tier(user_id)
    products = database.get_active_products()
    
    # Check if it's a new user (first time using /start)
    user_stats = database.get_user_stats_individual(user_id)
    is_new_user = user_stats.get('total_messages', 0) == 0
    
    # Get tier emoji and benefits info
    tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
    tier_discount = "20%" if user_tier == "VIP" else "10%" if user_tier == "Regular" else "0%"
    
    # Create personalized welcome message
    if is_new_user:
        welcome_header = f"🎉 **Welcome to the Bot, @{username}!**\n\n"
        intro_text = (
            "✨ You've joined an **exclusive messaging service** where you can:\n\n"
            "💬 **Send Direct Messages** to our admin team\n"
            "🔒 **Access Premium Content** with our locked content system\n"
            "🎁 **Earn Tier Benefits** - get discounts as you use the service\n"
            "⚡ **Quick Responses** from our professional support team\n\n"
        )
    else:
        welcome_header = f"👋 **Welcome back, @{username}!**\n\n"
        intro_text = ""
    
    # Balance and tier status
    balance_display = format_balance_display(user_credits)
    tier_status = f"{tier_emoji} **{user_tier} User** • {tier_discount} discount on messages\n\n"
    
    # Feature highlights
    features_text = (
        "🌟 **What You Can Do:**\n"
        "• 💬 Send messages with credits (text, photos, videos, files)\n"
        "• 🔒 Purchase exclusive locked content with `/buy_content`\n"
        "• 📊 Check your balance and transaction history\n"
        "• ⚙️ Configure auto-recharge settings\n"
        "• 🎁 Receive gifts and tier benefits\n\n"
    )
    
    # Credit packages
    packages_text = "💳 **Credit Packages Available:**\n"
    for product in products[:3]:  # Show top 3 products
        packages_text += f"• **{product['label']}** - {product['amount']} credits\n"
    packages_text += "\n"
    
    # Special offers for new users
    special_offers = ""
    if is_new_user:
        special_offers = (
            "🎊 **New User Bonus!**\n"
            "Get started with your first message - we've added some welcome credits!\n\n"
        )
        # Give new user bonus credits
        bonus_credits = 5
        database.add_user_credits(user_id, bonus_credits)
        user_credits += bonus_credits
        balance_display = format_balance_display(user_credits)
    
    # Combine all parts
    full_message = (
        welcome_header +
        intro_text +
        balance_display + "\n" +
        tier_status +
        features_text +
        special_offers +
        packages_text +
        "Choose an option below to get started! 👇"
    )
    
    # Enhanced keyboard with more options
    keyboard = []
    
    # Credit packages (top 3)
    if products:
        keyboard.append([InlineKeyboardButton(f"💎 {products[0]['label']}", callback_data=f"buy_{products[0]['id']}")])
        if len(products) > 1:
            keyboard.append([InlineKeyboardButton(f"⭐ {products[1]['label']}", callback_data=f"buy_{products[1]['id']}")])
        if len(products) > 2:
            keyboard.append([InlineKeyboardButton(f"🏆 {products[2]['label']}", callback_data=f"buy_{products[2]['id']}")])
    
    # Action buttons row 1
    keyboard.append([
        InlineKeyboardButton("📊 Balance", callback_data="check_balance"),
        InlineKeyboardButton("🔒 Content Store", callback_data="content_store")
    ])
    
    # Action buttons row 2
    keyboard.append([
        InlineKeyboardButton("⚙️ Settings", callback_data="user_settings"),
        InlineKeyboardButton("ℹ️ Help", callback_data="help_menu")
    ])
    
    # Billing and support
    keyboard.append([InlineKeyboardButton("💳 Manage Billing", callback_data="billing")])
    
    if is_new_user:
        keyboard.append([InlineKeyboardButton("🚀 Quick Start Guide", callback_data="quick_start")])

    await safe_reply(update, full_message, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced button handler for all inline keyboard actions."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    callback_data = query.data

    if callback_data == "check_balance":
        user_credits = database.get_user_credits_optimized(user_id)
        user_tier = database.get_user_tier(user_id)
        tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
        
        # Enhanced balance display with transaction history
        balance_msg = f"""📊 **Account Balance**

{format_balance_display(user_credits)}

{tier_emoji} **Tier:** {user_tier} User
💰 **Benefits:** {('20%' if user_tier == 'VIP' else '10%' if user_tier == 'Regular' else '0%')} discount on messages

💸 **Message Costs:**
• Text: {database.get_setting('cost_text_message', '1')} credits
• Photo: {database.get_setting('cost_photo_message', '2')} credits  
• Video: {database.get_setting('cost_video_message', '3')} credits
• Document: {database.get_setting('cost_document_message', '2')} credits

Use /buy to purchase more credits!"""
        
        keyboard = [
            [InlineKeyboardButton("💳 Buy Credits", callback_data="buy_menu")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        await query.edit_message_text(balance_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif callback_data == "content_store":
        # Show available locked content
        await query.edit_message_text(
            "🔒 **Premium Content Store**\n\n"
            "Browse and purchase exclusive locked content!\n\n"
            "**How to purchase:**\n"
            "• Ask an admin for available content IDs\n"
            "• Use `/buy_content <content_id>` to purchase\n"
            "• Enjoy instant access to premium content!\n\n"
            "💡 *More content added regularly!*",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")
            ]]),
            parse_mode='Markdown'
        )
    
    elif callback_data == "user_settings":
        # User settings menu
        auto_recharge = database.get_user_auto_recharge_settings(user_id)
        status = "✅ Enabled" if auto_recharge and auto_recharge.get('enabled') else "❌ Disabled"
        
        settings_text = f"""⚙️ **User Settings**

🔄 **Auto-Recharge:** {status}
{f"💰 Amount: {auto_recharge.get('amount', 10)} credits" if auto_recharge and auto_recharge.get('enabled') else ""}
{f"📊 Threshold: {auto_recharge.get('threshold', 5)} credits" if auto_recharge and auto_recharge.get('enabled') else ""}

🔔 **Notifications:** Enabled
📱 **Language:** English

Configure your preferences below:"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Toggle Auto-Recharge", callback_data="toggle_autorecharge")],
            [InlineKeyboardButton("🔔 Notification Settings", callback_data="notification_settings")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        await query.edit_message_text(settings_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif callback_data == "help_menu":
        help_text = """ℹ️ **Help & Support**

**🚀 Getting Started:**
• Use /start to access the main menu
• Purchase credits to send messages
• Earn tier benefits as you use the service

**💬 Messaging:**
• Send any message to contact our team
• Different message types have different costs
• Get tier discounts automatically applied

**🔒 Premium Content:**
• Use `/buy_content <id>` to purchase locked content
• Ask admins for available content IDs
• Instant access after purchase

**💳 Billing:**
• Use /buy to purchase credit packages
• Secure payments via Stripe
• Auto-recharge available for convenience

**🎁 Tier System:**
• 🆕 New User: No discount
• ⭐ Regular (50+ credits): 10% discount
• 🏆 VIP (100+ credits): 20% discount

**📞 Support:**
Just send a message - our team will respond quickly!"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif callback_data == "quick_start":
        quick_start_text = """🚀 **Quick Start Guide**

**Step 1: Welcome Bonus** ✅
You've received 5 welcome credits!

**Step 2: Send Your First Message** 💬
Just type anything and send it - our team will respond!

**Step 3: Explore Features** 🌟
• Check the content store for premium content
• Configure auto-recharge in settings
• Monitor your tier progress

**Step 4: Get More Credits** 💳
When you need more credits, use the buy buttons!

**Step 5: Enjoy the Service** 🎉
Ask questions, request content, or just chat!

Ready to get started? Send your first message! 👇"""
        
        keyboard = [
            [InlineKeyboardButton("💳 Buy More Credits", callback_data="buy_menu")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        await query.edit_message_text(quick_start_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif callback_data == "buy_menu":
        products = database.get_active_products()
        if not products:
            await query.edit_message_text("❌ No products available at the moment.")
            return
        
        buy_text = "💳 **Purchase Credits**\n\nSelect a package below:\n\n"
        keyboard = []
        
        for product in products:
            buy_text += f"• **{product['label']}** - {product['amount']} credits\n"
            keyboard.append([InlineKeyboardButton(f"{product['label']}", callback_data=f"buy_{product['id']}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")])
        await query.edit_message_text(buy_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif callback_data == "back_to_start":
        # Return to start menu
        await start(update, context)
        return
    
    elif callback_data == "toggle_autorecharge":
        # Toggle auto-recharge setting
        current_settings = database.get_user_auto_recharge_settings(user_id)
        current_enabled = current_settings.get('enabled', False) if current_settings else False
        
        success = database.update_user_auto_recharge_settings(user_id, not current_enabled)
        
        if success:
            status = "enabled" if not current_enabled else "disabled"
            await query.edit_message_text(
                f"✅ Auto-recharge has been **{status}**!\n\n"
                f"You can adjust the amount and threshold by contacting support.\n\n"
                f"Return to settings to see updated status.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⚙️ Back to Settings", callback_data="user_settings")
                ]]),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text("❌ Failed to update auto-recharge settings.")
    
    elif callback_data == "contact_support":
        await query.edit_message_text(
            "💬 **Contact Support**\n\n"
            "Our support team is ready to help!\n\n"
            "Just send any message and we'll respond quickly. You can send:\n"
            "• Text messages\n"
            "• Photos with questions\n" 
            "• Videos or documents\n"
            "• Voice messages\n\n"
            "**Response time:** Usually within minutes!\n\n"
            "Go ahead and send your message now! 👇",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Help", callback_data="help_menu")
            ]]),
            parse_mode='Markdown'
        )
    
    elif callback_data == "billing":
        await billing_command(update, context)

    elif callback_data.startswith("buy_"):
        product_id = int(callback_data.split("_")[1])
        product = next((p for p in database.get_active_products() if p['id'] == product_id), None)
        if not product:
            await safe_reply(update, "❌ This product is no longer available.")
            return

        customer_id = stripe_utils.get_or_create_stripe_customer(user_id, query.from_user.username)
        if not customer_id:
            await safe_reply(update, "❌ Could not create a customer profile. Please contact support.")
            return

        try:
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
            keyboard = [[InlineKeyboardButton("Proceed to Checkout 💳", url=checkout_session.url)]]
            await safe_reply(update, f"🛒 You selected *{product['label']}*. Click below to complete your purchase.", reply_markup=InlineKeyboardMarkup(keyboard))
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error for user {user_id}: {e}")
            await safe_reply(update, "❌ An error occurred with our payment provider. Please try again later.")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced balance command with detailed account information."""
    user_id = update.effective_user.id
    user_credits = database.get_user_credits_optimized(user_id)
    user_tier = database.get_user_tier(user_id)
    user_stats = database.get_user_stats_individual(user_id)
    
    # Get tier info
    tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
    discount = "20%" if user_tier == "VIP" else "10%" if user_tier == "Regular" else "0%"
    
    # Calculate credits to next tier
    next_tier_info = ""
    if user_tier == "New":
        credits_needed = 50 - user_credits
        next_tier_info = f"📈 {credits_needed} credits to ⭐ Regular tier"
    elif user_tier == "Regular":
        credits_needed = 100 - user_credits
        next_tier_info = f"📈 {credits_needed} credits to 🏆 VIP tier"
    else:
        next_tier_info = "🏆 Maximum tier achieved!"
    
    # Auto-recharge status
    auto_recharge = database.get_user_auto_recharge_settings(user_id)
    auto_status = "✅ Enabled" if auto_recharge and auto_recharge.get('enabled') else "❌ Disabled"
    
    balance_text = f"""📊 **Account Balance**

{format_balance_display(user_credits)}

{tier_emoji} **Current Tier:** {user_tier}
💰 **Your Discount:** {discount} on all messages
{next_tier_info}

🔄 **Auto-Recharge:** {auto_status}
📩 **Messages Sent:** {user_stats.get('total_messages', 0)}
📅 **Member Since:** {user_stats.get('member_since', 'Recently').strftime('%B %Y') if user_stats.get('member_since') else 'Recently'}

💸 **Current Message Costs (after discount):**"""
    
    # Calculate discounted costs
    base_costs = {
        'Text': int(database.get_setting('cost_text_message', '1')),
        'Photo': int(database.get_setting('cost_photo_message', '2')),
        'Video': int(database.get_setting('cost_video_message', '3')),
        'Document': int(database.get_setting('cost_document_message', '2'))
    }
    
    for msg_type, base_cost in base_costs.items():
        discounted_cost = database.apply_tier_discount(base_cost, user_tier)
        if discounted_cost < base_cost:
            balance_text += f"\n• {msg_type}: {discounted_cost} credits (~~{base_cost}~~)"
        else:
            balance_text += f"\n• {msg_type}: {discounted_cost} credits"
    
    keyboard = [
        [InlineKeyboardButton("💳 Buy Credits", callback_data="buy_menu")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="user_settings")],
        [InlineKeyboardButton("🚀 Main Menu", callback_data="back_to_start")]
    ]
    
    await safe_reply(update, balance_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced help command with comprehensive information."""
    user_id = update.effective_user.id
    user_tier = database.get_user_tier(user_id)
    tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
    
    help_text = f"""ℹ️ **Help & Command Guide**

**🚀 Main Commands:**
• `/start` - Access the main menu and features
• `/balance` - Check your credit balance and tier status  
• `/buy` - Purchase credit packages
• `/help` - Show this help message
• `/buy_content <id>` - Purchase locked premium content

**💬 How Messaging Works:**
• Send any message to contact our support team
• Messages cost credits based on type:
  - Text: {database.get_setting('cost_text_message', '1')} credits
  - Photo: {database.get_setting('cost_photo_message', '2')} credits
  - Video: {database.get_setting('cost_video_message', '3')} credits
  - Documents: {database.get_setting('cost_document_message', '2')} credits

**🎁 Your Status:**
{tier_emoji} **Tier:** {user_tier} User
💰 **Discount:** {('20%' if user_tier == 'VIP' else '10%' if user_tier == 'Regular' else '0%')} on all messages

**🏆 Tier Benefits:**
• 🆕 New User (0-49 credits): Standard pricing
• ⭐ Regular User (50-99 credits): 10% discount
• 🏆 VIP User (100+ credits): 20% discount

**🔒 Premium Content:**
• Ask admins for available content IDs
• Use `/buy_content <id>` to purchase
• Instant access after payment

**⚙️ Features:**
• Auto-recharge: Never run out of credits
• Secure payments via Stripe
• Professional support team
• Multiple message type support

**📞 Need Help?**
Just send a message - our team responds quickly!

Use `/start` to return to the main menu."""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Main Menu", callback_data="back_to_start")],
        [InlineKeyboardButton("💬 Contact Support", callback_data="contact_support")]
    ]
    
    await safe_reply(update, help_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Alias for /start."""
    await start(update, context)

async def billing_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provides a link to the Stripe billing portal to manage payment methods."""
    customer_id = stripe_utils.get_or_create_stripe_customer(update.effective_user.id, update.effective_user.username)
    if not customer_id:
        await safe_reply(update, "❌ Could not retrieve your customer profile.")
        return
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"https://t.me/{context.bot.username}?start=billing_return",
        )
        keyboard = [[InlineKeyboardButton("💳 Manage Payment Methods", url=portal_session.url)]]
        await safe_reply(update, "Click below to manage your payment methods and view past invoices.", reply_markup=InlineKeyboardMarkup(keyboard))
    except stripe.error.StripeError as e:
        logger.error(f"Billing portal error for user {update.effective_user.id}: {e}")
        await safe_reply(update, "❌ Could not open the billing portal. Please try again later.") 