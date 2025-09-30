"""
Text chat endpoints.

Endpoints:
- POST /send      → Send a user text message and get assistant reply
- GET /history    → Get recent conversation history
- POST /escalate  → Request human escalation

Important:
- Enforce rate-limiting and request size checks here.
- Keep request/response sizes small to meet 5s SLA.
"""

from flask import Blueprint, request, jsonify, current_app
from models import Conversation, Message, User, Ticket
from extensions import db, redis_client
from services.llm_service import call_llm
from services.sentiment_service import analyze_sentiment
from utils.rate_limiter import rate_limit

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/send", methods=["POST"])
@rate_limit("chat_send", limit=60, period=60)  # example: 60 req/min
def send():
    """
    Request body:
    {
        "user_id": "external-123",
        "message": "My internet is down",
        "conversation_id": null, # optional
        "locale": "hi_IN"
    }
    Response:
    {
        "reply": "...",
        "conversation_id": 1234,
        "meta": {"sentiment": -0.6, "llm_meta": {...}}
    }
    """
    payload = request.json or {}
    user_id = payload.get("user_id")
    text = payload.get("message", "").strip()[:5000]  # limit length
    locale = payload.get("locale", "en_IN")

    # Basic validation
    if not user_id or not text:
        return jsonify({"error": "user_id and message required"}), 400

    # Create or fetch conversation
    conversation = _get_or_create_conversation(user_id, payload.get("conversation_id"), locale)

    # Append user message
    user_msg = Message(conversation_id=conversation.id, sender="user", text=text, metadata={"locale": locale})
    db.session.add(user_msg)
    db.session.commit()

    # Quick sentiment (inline to allow immediate reaction)
    sentiment = analyze_sentiment(text, locale)

    # Build short context: fetch recent N messages
    recent_context = _fetch_recent_messages(conversation.id)

    # Call LLM adapter
    assistant_reply, llm_meta = call_llm(recent_context, text, locale)

    # Persist bot reply
    bot_msg = Message(conversation_id=conversation.id, sender="bot", text=assistant_reply, metadata={"llm": llm_meta})
    db.session.add(bot_msg)
    db.session.commit()

    # Escalation rules: E.g., negative sentiment or keywords
    if should_escalate(sentiment, assistant_reply):
        ticket = Ticket(conversation_id=conversation.id, status="open")
        db.session.add(ticket)
        db.session.commit()
        # schedule agent notification via Celery or internal queue

    return jsonify({"reply": assistant_reply, "conversation_id": conversation.id, "meta": {"sentiment": sentiment, "llm_meta": llm_meta}})

def _get_or_create_conversation(user_external_id: str, conversation_id: int, locale: str):
    """Helper to fetch or create conversation. This function should be atomic in production."""
    if conversation_id:
        conv = Conversation.query.get(conversation_id)
        if conv:
            return conv
    # find last open conversation for user
    user = User.query.filter_by(external_id=user_external_id).first()
    if not user:
        # In production, create user record with minimal data and fill later from CRM
        user = User(external_id=user_external_id, locale=locale)
        db.session.add(user)
        db.session.commit()
    conv = Conversation(user_id=user.id, channel="web", language=locale)
    db.session.add(conv)
    db.session.commit()
    return conv

def _fetch_recent_messages(conversation_id: int, limit:int=8):
    """
    Try Redis cache for speed; otherwise read from DB.
    Returns a list of dicts {'role': 'user'|'assistant', 'content': '...'}
    """
    # Implementation details described in service skeletons
    return []

def should_escalate(sentiment_score: float, assistant_reply: str) -> bool:
    """Simple heuristic; replace with ML model later."""
    if sentiment_score is None:
        return False
    return sentiment_score < -0.5 or "human" in assistant_reply.lower()
