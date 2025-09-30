"""
Transaction routes for payments.

- POST /create -> Create payment intent (Stripe)
- POST /webhook -> Receive Stripe webhook (validate signature)

Security:
- Validate Stripe webhook signature using STRIPE_WEBHOOK_SECRET
- Idempotency keys for PaymentIntent creation
"""

from flask import Blueprint, request, jsonify, current_app
from services.payments import create_payment_intent, handle_stripe_webhook

transaction_bp = Blueprint("transaction", __name__)

@transaction_bp.route("/create", methods=["POST"])
def create_payment():
    """
    Body:
    {
        "amount_cents": 12345,
        "currency": "inr",
        "metadata": {...}
    }
    """
    payload = request.json or {}
    amount = payload.get("amount_cents")
    currency = payload.get("currency", "inr")
    if not amount:
        return jsonify({"error": "amount_cents required"}), 400
    pi = create_payment_intent(amount, currency, metadata=payload.get("metadata"))
    return jsonify(pi)

@transaction_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    raw = request.data
    sig = request.headers.get("Stripe-Signature")
    try:
        event = handle_stripe_webhook(raw, sig)
        # Process event types: payment_intent.succeeded etc.
        return jsonify({"received": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
