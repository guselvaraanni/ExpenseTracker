"""Development seed data."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.defaults import seed_default_categories_for_user
from app.repositories.user_repository import UserRepository


def seed_demo_user(db: Session) -> None:
    """Create the default demo account if it does not exist."""
    repo = UserRepository(db)
    user = repo.get_by_email("test@example.com")
    if user is None:
        repo.create("test@example.com", hash_password("1234"))
        return

    seed_default_categories_for_user(db, user.id)
    db.commit()


def seed_all(db: Session) -> None:
    """Run all seed routines."""
    seed_demo_user(db)
