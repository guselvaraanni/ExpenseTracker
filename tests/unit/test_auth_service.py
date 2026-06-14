"""Unit tests for authentication service."""

import pytest

from app.core.exceptions import UnauthorizedError, UserAlreadyExistsError
from app.db.seed import seed_demo_user
from app.repositories.user_repository import UserRepository
from app.schemas.auth import SignupRequest
from app.services.auth_service import AuthService


@pytest.fixture
def auth_service(db_session) -> AuthService:
    """Provide an auth service backed by the test database."""
    seed_demo_user(db_session)
    return AuthService(UserRepository(db_session))


def test_authenticate_demo_user(auth_service: AuthService) -> None:
    """Demo user authenticates with correct password."""
    user = auth_service.authenticate("test@example.com", "1234")
    assert user.email == "test@example.com"


def test_authenticate_invalid_password(auth_service: AuthService) -> None:
    """Wrong password raises UnauthorizedError."""
    with pytest.raises(UnauthorizedError):
        auth_service.authenticate("test@example.com", "wrong")


def test_register_new_user(auth_service: AuthService) -> None:
    """Registration creates a new user."""
    payload = SignupRequest(
        email="alice@example.com",
        password="password1",
        confirm_password="password1",
    )
    user = auth_service.register(payload)
    assert user.email == "alice@example.com"
    assert user.id is not None


def test_register_duplicate_user(auth_service: AuthService) -> None:
    """Duplicate registration raises UserAlreadyExistsError."""
    payload = SignupRequest(
        email="test@example.com",
        password="password1",
        confirm_password="password1",
    )
    with pytest.raises(UserAlreadyExistsError):
        auth_service.register(payload)
