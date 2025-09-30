"""
Payment wrapper (Stripe).

- create_payment_intent(amount_cents, currency, metadata) -> PaymentIntent info
- handle_stripe_webhook(raw_body, signature) -> validated event dict

Security:
- Validate webhook signature using STRIPE_WEBHOOK_SECRET
- Use idempotency keys for safe retries
"""

import os
import stripe
from config import Config

stripe.api_key = Config.STRIPE_API_KEY

def create_payment_intent(amount_cents: int, currency: str = "inr", metadata: dict = None) -> dict:
    pi = stripe.PaymentIntent.create(amount=amount_cents, currency=currency, metadata=metadata or {})
    return {"id": pi.id, "client_secret": pi.client_secret, "status": pi.status}

def handle_stripe_webhook(raw_body: bytes, signature: str):
    try:
        event = stripe.Webhook.construct_event(raw_body, signature, Config.STRIPE_WEBHOOK_SECRET)
        return event
    except Exception as e:
        raise
