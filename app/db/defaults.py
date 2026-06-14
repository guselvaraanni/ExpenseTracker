"""Default category definitions seeded for new users."""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models import Category, CategoryType

DEFAULT_CATEGORIES: List[Tuple[str, CategoryType]] = [
    ("Food", CategoryType.EXPENSE),
    ("Transport", CategoryType.EXPENSE),
    ("Shopping", CategoryType.EXPENSE),
    ("Bills", CategoryType.EXPENSE),
    ("Health", CategoryType.EXPENSE),
    ("Salary", CategoryType.INCOME),
    ("Freelance", CategoryType.INCOME),
    ("Investment", CategoryType.INCOME),
]


def seed_default_categories_for_user(db: Session, user_id: int) -> None:
    """Create default categories for a user when none exist."""
    existing = db.query(Category).filter(Category.user_id == user_id).count()
    if existing > 0:
        return

    for name, category_type in DEFAULT_CATEGORIES:
        db.add(
            Category(
                user_id=user_id,
                name=name,
                type=category_type,
            )
        )
