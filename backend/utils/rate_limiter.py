"""
Simple rate-limiter decorator using Redis.

- Use token bucket / leaky bucket algorithm.
- Keep limits per user and per IP for abuse protection.
"""

import time
from functools import wraps
from extensions import redis_client
from flask import request, jsonify

def rate_limit(key_prefix: str, limit: int = 120, period: int = 60):
    """Decorator that rate-limits the wrapped view."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identifier = request.headers.get("X-User-Id") or request.remote_addr
            key = f"rl:{key_prefix}:{identifier}"
            current = redis_client.get(key)
            if current is None:
                redis_client.set(key, 1, ex=period)
            else:
                count = int(current)
                if count >= limit:
                    return jsonify({"error": "rate_limited"}), 429
                redis_client.incr(key)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
