"""User data access — PostgreSQL via SQLAlchemy."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import UserAlreadyExistsError
from app.db.defaults import seed_default_categories_for_user
from app.models import User, UserProfile
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """CRUD operations for users."""

    def get_by_email(self, email: str) -> Optional[User]:
        """Return a user by email address."""
        return (
            self.db.query(User)
            .filter(User.email == email.lower())
            .first()
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Return a user by primary key."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, password_hash: str) -> User:
        """Register a new user with an empty profile."""
        normalized = email.lower()
        if self.get_by_email(normalized) is not None:
            raise UserAlreadyExistsError("User already exists. Please login.")

        user = User(
            email=normalized,
            password_hash=password_hash,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()

        profile = UserProfile(user_id=user.id, currency="USD")
        self.db.add(profile)
        seed_default_categories_for_user(self.db, user.id)
        self.db.commit()
        self.db.refresh(user)
        return user

    def count(self) -> int:
        """Return total number of registered users."""
        return self.db.query(User).count()


def get_user_repository(db: Session) -> UserRepository:
    """Factory for request-scoped user repository."""
    return UserRepository(db)
