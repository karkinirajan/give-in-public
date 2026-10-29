import hashlib
import hmac

import pytest

from Website.security import hash_password, verify_password


def legacy_hash(password: str, salt: str = "abcdefghijklmnop") -> str:
    """Werkzeug 2.0 `method='sha256'` format."""
    return f"sha256${salt}${hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()}"


def test_new_hash_fits_the_existing_150_char_column():
    assert len(hash_password("pw-12345-xyz")) <= 150


def test_new_hash_verifies_and_needs_no_rehash():
    assert verify_password(hash_password("secret"), "secret") == (True, False)
    assert verify_password(hash_password("secret"), "nope") == (False, False)


def test_legacy_hash_verifies_and_is_flagged_for_upgrade():
    stored = legacy_hash("secret")
    assert verify_password(stored, "secret") == (True, True)
    assert verify_password(stored, "wrong") == (False, False)


@pytest.mark.parametrize("stored", [None, "", "sha256$only-two", "md5$salt$abc", "garbage"])
def test_malformed_or_missing_hashes_are_rejected(stored):
    assert verify_password(stored, "secret") == (False, False)


def test_missing_password_is_rejected():
    assert verify_password(hash_password("x"), None) == (False, False)
