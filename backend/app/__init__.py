from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask

from .config import Config
from .extensions import cors, db, ma, migrate
from sqlalchemy.exc import IntegrityError
from .utils.rate_limit import limiter


def create_app(config_class: type[Config] | None = None) -> Flask:
    """Application factory."""
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class or Config())

    _ensure_storage_dirs(app)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    limiter.init_app(app)
    # Ensure database tables exist on startup so runtime requests won't fail
    # with "no such table" errors. Calling create_all here is safe for simple
    # deployments; in production you may prefer migrations.
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            app.logger.exception("Failed to create database tables on startup")

    _register_blueprints(app)
    if not app.config.get("TESTING"):
        _seed_default_user(app)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


def _ensure_storage_dirs(app: Flask) -> None:
    """Create required directories for data persistence."""
    for key in ("DATA_DIR", "IMAGE_DIR", "THUMBNAIL_DIR", "DB_DIR"):
        path = app.config.get(key)
        if not path:
            continue
        Path(path).mkdir(parents=True, exist_ok=True)


def _register_blueprints(app: Flask) -> None:
    from .api.auth import auth_bp
    from .api.paintings import paintings_bp
    from .api.search import search_bp
    from .api.users import users_bp
    from .media import media_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(paintings_bp, url_prefix="/api/paintings")
    app.register_blueprint(search_bp, url_prefix="/api/search")
    app.register_blueprint(media_bp, url_prefix="/media")


def _seed_default_user(app: Flask) -> None:
    from .models import User
    from .extensions import db

    with app.app_context():
        db.create_all()
        if User.query.first():
            return
        user = User(username="studio", email="studio@canvas3t.local")
        user.set_password("canvas3t-demo")
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

