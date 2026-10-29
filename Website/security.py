"""Password hashing with support for hashes written by older Werkzeug versions."""

import hashlib
import hmac

from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    # pbkdf2 output fits the existing String(150) column (scrypt hashes are longer than 150).
    return generate_password_hash(password, method="pbkdf2:sha256")


def _check_legacy_sha256(stored: str, password: str) -> bool:
    """Verify Werkzeug 2.0's ``method='sha256'`` format: ``sha256$<salt>$<hmac-sha256-hex>``.

    Werkzeug 3 removed this method, but existing users' stored hashes still use it.
    """
    try:
        method, salt, digest = stored.split("$", 2)
    except ValueError:
        return False
    if method != "sha256":
        return False
    expected = hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, digest)


def verify_password(stored: str | None, password: str | None) -> tuple[bool, bool]:
    """Return ``(is_valid, needs_rehash)``. Legacy hashes are valid but should be upgraded."""
    if not stored or password is None:
        return False, False
    if stored.startswith("sha256$"):
        ok = _check_legacy_sha256(stored, password)
        return ok, ok
    try:
        return check_password_hash(stored, password), False
    except ValueError:  # unsupported/legacy method that Werkzeug no longer implements
        return False, False
