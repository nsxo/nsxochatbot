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
    """Enhanced start command with rich welcome experience including image and professional messaging."""
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
    
    # Create welcome image message for new users
    if is_new_user:
        # Send welcome image first (using a professional welcome image)
        # You can replace this with your own custom image URL
        welcome_image_url = "https://images.unsplash.com/photo-1557804506-669a67965ba0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=400&q=80"
        
        try:
            # Send welcome image with caption
            await update.message.reply_photo(
                photo=welcome_image_url,
                caption=f"""🎉 **Welcome to the Premium Messaging Experience!**

Hi @{username}! You've just joined an exclusive service where you can directly communicate with our team through a professional credit-based system.

✨ **What makes us special:**
• Direct access to real human support
• Professional response times
• Secure payment processing
• Tier-based benefits and discounts

🎁 **New User Bonus:** We've added 5 welcome credits to get you started!

Ready to explore? Tap the button below! 👇""",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"Could not send welcome image: {e}")
            # Fallback to text-only welcome for new users
            pass
    
    # Create personalized welcome message
    if is_new_user:
        welcome_header = f"🚀 **Get Started, @{username}!**\n\n"
        intro_text = (
            "Welcome to your **Premium Messaging Dashboard**! Here's everything you need to know:\n\n"
            "💬 **Send Messages**: Each message costs credits based on type\n"
            "🎯 **Get Responses**: Our team provides professional, timely replies\n" 
            "🏆 **Earn Benefits**: Use more → get better tier → save money\n"
            "🔒 **Premium Content**: Access exclusive locked content\n\n"
        )
        
        # Give new user bonus credits
        bonus_credits = 5
        database.add_user_credits(user_id, bonus_credits)
        user_credits += bonus_credits
        
    else:
        welcome_header = f"👋 **Welcome back, @{username}!**\n\n"
        intro_text = ""
    
    # Balance and tier status with enhanced formatting
    balance_display = format_balance_display(user_credits)
    tier_status = f"{tier_emoji} **{user_tier} User** • {tier_discount} discount on all messages\n\n"
    
    # Enhanced features section
    features_text = (
        "🌟 **Quick Actions:**\n"
        "• 📊 Check your account balance and tier progress\n"
        "• 💳 Purchase credit packages (secure Stripe payments)\n"
        "• 🔒 Browse our exclusive content store\n"
        "• ⚙️ Configure auto-recharge and preferences\n"
        "• 📞 Get instant help and support\n\n"
    )
    
    # Credit packages preview - show top 3 most popular
    packages_text = ""
    if products:
        packages_text = "💎 **Popular Packages:**\n"
        for i, product in enumerate(products[:3]):
            emoji = "🚀" if i == 0 else "⭐" if i == 1 else "🏆"
            packages_text += f"• {emoji} **{product['label']}** - {product['amount']} credits\n"
        packages_text += "\n"
    
    # Special messaging for new users
    special_section = ""
    if is_new_user:
        special_section = (
            "🎊 **You're All Set!**\n"
            f"Your welcome bonus of {bonus_credits} credits has been added to your account. "
            "Start by sending a message or exploring our features below!\n\n"
        )
    
    # Call-to-action
    cta_text = "👇 **Choose what you'd like to do:**"
    
    # Combine all parts for the main message
    full_message = (
        welcome_header +
        intro_text +
        balance_display + "\n" +
        tier_status +
        features_text +
        packages_text +
        special_section +
        cta_text
    )
    
    # Enhanced keyboard with better organization
    keyboard = []
    
    # New user gets a special "Get Started" button
    if is_new_user:
        keyboard.append([InlineKeyboardButton("🚀 Get Started - Send First Message!", callback_data="quick_start")])
        keyboard.append([InlineKeyboardButton("📖 Quick Tutorial", callback_data="tutorial")])
    
    # Credit packages (top 3) - more prominent for new users
    if products:
        if is_new_user:
            keyboard.append([InlineKeyboardButton(f"💎 {products[0]['label']} (Most Popular)", callback_data=f"buy_{products[0]['id']}")])
            if len(products) > 1:
                keyboard.append([InlineKeyboardButton(f"⭐ {products[1]['label']}", callback_data=f"buy_{products[1]['id']}")])
        else:
            # Regular users get a condensed view
            keyboard.append([InlineKeyboardButton(f"💎 {products[0]['label']}", callback_data=f"buy_{products[0]['id']}")])
            if len(products) > 1:
                keyboard.append([InlineKeyboardButton(f"⭐ {products[1]['label']}", callback_data=f"buy_{products[1]['id']}")])
    
    # Main action buttons - organized by importance
    keyboard.append([
        InlineKeyboardButton("📊 My Account", callback_data="check_balance"),
        InlineKeyboardButton("💳 Buy Credits", callback_data="buy_menu")
    ])
    
    keyboard.append([
        InlineKeyboardButton("🔒 Content Store", callback_data="content_store"),
        InlineKeyboardButton("⚙️ Settings", callback_data="user_settings")
    ])
    
    # Support and help
    keyboard.append([
        InlineKeyboardButton("📞 Contact Support", callback_data="contact_support"),
        InlineKeyboardButton("ℹ️ Help & FAQ", callback_data="help_menu")
    ])
    
    # Special buttons for new users
    if is_new_user:
        keyboard.append([InlineKeyboardButton("🎁 New User Benefits", callback_data="new_user_benefits")])

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
    
    elif callback_data == "back_to_buy":
        # Return to buy menu
        await buy_command(update, context)
        return
    
    elif callback_data.startswith("category_"):
        # Handle package categories
        category = callback_data.split("_")[1]
        await handle_package_category(update, context, category)
        return
    
    elif callback_data == "quick_buy_menu":
        await show_quick_buy_menu(update, context)
        return
    
    elif callback_data == "special_offers":
        await show_special_offers(update, context)
        return
    
    elif callback_data == "compare_plans":
        await show_compare_plans(update, context)
        return
    
    elif callback_data == "value_calculator":
        await show_value_calculator(update, context)
        return
    
    elif callback_data == "help_choose":
        await show_package_advisor(update, context)
        return
    
    elif callback_data == "setup_autorecharge":
        await show_autorecharge_setup(update, context)
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
        support_text = """📞 **Contact Our Support Team**

Ready to send your first message? Just type anything below and send it!

**What happens next:**
1. Your message goes directly to our support team
2. Credits are deducted based on message type
3. You'll receive a professional response
4. Continue the conversation naturally

**Example messages you could send:**
• "Hi! I'm new here and have a question about..."
• "Can you help me understand how this works?"
• "What services do you offer?"
• "I'd like to know more about your premium content"

**Message Costs:**
• Text: 1 credit
• Photo: 2 credits
• Video: 3 credits  
• Document: 2 credits

💡 **Tip:** Your current tier gets you {('20%' if database.get_user_tier(user_id) == 'VIP' else '10%' if database.get_user_tier(user_id) == 'Regular' else '0%')} discount!

Go ahead - type your message below! 👇"""
        
        keyboard = [
            [InlineKeyboardButton("💳 Need More Credits?", callback_data="buy_menu")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        await query.edit_message_text(support_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif callback_data == "new_user_benefits":
        benefits_text = """🎁 **New User Benefits & Rewards**

Welcome to our premium messaging service! As a new user, you get exclusive benefits:

**🎉 Immediate Benefits:**
• ✅ 5 welcome credits (already added!)
• ✅ Priority support responses
• ✅ Access to new user tutorials
• ✅ Special onboarding assistance

**🚀 Getting Started Bonus:**
• Your first message gets extra attention
• Detailed explanation of all features
• Personalized service recommendations
• Help setting up your preferences

**📈 Growth Path:**
• Send 50+ credits worth → ⭐ Regular tier (10% discount)
• Send 100+ credits worth → 🏆 VIP tier (20% discount)
• Lifetime tier status once achieved
• Compounding savings over time

**💎 Exclusive Access:**
• First look at new premium content
• Early access to special promotions
• Invitations to exclusive events
• Personalized service offerings

**🎯 Your Next Steps:**
1. Send your first message (use your 5 free credits!)
2. Explore our content store
3. Consider a starter package for ongoing use
4. Set up auto-recharge for convenience

Ready to begin your premium experience? 🌟"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Send First Message", callback_data="contact_support")],
            [InlineKeyboardButton("🔒 Explore Content Store", callback_data="content_store")],
            [InlineKeyboardButton("💳 View Credit Packages", callback_data="buy_menu")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        await query.edit_message_text(benefits_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    elif callback_data == "tutorial":
        tutorial_text = """📖 **Quick Tutorial - How It Works**

**Step 1: Understanding Credits** 💰
• Credits are used to send messages to our team
• Different message types cost different amounts:
  - Text messages: 1 credit
  - Photos: 2 credits  
  - Videos: 3 credits
  - Documents: 2 credits

**Step 2: Sending Messages** 💬
• Just type and send any message normally
• Credits are automatically deducted
• Your message goes directly to our support team
• You'll get a professional response quickly

**Step 3: Getting More Credits** 💳
• Use the "Buy Credits" button for secure payment
• Choose from various package sizes
• Instant credit addition after payment
• Set up auto-recharge to never run out

**Step 4: Tier Benefits** 🏆
• Use more credits → unlock higher tiers
• ⭐ Regular tier (50+ credits): 10% discount
• 🏆 VIP tier (100+ credits): 20% discount
• Automatic discounts applied to all messages

**Step 5: Premium Features** 🌟
• Access exclusive locked content
• Configure personalized settings
• Track your usage and spending
• Get priority support as a higher tier user

Ready to start? Send your first message! 👇"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Send First Message", callback_data="contact_support")],
            [InlineKeyboardButton("💳 Buy Credits", callback_data="buy_menu")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
        ]
        await query.edit_message_text(tutorial_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
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
    """Enhanced buy command with comprehensive credit store and recommendations."""
    user_id = update.effective_user.id
    user_credits = database.get_user_credits_optimized(user_id)
    user_tier = database.get_user_tier(user_id)
    products = database.get_active_products()
    
    if not products:
        await safe_reply(update, "❌ No credit packages are available at the moment. Please contact support.")
        return
    
    # Get tier info for recommendations
    tier_emoji = "🏆" if user_tier == "VIP" else "⭐" if user_tier == "Regular" else "🆕"
    
    # Package recommendations based on current credits and usage
    recommendation = get_package_recommendation(user_credits, user_tier)
    
    # Enhanced header
    header = f"""💳 **Credit Store**

{format_balance_display(user_credits)}
{tier_emoji} **Current Tier:** {user_tier}

{recommendation}

🛒 **Available Packages:**"""
    
    # Create enhanced keyboard with package categories
    keyboard = []
    
    # Organize products by size
    starter_products = [p for p in products if p['amount'] <= 25]
    regular_products = [p for p in products if 26 <= p['amount'] <= 100]
    premium_products = [p for p in products if p['amount'] > 100]
    
    # Add starter packages
    if starter_products:
        keyboard.append([InlineKeyboardButton("🚀 Starter Packages", callback_data="category_starter")])
    
    # Add regular packages  
    if regular_products:
        keyboard.append([InlineKeyboardButton("💼 Regular Packages", callback_data="category_regular")])
    
    # Add premium packages
    if premium_products:
        keyboard.append([InlineKeyboardButton("🏆 Premium Packages", callback_data="category_premium")])
    
    # Quick buy buttons for popular packages
    keyboard.append([InlineKeyboardButton("⚡ Quick Buy", callback_data="quick_buy_menu")])
    
    # Special offers and bundles
    keyboard.append([
        InlineKeyboardButton("🎁 Special Offers", callback_data="special_offers"),
        InlineKeyboardButton("📊 Compare Plans", callback_data="compare_plans")
    ])
    
    # Utility buttons
    keyboard.append([
        InlineKeyboardButton("💰 Value Calculator", callback_data="value_calculator"),
        InlineKeyboardButton("❓ Help Me Choose", callback_data="help_choose")
    ])
    
    # Navigation
    keyboard.append([
        InlineKeyboardButton("⚙️ Auto-Recharge", callback_data="setup_autorecharge"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")
    ])
    
    await safe_reply(update, header, reply_markup=InlineKeyboardMarkup(keyboard))

def get_package_recommendation(user_credits: int, user_tier: str) -> str:
    """Get personalized package recommendation based on user profile."""
    if user_credits <= 5:
        return "🔥 **Recommended:** Start with our Basic Pack to get messaging!"
    elif user_credits <= 15:
        return "💡 **Recommended:** Premium Pack gives you the best value!"
    elif user_credits <= 30:
        return "⭐ **Recommended:** Power Pack - perfect for regular users!"
    elif user_tier == "VIP":
        return "🏆 **VIP Status:** Consider our Enterprise Pack for maximum value!"
    else:
        return "🌟 **Popular Choice:** Most users love our Premium Pack!"

async def handle_package_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Handle package category selection."""
    query = update.callback_query
    await query.answer()
    
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
        # Calculate value proposition
        value_text = get_value_text(product['amount'])
        
        # Create package display
        package_text = f"**{product['label']}**\n{product['description']}\n{value_text}"
        message += f"• {package_text}\n\n"
        
        # Add buy button
        keyboard.append([InlineKeyboardButton(
            f"{product['label']} - {product['amount']} credits",
            callback_data=f"buy_{product['id']}"
        )])
    
    # Add navigation
    keyboard.append([
        InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_start")
    ])
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

def get_value_text(credits: int) -> str:
    """Get value proposition text for credit amount."""
    if credits >= 500:
        return "🌟 40% bonus • Enterprise support • Priority processing"
    elif credits >= 200:
        return "💎 25% bonus credits • VIP status • Premium support"
    elif credits >= 100:
        return "🏆 Best value • Reach VIP tier • 20% message discount"
    elif credits >= 50:
        return "⭐ Great value • Reach Regular tier • 10% discount"
    elif credits >= 25:
        return "💼 Good value • Perfect for regular users"
    else:
        return "🚀 Perfect starter amount"

async def show_quick_buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show quick buy menu with most popular packages."""
    query = update.callback_query
    await query.answer()
    
    products = database.get_active_products()
    user_tier = database.get_user_tier(query.from_user.id)
    
    # Select most popular packages
    popular_packages = []
    for amount in [25, 50, 100]:
        package = next((p for p in products if p['amount'] == amount), None)
        if package:
            popular_packages.append(package)
    
    message = """⚡ **Quick Buy - Popular Packages**

Most chosen by our users:

"""
    
    keyboard = []
    for i, product in enumerate(popular_packages):
        # Add popularity indicator
        popularity = ["🥉 Bronze Choice", "🥈 Silver Choice", "🥇 Gold Choice"][i] if i < 3 else "⭐ Popular"
        message += f"**{product['label']}** - {popularity}\n{product['description']}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"⚡ {product['label']} - ${product['amount']//10}.{product['amount']%10}0",
            callback_data=f"buy_{product['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy")])
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_special_offers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show special offers and promotions."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_stats = database.get_user_stats_individual(user_id)
    is_new_user = user_stats.get('total_messages', 0) < 5
    
    offers_text = "🎁 **Special Offers**\n\n"
    keyboard = []
    
    if is_new_user:
        offers_text += """🌟 **New User Special!**
• 50% bonus on your first Premium Pack purchase
• Instant VIP tier upgrade
• Priority support access

"""
        keyboard.append([InlineKeyboardButton("🌟 Claim New User Bonus", callback_data="new_user_bonus")])
    
    offers_text += """🔥 **Limited Time Offers:**

💎 **Bundle Deal:** Buy 2 Premium Packs, get 1 Basic Pack FREE!
🏆 **VIP Fast Track:** Power Pack + instant VIP tier upgrade
⚡ **Flash Sale:** 25% extra credits on Mega Pack
🎯 **Loyalty Bonus:** 15% more credits for returning customers

💰 **Best Value Guarantee:**
If you find a better deal, we'll match it plus 10% extra!

"""
    
    keyboard.extend([
        [InlineKeyboardButton("💎 Bundle Deal", callback_data="bundle_deal")],
        [InlineKeyboardButton("🏆 VIP Fast Track", callback_data="vip_fasttrack")],
        [InlineKeyboardButton("⚡ Flash Sale", callback_data="flash_sale")],
        [InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy")]
    ])
    
    await query.edit_message_text(offers_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_compare_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed plan comparison."""
    query = update.callback_query
    await query.answer()
    
    compare_text = """📊 **Package Comparison**

**🚀 Starter Pack (10 credits)**
• Perfect for: First-time users
• Message capacity: ~10 messages
• Best for: Testing the service
• Value: Basic

**💼 Basic Pack (25 credits)**
• Perfect for: Light users
• Message capacity: ~25 messages  
• Best for: Occasional messaging
• Value: Good • 2.5x starter value

**⭐ Premium Pack (50 credits)**
• Perfect for: Regular users
• Message capacity: ~50 messages
• Best for: Daily communication
• Value: Great • Tier progression

**🏆 Power Pack (100 credits)**
• Perfect for: Heavy users
• Message capacity: ~100 messages
• Best for: VIP tier unlock
• Value: Excellent • 20% discounts

**💎 Mega Pack (200 credits)**
• Perfect for: Power users
• Message capacity: ~250 messages
• Best for: Bulk messaging
• Value: Outstanding • 25% bonus

**🌟 Enterprise (500 credits)**
• Perfect for: Business users
• Message capacity: ~700 messages
• Best for: Professional use
• Value: Premium • 40% bonus

💡 **Recommendation:** Start with Premium Pack for best balance of value and features!"""
    
    keyboard = [
        [InlineKeyboardButton("💡 Get Recommendation", callback_data="help_choose")],
        [InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy")]
    ]
    
    await query.edit_message_text(compare_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_value_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show value calculator to help users choose packages."""
    query = update.callback_query
    await query.answer()
    
    calculator_text = """💰 **Value Calculator**

**How much do you message?**

📱 **Light User (1-2 messages/day)**
• Monthly need: ~30-60 credits
• Recommended: Basic or Premium Pack
• Best value: Premium Pack (lasts longer)

💬 **Regular User (3-5 messages/day)**
• Monthly need: ~90-150 credits  
• Recommended: Premium or Power Pack
• Best value: Power Pack (VIP benefits)

🔥 **Heavy User (6+ messages/day)**
• Monthly need: 180+ credits
• Recommended: Mega or Enterprise Pack
• Best value: Enterprise Pack (40% bonus)

💼 **Business User (Professional)**
• Monthly need: 300+ credits
• Recommended: Enterprise Pack
• Best value: Enterprise (priority support)

**💡 Pro Tips:**
• VIP tier (100+ credits) = 20% discount on all messages
• Regular tier (50+ credits) = 10% discount
• Larger packages = better value per credit
• Auto-recharge = never run out of credits

**Calculate Your Savings:**
VIP users save ~2 credits per 10 messages
That's 20% more messaging for the same price!"""
    
    keyboard = [
        [InlineKeyboardButton("💡 Get Personal Recommendation", callback_data="help_choose")],
        [InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy")]
    ]
    
    await query.edit_message_text(calculator_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_package_advisor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show personalized package advisor."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_credits = database.get_user_credits_optimized(user_id)
    user_tier = database.get_user_tier(user_id)
    user_stats = database.get_user_stats_individual(user_id)
    
    # Analyze user profile
    total_messages = user_stats.get('total_messages', 0)
    is_new_user = total_messages < 5
    
    advisor_text = f"""🤖 **Personal Package Advisor**

**Your Profile Analysis:**
• Current Credits: {user_credits}
• Current Tier: {user_tier}
• Messages Sent: {total_messages}
• Usage Pattern: {"New User" if is_new_user else "Regular User"}

"""
    
    # Generate personalized recommendation
    if is_new_user:
        advisor_text += """🌟 **New User Recommendation:**

Since you're new to our service, I recommend starting with the **Premium Pack (50 credits)**:

✅ **Why Premium Pack?**
• Perfect amount to try all features
• Reaches Regular tier (10% discount)
• Great value for money
• Lasts 2-3 weeks for most users

🎁 **Bonus:** New users get extra support and priority responses!"""
        
        recommended_product = next((p for p in database.get_active_products() if p['amount'] == 50), None)
        
    elif user_tier == "New" and user_credits < 30:
        advisor_text += """📈 **Tier Upgrade Recommendation:**

You're close to Regular tier! I recommend the **Power Pack (100 credits)**:

✅ **Why Power Pack?**
• Instant VIP tier upgrade (20% discount)
• Best long-term value
• Never worry about running out
• Premium support included

💰 **Value:** 20% discount means 120 effective messages for 100 credits!"""
        
        recommended_product = next((p for p in database.get_active_products() if p['amount'] == 100), None)
        
    elif user_tier == "VIP":
        advisor_text += """🏆 **VIP User Recommendation:**

As a VIP user, maximize your benefits with the **Enterprise Pack (500 credits)**:

✅ **Why Enterprise Pack?**
• 40% bonus credits (700 effective credits)
• Priority processing
• Enterprise support
• Best value per credit

💎 **VIP Exclusive:** Enterprise users get access to premium features!"""
        
        recommended_product = next((p for p in database.get_active_products() if p['amount'] == 500), None)
        
    else:
        advisor_text += """⭐ **Balanced Recommendation:**

Based on your usage, the **Premium Pack (50 credits)** is perfect:

✅ **Why Premium Pack?**
• Most popular choice
• Good for regular messaging
• Maintains your tier status
• Excellent value proposition

💡 **Alternative:** Consider Power Pack if you message frequently!"""
        
        recommended_product = next((p for p in database.get_active_products() if p['amount'] == 50), None)
    
    keyboard = []
    if recommended_product:
        keyboard.append([InlineKeyboardButton(
            f"✅ Buy {recommended_product['label']} (Recommended)",
            callback_data=f"buy_{recommended_product['id']}"
        )])
    
    keyboard.extend([
        [InlineKeyboardButton("📊 Compare All Plans", callback_data="compare_plans")],
        [InlineKeyboardButton("💰 Value Calculator", callback_data="value_calculator")],
        [InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy")]
    ])
    
    await query.edit_message_text(advisor_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def show_autorecharge_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show auto-recharge setup options."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    current_settings = database.get_user_auto_recharge_settings(user_id)
    is_enabled = current_settings.get('enabled', False) if current_settings else False
    
    setup_text = f"""⚙️ **Auto-Recharge Setup**

Never run out of credits again! Auto-recharge automatically buys more credits when you're running low.

**Current Status:** {"✅ Enabled" if is_enabled else "❌ Disabled"}

"""
    
    if is_enabled:
        amount = current_settings.get('amount', 10)
        threshold = current_settings.get('threshold', 5)
        setup_text += f"""**Your Settings:**
• Recharge Amount: {amount} credits
• Trigger When: Balance drops to {threshold} credits
• Payment Method: Your saved card

🔄 **How it works:**
1. Your balance drops to {threshold} credits
2. We automatically charge your card
3. {amount} credits added instantly
4. You keep messaging without interruption!"""
        
        keyboard = [
            [InlineKeyboardButton("❌ Disable Auto-Recharge", callback_data="toggle_autorecharge")],
            [InlineKeyboardButton("⚙️ Modify Settings", callback_data="modify_autorecharge")],
            [InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy")]
        ]
    else:
        setup_text += """🌟 **Benefits of Auto-Recharge:**
• Never miss important conversations
• Automatic credit top-ups
• Secure payment processing
• Customizable amounts and thresholds
• Cancel anytime

**Recommended Settings:**
• Recharge: 50 credits (Premium Pack)
• Trigger: When balance drops to 5 credits
• Perfect for regular users!

⚡ **Quick Setup Options:**"""
        
        keyboard = [
            [InlineKeyboardButton("⚡ Quick Setup (50 credits @ 5)", callback_data="autorecharge_quick")],
            [InlineKeyboardButton("💼 Basic Setup (25 credits @ 3)", callback_data="autorecharge_basic")],
            [InlineKeyboardButton("🏆 VIP Setup (100 credits @ 10)", callback_data="autorecharge_vip")],
            [InlineKeyboardButton("⚙️ Custom Setup", callback_data="autorecharge_custom")],
            [InlineKeyboardButton("🔙 Back to Store", callback_data="back_to_buy")]
        ]
    
    await query.edit_message_text(setup_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

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