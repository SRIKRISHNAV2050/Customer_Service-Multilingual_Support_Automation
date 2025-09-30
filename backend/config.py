"""
Application configuration.

- Centralizes configuration loading from environment variables.
- Keeps SLA-related timeouts and API endpoints configurable.
- In production, prefer using a secrets manager and not raw env files.
"""

import os
from datetime import timedelta

class Config:
    # App
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = ENV != "production"
    SECRET_KEY = os.getenv("SECRET_KEY", "please-change-me")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/customer_ai")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis / Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # External APIs (limit to 3: SMS, EMAIL, PAYMENT)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    WHISPER_API_KEY = os.getenv("WHISPER_API_KEY")

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # SLA / Performance tuning
    LLM_REQUEST_TIMEOUT_SEC = int(os.getenv("LLM_REQUEST_TIMEOUT_SEC", "8"))
    STT_REQUEST_TIMEOUT_SEC = int(os.getenv("STT_REQUEST_TIMEOUT_SEC", "10"))
    TEXT_RESPONSE_SLA_MS = int(os.getenv("TEXT_RESPONSE_SLA_MS", "5000"))
    VOICE_RESPONSE_SLA_MS = int(os.getenv("VOICE_RESPONSE_SLA_MS", "15000"))

    # Security / Encryption
    FERNET_KEY = os.getenv("FERNET_KEY")  # Use KMS in production

    # Misc
    MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "8"))
    TOKEN_BUDGET = int(os.getenv("TOKEN_BUDGET", "2000"))

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False

