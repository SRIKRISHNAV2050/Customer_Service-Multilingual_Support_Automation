"""
Initialize and expose extensions: db, migrate, redis client, celery.

This centralizes initialization to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
redis_client = None
celery = None

def init_redis(app):
    """Initialize redis client (used for cache, rate-limit, celery broker)."""
    global redis_client
    url = app.config.get("REDIS_URL")
    redis_client = redis.from_url(url)
    return redis_client

def init_celery(app):
    """Create celery application bound to Flask config."""
    global celery
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery
  
