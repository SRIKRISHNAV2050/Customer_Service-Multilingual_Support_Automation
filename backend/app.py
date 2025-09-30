"""
Application factory.

- Bootstraps Flask, extensions, blueprints.
- Provides a lightweight health check.
- For production use Gunicorn + multiple workers.
"""

from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, init_redis, init_celery
import os

def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    init_redis(app)
    init_celery(app)

    # Register Blueprints
    from routes.chat import chat_bp
    from routes.voice import voice_bp
    from routes.agent import agent_bp
    from routes.transaction import transaction_bp

    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(voice_bp, url_prefix="/api/voice")
    app.register_blueprint(agent_bp, url_prefix="/api/agent")
    app.register_blueprint(transaction_bp, url_prefix="/api/transaction")

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "env": app.config.get("ENV")})

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

