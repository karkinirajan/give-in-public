import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def _database_uri() -> str:
    """DATABASE_URL (Heroku style `postgres://` is accepted), or a local SQLite file."""
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        return "sqlite:///database.db"
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    app.config.update(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=_database_uri(),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "").lower()
        in {"1", "true", "yes"},
    )
    if config:
        app.config.update(config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set the SECRET_KEY environment variable before starting the app.")

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    from .auth import auth
    from .models import User
    from .views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # No migration tooling yet: create any missing tables on startup.
    with app.app_context():
        db.create_all()

    return app
