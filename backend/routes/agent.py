"""
Agent endpoints & handoff APIs.
- Agents authenticate via JWT.
- Provide endpoints to list tickets, claim, append message, close ticket.
- Provide context payload for agent UI.
"""

from flask import Blueprint, request, jsonify
from utils.security import admin_required
from models import Ticket, Conversation, Message
from extensions import db

agent_bp = Blueprint("agent", __name__)

@agent_bp.route("/tickets", methods=["GET"])
@admin_required
def list_tickets():
    # Pagination and filters in production
    tickets = Ticket.query.filter_by(status="open").all()
    return jsonify([{"ticket_id": t.id, "conversation_id": t.conversation_id} for t in tickets])

@agent_bp.route("/tickets/<int:ticket_id>/claim", methods=["POST"])
@admin_required
def claim(ticket_id):
    data = request.json or {}
    agent_id = data.get("agent_id")
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.assigned_agent = agent_id
    ticket.status = "assigned"
    db.session.commit()
    return jsonify({"ok": True})
