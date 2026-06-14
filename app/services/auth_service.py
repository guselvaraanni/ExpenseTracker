"""Authentication business logic."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.exceptions import UnauthorizedError
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.repositories.user_repository import UserRepository, get_user_repository
from app.schemas.auth import SignupRequest, UserRead


class AuthService:
    """Handles user registration, login, and session management."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register(self, payload: SignupRequest) -> UserRead:
        """Register a new user with a hashed password."""
        password_hash = hash_password(payload.password)
        user = self.user_repository.create(payload.email, password_hash)
        return self._to_user_read(user)

    def authenticate(self, email: str, password: str) -> UserRead:
        """Validate credentials and return the authenticated user."""
        user = self.user_repository.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")
        return self._to_user_read(user)

    @staticmethod
    def create_session(request: Request, user: UserRead) -> None:
        """Persist authenticated user in the server-side session."""
        request.session["user_id"] = user.email

    @staticmethod
    def destroy_session(request: Request) -> None:
        """Clear the current session."""
        request.session.clear()

    def get_user_from_session(self, request: Request) -> Optional[UserRead]:
        """Return the logged-in user from session, if any."""
        email = request.session.get("user_id")
        if not email:
            return None

        user = self.user_repository.get_by_email(email)
        if user is None or not user.is_active:
            request.session.clear()
            return None

        return self._to_user_read(user)

    @staticmethod
    def _to_user_read(user: User) -> UserRead:
        """Map ORM user to API schema."""
        return UserRead(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
        )


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    """Dependency factory for AuthService."""
    return AuthService(get_user_repository(db))
