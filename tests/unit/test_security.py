"""Unit tests for password hashing."""

from app.core.security import hash_password, verify_password


def test_hash_password_produces_bcrypt_hash() -> None:
    """Hashed passwords use bcrypt format."""
    hashed = hash_password("my-secret")
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_verify_password_accepts_correct_password() -> None:
    """Correct password verifies successfully."""
    hashed = hash_password("my-secret")
    assert verify_password("my-secret", hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    """Incorrect password fails verification."""
    hashed = hash_password("my-secret")
    assert verify_password("wrong-password", hashed) is False
