#!/usr/bin/env python3
"""
Webhook server for handling Stripe payments.
Run this alongside your Telegram bot to automatically credit users after payment.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Any

# Try to import optional dependencies with fallbacks
try:
    from flask import Flask, request, jsonify
    HAS_FLASK = True
except ImportError:
    print("Flask not available - webhook server will be disabled")
    Flask = None
    request = None
    jsonify = None
    HAS_FLASK = False

try:
    import stripe
    HAS_STRIPE = True
except ImportError:
    print("Stripe not available - payment webhooks will be disabled")
    stripe = None
    HAS_STRIPE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available, using environment variables directly")

try:
    import psycopg2
    HAS_POSTGRES = True
    # Type alias for when psycopg2 is available
    PostgresConnection = psycopg2.extensions.connection
except ImportError:
    print("psycopg2 not available - using fallback database handling")
    psycopg2 = None
    HAS_POSTGRES = False
    # Fallback type alias
    PostgresConnection = Any

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load configuration
DATABASE_URL: Optional[str] = os.getenv('DATABASE_URL')
STRIPE_API_KEY: Optional[str] = os.getenv('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv('STRIPE_WEBHOOK_SECRET')
WEBHOOK_PORT: int = int(os.getenv('WEBHOOK_PORT', '8000'))

# Configure Stripe if available
if HAS_STRIPE and STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY

# Initialize Flask app if available
if HAS_FLASK:
    app = Flask(__name__)
else:
    app = None


def get_db_connection() -> Optional[PostgresConnection]:
    """Create and return a database connection."""
    if HAS_POSTGRES and DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        logger.error("PostgreSQL not available or DATABASE_URL not set")
        return None


def add_user_credits(user_id: int, credits: int, credit_type: str = 'message') -> None:
    """Add credits to a user's account after successful payment."""
    conn = get_db_connection()
    if not conn:
        logger.error("Cannot add credits to user %s - no database connection", user_id)
        return

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
            logger.info("✅ Added %s %s credits to user %s", credits, credit_type, user_id)

    except Exception as e:
        logger.error("Error adding credits to user %s: %s", user_id, e)
        conn.rollback()
    finally:
        conn.close()


def save_payment_method(user_id: int, payment_method_id: str, customer_id: str) -> None:
    """Save payment method for auto-recharge."""
    conn = get_db_connection()
    if not conn:
        logger.error("Cannot save payment method for user {user_id} - no database connection")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO auto_recharge_settings
                    (telegram_id, stripe_customer_id, stripe_payment_method_id, enabled)
                VALUES (%s, %s, %s, false)
                ON CONFLICT (telegram_id)
                DO UPDATE SET
                    stripe_customer_id = EXCLUDED.stripe_customer_id,
                    stripe_payment_method_id = EXCLUDED.stripe_payment_method_id
                """,
                (user_id, customer_id, payment_method_id)
            )
            conn.commit()
            logger.info("✅ Saved payment method for user %s", user_id)
    except Exception as e:
        logger.error("Error saving payment method for user %s: %s", user_id, e)
        conn.rollback()
    finally:
        conn.close()


# Only define Flask routes if Flask is available
if HAS_FLASK and app:
    @app.route('/health', methods=['GET'])
    def health_check() -> tuple:
        """Health check endpoint."""
        return jsonify({'status': 'healthy'}), 200

    @app.route('/stripe-webhook', methods=['POST'])
    def stripe_webhook() -> tuple:
        """Handle Stripe webhook events."""
        if not HAS_STRIPE:
            logger.error("Stripe webhook received but Stripe is not available")
            return jsonify({'error': 'Stripe not configured'}), 503

        if not STRIPE_WEBHOOK_SECRET:
            logger.error("Stripe webhook secret not configured")
            return jsonify({'error': 'Webhook secret not configured'}), 503

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

            # Handle checkout.session.completed event
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']

                # Get user and product info from metadata
                user_id = int(session['metadata']['telegram_user_id'])
                item_type = session['metadata']['item_type']
                amount = int(session['metadata']['amount'])

                # Add credits to user
                if item_type == 'credits':
                    add_user_credits(user_id, amount, 'message')
                else:  # time
                    add_user_credits(user_id, amount, 'time')

                # Save payment method if available
                if session.get('payment_intent'):
                    # Retrieve payment intent to get payment method
                    payment_intent = stripe.PaymentIntent.retrieve(session['payment_intent'])
                    if payment_intent.get('payment_method') and session.get('customer'):
                        save_payment_method(
                            user_id,
                            payment_intent['payment_method'],
                            session['customer']
                        )

                logger.info("✅ Successfully processed payment for user %s", user_id)

                # TODO: Send notification to user via Telegram bot
                # This would require bot integration or a separate notification service

            return jsonify({'received': True}), 200

        except Exception as e:
            # Handle Stripe-specific errors only if Stripe is available
            if (HAS_STRIPE and hasattr(stripe, 'error') and
                isinstance(e, stripe.error.SignatureVerificationError)):
                logger.error("Invalid signature: %s", e)
                return jsonify({'error': 'Invalid signature'}), 400
            else:
                logger.error("Webhook error: %s", e)
                return jsonify({'error': str(e)}), 500

    @app.route('/telegram-webhook', methods=['POST'])
    def telegram_webhook() -> tuple:
        """Handle Telegram webhook requests."""
        try:
            update_data = request.get_json()

            if not update_data:
                logger.warning("Received empty webhook data")
                return jsonify({'status': 'error', 'message': 'No data'}), 400

            logger.info("Received Telegram webhook update: %s", update_data.get('update_id', 'unknown'))

            # For now, just acknowledge the webhook
            # TODO: Process the update with the bot application
            return jsonify({'status': 'ok', 'message': 'Webhook received'}), 200

        except Exception as e:
            logger.error("Telegram webhook error: %s", e)
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/health', methods=['GET'])
    def enhanced_health_check() -> tuple:
        """Enhanced health check endpoint."""
        return jsonify({
            'service': 'telegram-bot',
            'status': 'healthy',
            'mode': 'webhook',
            'timestamp': datetime.now().isoformat(),
            'stripe_available': HAS_STRIPE,
            'postgres_available': HAS_POSTGRES,
            'endpoints': {
                'telegram_webhook': '/telegram-webhook',
                'stripe_webhook': '/stripe-webhook',
                'health': '/health'
            }
        })


def main() -> None:
    """Main function to start the webhook server."""
    if not HAS_FLASK:
        logger.error("Flask not available - cannot start webhook server")
        return

    # Check required dependencies
    missing_deps = []
    if not DATABASE_URL:
        missing_deps.append("DATABASE_URL")
    if HAS_STRIPE and not STRIPE_API_KEY:
        missing_deps.append("STRIPE_API_KEY")
    if HAS_STRIPE and not STRIPE_WEBHOOK_SECRET:
        missing_deps.append("STRIPE_WEBHOOK_SECRET")

    if missing_deps:
        logger.warning("Missing environment variables: %s", ', '.join(missing_deps))
        logger.info("Some features may not work properly")

    logger.info("Starting webhook server on port %s", WEBHOOK_PORT)
    logger.info("Flask available: %s", HAS_FLASK)
    logger.info("Stripe available: %s", HAS_STRIPE)
    logger.info("PostgreSQL available: %s", HAS_POSTGRES)

    if app:
        app.run(host='0.0.0.0', port=WEBHOOK_PORT)


if __name__ == '__main__':
    main()