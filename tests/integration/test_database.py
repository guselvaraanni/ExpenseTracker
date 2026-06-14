"""Integration tests for database-backed repositories."""

from decimal import Decimal

from app.models import UserProfile
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository


def test_user_registration_creates_profile(db_session) -> None:
    """Creating a user also creates an empty profile row."""
    repo = UserRepository(db_session)
    user = repo.create("profileuser@example.com", "hashed-password")

    profile = (
        db_session.query(UserProfile)
        .filter(UserProfile.user_id == user.id)
        .first()
    )
    assert profile is not None
    assert profile.currency == "USD"
    assert profile.monthly_salary is None


def test_profile_repository_update_salary(db_session) -> None:
    """Profile repository can persist monthly salary."""
    user_repo = UserRepository(db_session)
    user = user_repo.create("salaryuser@example.com", "hashed-password")

    profile_repo = ProfileRepository(db_session)
    profile = profile_repo.update_salary(user.id, monthly_salary=Decimal("450000"))

    assert profile.monthly_salary == 450000
    assert profile.currency == "USD"
