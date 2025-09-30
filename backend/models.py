"""
SQLAlchemy models. Production-ready structure with PII encryption and vector support.

- If using Postgres + pgvector, use `sqlalchemy.dialects.postgresql` for vector column.
- For MongoDB, convert these models to MongoEngine or pydantic/ODM.
"""

from datetime import datetime
from extensions import db
from sqlalchemy.dialects.postgresql import JSONB

# Optional: pgvector import if installed
# from pgvector.sqlalchemy import Vector

class User(db.Model):
    """
    User profile
    - email_enc and phone_enc store encrypted PII
    - external_id maps to CRM or SSO provider
    """
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    external_id = db.Column(db.String(128), unique=True, nullable=True)
    name = db.Column(db.String(256), nullable=True)
    email_enc = db.Column(db.LargeBinary, nullable=True)
    phone_enc = db.Column(db.LargeBinary, nullable=True)
    locale = db.Column(db.String(10), default="en_IN")
    crm_id = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversation(db.Model):
    """
    Conversation session
    - status: open, resolved, escalated
    - meta: arbitrary JSON for extra metadata
    """
    __tablename__ = "conversations"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    channel = db.Column(db.String(50), nullable=False, default="web")
    status = db.Column(db.String(50), default="open")
    language = db.Column(db.String(10), default="en_IN")
    meta = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    """
    Each message in a conversation.
    - metadata holds sentiment, intent, llm tokens, attachments meta, etc.
    """
    __tablename__ = "messages"
    id = db.Column(db.BigInteger, primary_key=True)
    conversation_id = db.Column(db.BigInteger, db.ForeignKey("conversations.id"), index=True, nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # user|bot|agent|system
    text = db.Column(db.Text, nullable=False)
    metadata = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Ticket(db.Model):
    """
    Ticket for human agent escalation or follow up.
    """
    __tablename__ = "tickets"
    id = db.Column(db.BigInteger, primary_key=True)
    conversation_id = db.Column(db.BigInteger, db.ForeignKey("conversations.id"), nullable=False)
    status = db.Column(db.String(50), default="open")
    assigned_agent = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    meta = db.Column(JSONB, nullable=True)

class KnowledgeDocument(db.Model):
    """
    Knowledge base document (for RAG).
    - embedding vector column if using pgvector
    """
    __tablename__ = "knowledge_documents"
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta = db.Column(JSONB, nullable=True)
    # embedding = db.Column(Vector(1536))  # enable if pgvector installed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
