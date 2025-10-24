import os
import stripe
from flask import jsonify, request
from config.settings import Config

# Load Stripe keys from environment first, then fall back to config settings
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') or getattr(Config, 'STRIPE_SECRET_KEY', None)

def create_payment_intent(amount_cents, currency='usd', metadata=None):
    if stripe.api_key is None:
        raise RuntimeError('Stripe secret key not configured')
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            automatic_payment_methods={"enabled": True},
            metadata=metadata or {}
        )
        return intent
    except Exception as e:
        raise


def handle_stripe_webhook(request):
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET') or getattr(Config, 'STRIPE_WEBHOOK_SECRET', None)
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            event = stripe.Event.construct_from(request.json, stripe.api_key)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # TODO: mark order as paid using metadata/order id
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # TODO: handle failed payment

    return jsonify({'status': 'success'}), 200


def create_checkout_session(line_items, success_url, cancel_url, mode='payment', metadata=None):
    if stripe.api_key is None:
        raise RuntimeError('Stripe secret key not configured')
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode=mode,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {}
        )
        return session
    except Exception:
        raise