#!/usr/bin/env python3
"""
Enhanced Stripe webhook handler supporting multiple webhook events.
Provides comprehensive payment processing, failure handling, and business protection.
"""

import os
import logging
from flask import Flask, request, jsonify
import stripe
from dotenv import load_dotenv
import psycopg2
from datetime import datetime
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
DATABASE_URL = os.getenv('DATABASE_URL')
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '0'))
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8000'))

# Configure Stripe
stripe.api_key = STRIPE_API_KEY

# Initialize Flask app
app = Flask(__name__)

def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(DATABASE_URL)

def get_user_by_customer_id(customer_id: str) -> Optional[int]:
    """Get user ID from Stripe customer ID."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT telegram_id FROM users WHERE stripe_customer_id = %s",
                (customer_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    finally:
        conn.close()

def add_user_credits(user_id: int, credits: int, credit_type: str = 'message') -> None:
    """Add credits to a user's account after successful payment."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if credit_type == 'message':
                cursor.execute(
                    """
                    INSERT INTO users (telegram_id, message_credits)
                    VALUES (%s, %s)
                    ON CONFLICT (telegram_id)
                    DO UPDATE SET message_credits = users.message_credits + EXCLUDED.message_credits
                    """,
                    (user_id, credits)
                )
            else:  # time credits
                cursor.execute(
                    """
                    INSERT INTO users (telegram_id, time_credits_seconds)
                    VALUES (%s, %s)
                    ON CONFLICT (telegram_id)
                    DO UPDATE SET time_credits_seconds = users.time_credits_seconds + EXCLUDED.time_credits_seconds
                    """,
                    (user_id, credits)
                )

            # Log the transaction
            cursor.execute(
                """
                INSERT INTO payment_logs (telegram_id, credit_type, amount, timestamp, stripe_session_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, credit_type, credits, datetime.now(), None)
            )

            conn.commit()
            logger.info(f"Added {credits} {credit_type} credits to user {user_id}")
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        conn.close()

def save_payment_method(user_id: int, payment_method_id: str, customer_id: str) -> None:
    """Save payment method for auto-recharge."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auto_recharge_settings (telegram_id, stripe_payment_method_id)
                VALUES (%s, %s)
                ON CONFLICT (telegram_id)
                DO UPDATE SET stripe_payment_method_id = EXCLUDED.stripe_payment_method_id
                """,
                (user_id, payment_method_id)
            )
            conn.commit()
            logger.info(f"Saved payment method for user {user_id}")
    except Exception as e:
        logger.error(f"Error saving payment method: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        conn.close()

def log_failed_payment(user_id: int, amount: int, reason: str, payment_intent_id: str) -> None:
    """Log failed payment for tracking and analysis."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO failed_payments (telegram_id, amount, failure_reason, payment_intent_id, failed_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, amount, reason, payment_intent_id, datetime.now())
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Error logging failed payment: {e}")
    finally:
        conn.close()

def disable_auto_recharge(user_id: int, reason: str) -> None:
    """Disable auto-recharge after multiple failures."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE auto_recharge_settings
                SET enabled = FALSE, disabled_reason = %s, disabled_at = %s
                WHERE telegram_id = %s
                """,
                (reason, datetime.now(), user_id)
            )
            conn.commit()
            logger.info(f"Disabled auto-recharge for user {user_id}: {reason}")
    except Exception as e:
        logger.error(f"Error disabling auto-recharge: {e}")
    finally:
        conn.close()

async def send_telegram_notification(user_id: int, message: str) -> None:
    """Send notification to user via Telegram bot (requires bot integration)."""
    # This would require importing the bot instance or using a notification queue
    # For now, we'll log the notification
    logger.info(f"Telegram notification for user {user_id}: {message}")

async def send_admin_alert(message: str) -> None:
    """Send alert to admin via Telegram."""
    logger.info(f"Admin alert: {message}")

# ========================= WEBHOOK HANDLERS =========================

async def handle_checkout_session_completed(session: Dict[str, Any]) -> bool:
    """Handle successful checkout session completion."""
    try:
        # Get user and product info from metadata
        user_id = int(session['metadata']['telegram_user_id'])
        item_type = session['metadata']['item_type']
        amount = int(session['metadata']['amount'])

        # Add credits to user
        if item_type == 'credits':
            add_user_credits(user_id, amount, 'message')
        else:  # time
            add_user_credits(user_id, amount, 'time')

        # Save payment method if available for future auto-recharge
        if session.get('payment_intent'):
            payment_intent = stripe.PaymentIntent.retrieve(session['payment_intent'])
            if payment_intent.get('payment_method') and session.get('customer'):
                save_payment_method(user_id, payment_intent['payment_method'], session['customer'])

        # Send success notification
        await send_telegram_notification(
            user_id,
            f"✅ Payment successful! {amount} {'credits' if item_type == 'credits' else 'minutes'} added to your account."
        )

        logger.info(f"Successfully processed payment for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error handling checkout session: {e}")
        return False

async def handle_payment_intent_failed(payment_intent: Dict[str, Any]) -> bool:
    """Handle failed payment intent."""
    try:
        customer_id = payment_intent.get('customer')
        if not customer_id:
            logger.warning("No customer ID in failed payment intent")
            return False

        user_id = get_user_by_customer_id(customer_id)
        if not user_id:
            logger.warning(f"No user found for customer {customer_id}")
            return False

        amount = payment_intent['amount'] // 100  # Convert from cents
        failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')

        # Log the failed payment
        log_failed_payment(user_id, amount, failure_reason, payment_intent['id'])

        # Check if this is an auto-recharge failure
        metadata = payment_intent.get('metadata', {})
        if metadata.get('auto_recharge') == 'true':
            # Send auto-recharge failure notification
            await send_telegram_notification(
                user_id,
                f"❌ Auto-recharge failed: {failure_reason}\n\n"
                f"Please update your payment method in /billing or disable auto-recharge in /autorecharge."
            )

            # Check failure frequency and disable if needed
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM failed_payments
                        WHERE telegram_id = %s
                        AND failed_at > NOW() - INTERVAL '24 hours'
                        """,
                        (user_id,)
                    )
                    recent_failures = cursor.fetchone()[0]

                    if recent_failures >= 3:  # 3 failures in 24 hours
                        disable_auto_recharge(user_id, f"3+ failures in 24h: {failure_reason}")
                        await send_telegram_notification(
                            user_id,
                            "⚠️ Auto-recharge has been disabled due to multiple payment failures. "
                            "Please update your payment method and re-enable in /autorecharge."
                        )
            finally:
                conn.close()
        else:
            # Regular payment failure
            await send_telegram_notification(
                user_id,
                f"❌ Payment failed: {failure_reason}\n\n"
                f"Please try again or use a different payment method."
            )

        logger.info(f"Handled payment failure for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")
        return False

async def handle_payment_method_attached(payment_method: Dict[str, Any]) -> bool:
    """Handle when a payment method is attached to a customer."""
    try:
        customer_id = payment_method.get('customer')
        if not customer_id:
            return False

        user_id = get_user_by_customer_id(customer_id)
        if not user_id:
            return False

        # Save the payment method for auto-recharge
        save_payment_method(user_id, payment_method['id'], customer_id)

        # Notify user
        card_info = payment_method.get('card', {})
        card_brand = card_info.get('brand', 'card').title()
        card_last4 = card_info.get('last4', 'XXXX')

        await send_telegram_notification(
            user_id,
            f"💳 Payment method saved: {card_brand} ending in {card_last4}\n\n"
            f"You can now enable auto-recharge in /autorecharge for seamless credit top-ups!"
        )

        logger.info(f"Payment method attached for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error handling payment method attached: {e}")
        return False

async def handle_invoice_payment_succeeded(invoice: Dict[str, Any]) -> bool:
    """Handle successful subscription invoice payment."""
    try:
        customer_id = invoice.get('customer')
        if not customer_id:
            return False

        user_id = get_user_by_customer_id(customer_id)
        if not user_id:
            return False

        amount_paid = invoice['amount_paid'] // 100  # Convert from cents

        # For subscription plans - add monthly credits
        subscription_id = invoice.get('subscription')
        if subscription_id:
            # Add monthly credits based on subscription plan
            # This would need to be configured based on your subscription plans
            monthly_credits = 1000  # Example: premium plan gives 1000 credits/month
            add_user_credits(user_id, monthly_credits, 'message')

            await send_telegram_notification(
                user_id,
                f"✅ Subscription renewed! {monthly_credits} credits added to your account.\n\n"
                f"Amount charged: ${amount_paid}"
            )

        logger.info(f"Invoice payment succeeded for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error handling invoice payment: {e}")
        return False

async def handle_charge_dispute_created(dispute: Dict[str, Any]) -> bool:
    """Handle chargeback/dispute creation."""
    try:
        charge = dispute.get('charge', {})
        customer_id = charge.get('customer')
        amount = dispute['amount'] // 100  # Convert from cents
        reason = dispute.get('reason', 'Unknown')

        user_id = None
        if customer_id:
            user_id = get_user_by_customer_id(customer_id)

        # Log dispute for business tracking
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO disputes (telegram_id, dispute_id, amount, reason, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, dispute['id'], amount, reason, dispute['status'], datetime.now())
                )
                conn.commit()
        finally:
            conn.close()

        # Alert admin
        await send_admin_alert(
            f"🚨 Chargeback Alert!\n\n"
            f"Amount: ${amount}\n"
            f"Reason: {reason}\n"
            f"User: {user_id or 'Unknown'}\n"
            f"Dispute ID: {dispute['id']}"
        )

        # If user identified, suspend account
        if user_id:
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET is_banned = TRUE, ban_reason = %s WHERE telegram_id = %s",
                        (f"Chargeback dispute: {dispute['id']}", user_id)
                    )
                    conn.commit()
            finally:
                conn.close()

            await send_telegram_notification(
                user_id,
                f"⚠️ Your account has been temporarily suspended due to a payment dispute.\n\n"
                f"Please contact support to resolve this issue."
            )

        logger.info(f"Handled dispute creation: {dispute['id']}")
        return True

    except Exception as e:
        logger.error(f"Error handling dispute: {e}")
        return False

async def handle_customer_subscription_deleted(subscription: Dict[str, Any]) -> bool:
    """Handle subscription cancellation."""
    try:
        customer_id = subscription.get('customer')
        if not customer_id:
            return False

        user_id = get_user_by_customer_id(customer_id)
        if not user_id:
            return False

        # Remove subscription benefits
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET subscription_status = 'cancelled' WHERE telegram_id = %s",
                    (user_id,)
                )
                conn.commit()
        finally:
            conn.close()

        await send_telegram_notification(
            user_id,
            f"📄 Subscription cancelled successfully.\n\n"
            f"Your current credits remain available, but no new monthly credits will be added.\n"
            f"You can resubscribe anytime in /start."
        )

        logger.info(f"Handled subscription cancellation for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Error handling subscription deletion: {e}")
        return False

# ========================= MAIN WEBHOOK ENDPOINT =========================

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Enhanced webhook handler supporting multiple Stripe events."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    if not sig_header:
        logger.error("Missing Stripe signature header")
        return jsonify({'error': 'Missing signature'}), 400

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )

        event_type = event['type']
        event_data = event['data']['object']

        # Route to appropriate handler
        handlers = {
            'checkout.session.completed': handle_checkout_session_completed,
            'payment_intent.payment_failed': handle_payment_intent_failed,
            'payment_method.attached': handle_payment_method_attached,
            'invoice.payment_succeeded': handle_invoice_payment_succeeded,
            'charge.dispute.created': handle_charge_dispute_created,
            'customer.subscription.deleted': handle_customer_subscription_deleted,
        }

        handler = handlers.get(event_type)
        if handler:
            import asyncio
            success = asyncio.run(handler(event_data))
            if success:
                logger.info(f"Successfully handled {event_type}")
                return jsonify({'received': True}), 200
            else:
                logger.error(f"Failed to handle {event_type}")
                return jsonify({'error': 'Handler failed'}), 500
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return jsonify({'received': True}), 200

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'webhooks_supported': [
            'checkout.session.completed',
            'payment_intent.payment_failed',
            'payment_method.attached',
            'invoice.payment_succeeded',
            'charge.dispute.created',
            'customer.subscription.deleted'
        ]
    })

if __name__ == '__main__':
    if not all([DATABASE_URL, STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET]):
        logger.error("Missing required environment variables")
        exit(1)

    logger.info(f"Starting enhanced webhook server on port {WEBHOOK_PORT}")
    logger.info("Supported webhooks: checkout.session.completed, payment_intent.payment_failed, payment_method.attached, invoice.payment_succeeded, charge.dispute.created, customer.subscription.deleted")
    app.run(host='0.0.0.0', port=WEBHOOK_PORT)