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
    """Handles the /start command, displaying a welcome message and available products."""
    user_id = update.effective_user.id
    # database.sync_user_username(...) can be re-added here if needed
    
    welcome_message = database.get_setting('welcome_message', "Welcome to the bot!")
    user_credits = database.get_user_credits_optimized(user_id)
    products = database.get_active_products()

    message = f"{welcome_message}\n\nYour current balance is *{user_credits} credits*."
    
    keyboard = [[InlineKeyboardButton(p['label'], callback_data=f"buy_{p['id']}")] for p in products]
    keyboard.append([InlineKeyboardButton("💳 Manage Billing", callback_data="billing")])
    keyboard.append([InlineKeyboardButton("📊 Check Balance", callback_data="check_balance")])

    await safe_reply(update, message, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all button presses from inline keyboards."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    callback_data = query.data

    if callback_data == "check_balance":
        user_credits = database.get_user_credits_optimized(user_id)
        balance_msg = format_balance_display(user_credits)
        await safe_reply(update, balance_msg)
    
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
    """Shows the user's current credit balance."""
    user_credits = database.get_user_credits_optimized(update.effective_user.id)
    await safe_reply(update, format_balance_display(user_credits))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a helpful message."""
    help_text = "Here are the available commands:\n\n/start - Main menu\n/balance - Check your credits\n/help - This message"
    await safe_reply(update, help_text)

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