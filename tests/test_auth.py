from Website import create_app, db
from Website.models import User

from .test_security import legacy_hash


def signup(client, **overrides):
    data = {
        "email": "alice@example.com",
        "password1": "pw-12345-xyz",
        "password2": "pw-12345-xyz",
        "fullname": "Alice",
        "radio": "donor",
    } | overrides
    return client.post("/signup", data=data)


def test_signup_creates_user_with_hashed_password(client, app):
    res = signup(client)
    assert res.status_code == 302 and res.headers["Location"].endswith("/login")
    user = User.query.filter_by(email="alice@example.com").one()
    assert user.password != "pw-12345-xyz" and len(user.password) <= 150


def test_signup_rejects_duplicates_mismatch_short_name_and_empty_password(client, make_user):
    make_user()
    for overrides in (
        {},  # duplicate email
        {"email": "bob@example.com", "password2": "different"},
        {"email": "bob@example.com", "fullname": "Bo"},
        {"email": "bob@example.com", "password1": "", "password2": ""},
        {"email": "b@x.io"},  # email shorter than 8 characters
    ):
        assert signup(client, **overrides).status_code == 200
    assert User.query.count() == 1


def test_signup_with_missing_fields_does_not_crash(client):
    assert client.post("/signup", data={}).status_code == 200


def test_login_success_redirects_to_dashboard(client, make_user, login):
    make_user()
    res = login()
    assert res.status_code == 302 and res.headers["Location"].endswith("/dashboard/configure")


def test_login_wrong_password_and_unknown_email(client, make_user, login):
    make_user()
    assert login(password="nope").status_code == 200
    assert login(email="ghost@example.com").status_code == 200
    assert client.get("/dashboard/configure").status_code == 302  # still logged out


def test_legacy_hash_user_can_log_in_and_is_upgraded(client, app):
    user = User(email="old@example.com", first_name="Old", password=legacy_hash("old-pass"))
    db.session.add(user)
    db.session.commit()
    res = client.post("/login", data={"email": "old@example.com", "password1": "old-pass"})
    assert res.status_code == 302
    db.session.refresh(user)
    assert not user.password.startswith("sha256$")
    # and the upgraded hash still works
    client.get("/logout")
    assert (
        client.post(
            "/login", data={"email": "old@example.com", "password1": "old-pass"}
        ).status_code
        == 302
    )


def test_logout_requires_login_then_logs_out(client, make_user, login):
    assert client.get("/logout").status_code == 302
    make_user()
    login()
    assert client.get("/logout").status_code == 302
    assert client.get("/dashboard/configure").status_code == 302


def test_csrf_is_enforced_on_forms(make_user):
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.app_context():
        client = app.test_client()
        assert client.post("/login", data={"email": "a", "password1": "b"}).status_code == 400
        page = client.get("/login").get_data(as_text=True)
        assert 'name="csrf_token"' in page


def test_missing_secret_key_fails_fast(monkeypatch):
    import pytest

    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"SQLALCHEMY_DATABASE_URI": "sqlite://"})
