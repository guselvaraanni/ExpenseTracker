"""Category management logic."""

from __future__ import annotations

from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.models import Category, CategoryType
from app.repositories.category_repository import (
    CategoryRepository,
    get_category_repository,
)
from app.repositories.transaction_repository import (
    TransactionRepository,
    get_transaction_repository,
)
from app.schemas.auth import UserRead
from app.schemas.category import (
    CategoryListResponse,
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)


class CategoryService:
    """Handles category creation, listing, and removal."""

    def __init__(
        self,
        category_repository: CategoryRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self.category_repository = category_repository
        self.transaction_repository = transaction_repository

    def list_categories(self, user: UserRead) -> CategoryListResponse:
        """Return all categories for the current user."""
        categories = self.category_repository.list_by_user(user.id)
        items = [self._to_response(category) for category in categories]
        return CategoryListResponse(items=items, total=len(items))

    def create_category(
        self,
        user: UserRead,
        payload: CreateCategoryRequest,
    ) -> CategoryResponse:
        """Create a category after validation."""
        name = self._normalize_name(payload.name)
        category_type = self._parse_type(payload.type)

        existing = self.category_repository.get_by_name(user.id, name)
        if existing is not None:
            raise ValidationError(f"Category '{name}' already exists.")

        category = self.category_repository.create(user.id, name, category_type)
        return self._to_response(category)

    def update_category(
        self,
        user: UserRead,
        category_id: int,
        payload: UpdateCategoryRequest,
    ) -> CategoryResponse:
        """Update a category owned by the current user."""
        category = self._get_owned_category(user.id, category_id)

        name = (
            self._normalize_name(payload.name)
            if payload.name is not None
            else category.name
        )
        category_type = (
            self._parse_type(payload.type)
            if payload.type is not None
            else category.type
        )

        if payload.name is None and payload.type is None:
            raise ValidationError("At least one field must be provided.")

        duplicate = self.category_repository.get_by_name(user.id, name)
        if duplicate is not None and duplicate.id != category.id:
            raise ValidationError(f"Category '{name}' already exists.")

        updated = self.category_repository.update(category, name, category_type)
        return self._to_response(updated)

    def delete_category(self, user: UserRead, category_id: int) -> None:
        """Delete a category if it is not in use."""
        category = self._get_owned_category(user.id, category_id)
        in_use = self.transaction_repository.count_by_category(category.id, user.id)
        if in_use > 0:
            raise ValidationError(
                "Cannot delete a category that has transactions. "
                "Reassign or delete those transactions first."
            )
        self.category_repository.delete(category)

    def _get_owned_category(self, user_id: int, category_id: int) -> Category:
        """Return a category or raise if missing."""
        category = self.category_repository.get_by_id(category_id, user_id)
        if category is None:
            raise NotFoundError("Category not found.")
        return category

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Trim and validate category name."""
        normalized = name.strip()
        if not normalized:
            raise ValidationError("Category name is required.")
        return normalized

    @staticmethod
    def _parse_type(value: str) -> CategoryType:
        """Map API type string to enum."""
        try:
            return CategoryType(value)
        except ValueError as exc:
            raise ValidationError("Category type must be 'income' or 'expense'.") from exc

    @staticmethod
    def _to_response(category: Category) -> CategoryResponse:
        """Map ORM category to API schema."""
        return CategoryResponse(
            id=category.id,
            name=category.name,
            type=category.type.value,
            user_id=category.user_id,
        )


def get_category_service(
    db: Session = Depends(get_db),
) -> CategoryService:
    """Dependency factory for CategoryService."""
    return CategoryService(
        get_category_repository(db),
        get_transaction_repository(db),
    )
