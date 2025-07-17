#!/usr/bin/env python3
"""
Stripe integration utilities for the Telegram bot.
"""

import logging
import stripe
from telegram import Update

from src import database
from src.config import settings

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_API_KEY

def get_or_create_stripe_customer(user_id: int, username: str = None) -> str:
    """Get or create a Stripe customer for the user."""
    customer_id = database.get_stripe_customer_id(user_id)
    if customer_id:
        return customer_id

    try:
        customer = stripe.Customer.create(
            metadata={'telegram_id': str(user_id)},
            description=f"Telegram user {username or user_id}"
        )
        database.set_stripe_customer_id(user_id, customer.id)
        return customer.id
    except stripe.error.StripeError as e:
        logger.error(f"Error creating Stripe customer: {e}")
        return None

async def process_stripe_webhook(payload: str, signature: str) -> bool:
    """Process incoming Stripe webhook."""
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=signature, secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"Invalid Stripe webhook signature: {e}")
        return False

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session.get('client_reference_id'))
        metadata = session.get('metadata', {})
        amount = int(metadata.get('amount', 0))
        item_type = metadata.get('item_type', 'message')

        if user_id and amount > 0:
            database.add_user_credits(user_id, amount, item_type)
            logger.info(f"Processed successful payment for user {user_id}. Added {amount} {item_type} credits.")
        else:
            logger.warning(f"Could not process payment from webhook: missing user_id or amount. Session: {session}")


    return True 