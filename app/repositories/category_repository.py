"""Category data access — PostgreSQL via SQLAlchemy."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Category, CategoryType
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):
    """CRUD operations for categories."""

    def get_by_id(self, category_id: int, user_id: int) -> Optional[Category]:
        """Return a category owned by the given user."""
        return (
            self.db.query(Category)
            .filter(Category.id == category_id, Category.user_id == user_id)
            .first()
        )

    def get_by_name(self, user_id: int, name: str) -> Optional[Category]:
        """Return a category by name for a user."""
        return (
            self.db.query(Category)
            .filter(Category.user_id == user_id, Category.name == name)
            .first()
        )

    def list_by_user(self, user_id: int) -> List[Category]:
        """Return all categories for a user."""
        return (
            self.db.query(Category)
            .filter(Category.user_id == user_id)
            .order_by(Category.type, Category.name)
            .all()
        )

    def create(
        self,
        user_id: int,
        name: str,
        category_type: CategoryType,
    ) -> Category:
        """Create a category for a user."""
        category = Category(
            user_id=user_id,
            name=name,
            type=category_type,
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(
        self,
        category: Category,
        name: str,
        category_type: CategoryType,
    ) -> Category:
        """Update an existing category."""
        category.name = name
        category.type = category_type
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        """Delete a category."""
        self.db.delete(category)
        self.db.commit()


def get_category_repository(db: Session) -> CategoryRepository:
    """Factory for request-scoped category repository."""
    return CategoryRepository(db)
