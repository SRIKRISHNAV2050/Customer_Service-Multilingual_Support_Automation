"""
Security helpers: encryption for small PII fields, JWT utilities for agents,
and webhook signature helpers.

Important:
- Do NOT keep encryption keys in source or .env in prod; use KMS (AWS/GCP/Azure).
- Use minimal encryption at application level for small fields; for DB-level encryption use DB features if available.
"""

from cryptography.fernet import Fernet
import os
import jwt
from functools import wraps
from flask import request, jsonify, current_app

FERNET_KEY = os.getenv("FERNET_KEY", Fernet.generate_key().decode())
fernet = Fernet(FERNET_KEY.encode())

def encrypt_field(plaintext: str) -> bytes:
    if plaintext is None:
        return None
    return fernet.encrypt(plaintext.encode("utf-8"))

def decrypt_field(cipher: bytes) -> str:
    if cipher is None:
        return None
    return fernet.decrypt(cipher).decode("utf-8")

def admin_required(f):
    """Agent/employee auth decorator. Replace simple JWT verification with real auth in prod."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET", "secret"), algorithms=["HS256"])
            if payload.get("role") != "agent":
                return jsonify({"error": "Forbidden"}), 403
            request.agent = payload  # attach agent info
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper
