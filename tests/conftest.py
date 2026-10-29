import os

os.environ.setdefault("SECRET_KEY", "test-only-secret-key")

import pytest  # noqa: E402

from Website import create_app, db  # noqa: E402


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            # In-memory SQLite by default; set TEST_DATABASE_URL to run against PostgreSQL.
            "SQLALCHEMY_DATABASE_URI": os.environ.get("TEST_DATABASE_URL", "sqlite://"),
        }
    )
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_user(app):
    from Website.models import User
    from Website.security import hash_password

    def _make(email="alice@example.com", password="pw-12345-xyz", name="Alice"):
        user = User(email=email, first_name=name, password=hash_password(password), type="donor")
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def login(client):
    def _login(email="alice@example.com", password="pw-12345-xyz"):
        return client.post("/login", data={"email": email, "password1": password})

    return _login
