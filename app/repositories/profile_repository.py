"""User profile data access — PostgreSQL via SQLAlchemy."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models import UserProfile
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository):
    """CRUD operations for user profiles."""

    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """Return the profile for a user."""
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

    def update_salary(
        self,
        user_id: int,
        monthly_salary: Decimal,
        currency: str = "USD",
    ) -> UserProfile:
        """Update monthly salary for a user profile."""
        profile = self.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id, currency=currency)
            self.db.add(profile)

        profile.monthly_salary = monthly_salary
        profile.currency = currency
        self.db.commit()
        self.db.refresh(profile)
        return profile


def get_profile_repository(db: Session) -> ProfileRepository:
    """Factory for request-scoped profile repository."""
    return ProfileRepository(db)
