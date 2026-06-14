"""Transaction business logic."""

from __future__ import annotations

import math
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.models import CategoryType, Transaction
from app.repositories.category_repository import (
    CategoryRepository,
    get_category_repository,
)
from app.repositories.transaction_repository import (
    TransactionRepository,
    get_transaction_repository,
)
from app.schemas.auth import UserRead
from app.schemas.transaction import (
    CreateTransactionRequest,
    TransactionListResponse,
    TransactionResponse,
    UpdateTransactionRequest,
)


class TransactionService:
    """Handles transaction creation, updates, and queries."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.transaction_repository = transaction_repository
        self.category_repository = category_repository

    def list_transactions(
        self,
        user: UserRead,
        *,
        page: int = 1,
        per_page: int = 10,
        category_type: Optional[str] = None,
    ) -> TransactionListResponse:
        """Return paginated transactions for the current user."""
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        parsed_type = self._parse_optional_type(category_type)

        items, total = self.transaction_repository.list_by_user(
            user.id,
            page=page,
            per_page=per_page,
            category_type=parsed_type,
        )
        pages = math.ceil(total / per_page) if total else 0
        return TransactionListResponse(
            items=[self._to_response(item) for item in items],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        )

    def get_transaction(self, user: UserRead, transaction_id: int) -> TransactionResponse:
        """Return a single transaction."""
        transaction = self._get_owned_transaction(user.id, transaction_id)
        return self._to_response(transaction)

    def create_transaction(
        self,
        user: UserRead,
        payload: CreateTransactionRequest,
    ) -> TransactionResponse:
        """Create a transaction after validation."""
        self._validate_transaction_date(payload.transaction_date)
        self._validate_category(user.id, payload.category_id)

        transaction = self.transaction_repository.create(
            user_id=user.id,
            amount=payload.amount,
            description=payload.description.strip(),
            transaction_date=payload.transaction_date,
            category_id=payload.category_id,
        )
        return self._to_response(transaction)

    def update_transaction(
        self,
        user: UserRead,
        transaction_id: int,
        payload: UpdateTransactionRequest,
    ) -> TransactionResponse:
        """Update a transaction owned by the current user."""
        transaction = self._get_owned_transaction(user.id, transaction_id)

        if (
            payload.amount is None
            and payload.description is None
            and payload.transaction_date is None
            and payload.category_id is None
        ):
            raise ValidationError("At least one field must be provided.")

        amount = payload.amount if payload.amount is not None else transaction.amount
        description = (
            payload.description.strip()
            if payload.description is not None
            else transaction.description
        )
        transaction_date = (
            payload.transaction_date
            if payload.transaction_date is not None
            else transaction.transaction_date
        )
        category_id = (
            payload.category_id
            if payload.category_id is not None
            else transaction.category_id
        )

        self._validate_transaction_date(transaction_date)
        self._validate_category(user.id, category_id)

        updated = self.transaction_repository.update(
            transaction,
            amount=amount,
            description=description,
            transaction_date=transaction_date,
            category_id=category_id,
        )
        return self._to_response(updated)

    def delete_transaction(self, user: UserRead, transaction_id: int) -> None:
        """Delete a transaction owned by the current user."""
        transaction = self._get_owned_transaction(user.id, transaction_id)
        self.transaction_repository.delete(transaction)

    def _get_owned_transaction(self, user_id: int, transaction_id: int) -> Transaction:
        """Return a transaction or raise if missing."""
        transaction = self.transaction_repository.get_by_id(transaction_id, user_id)
        if transaction is None:
            raise NotFoundError("Transaction not found.")
        return transaction

    def _validate_category(self, user_id: int, category_id: int) -> None:
        """Ensure the category exists and belongs to the user."""
        category = self.category_repository.get_by_id(category_id, user_id)
        if category is None:
            raise ValidationError("Invalid category selected.")

    @staticmethod
    def _validate_transaction_date(transaction_date: date) -> None:
        """Reject future-dated transactions."""
        if transaction_date > date.today():
            raise ValidationError("Transaction date cannot be in the future.")

    @staticmethod
    def _parse_optional_type(value: Optional[str]) -> Optional[CategoryType]:
        """Parse optional category type filter."""
        if value is None or value == "all":
            return None
        try:
            return CategoryType(value)
        except ValueError as exc:
            raise ValidationError("Type filter must be 'income', 'expense', or 'all'.") from exc

    @staticmethod
    def _to_response(transaction: Transaction) -> TransactionResponse:
        """Map ORM transaction to API schema."""
        if transaction.category is None:
            raise ValidationError("Transaction category is missing.")

        return TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            description=transaction.description,
            transaction_date=transaction.transaction_date,
            category_id=transaction.category_id,
            category_name=transaction.category.name,
            category_type=transaction.category.type.value,
            user_id=transaction.user_id,
            created_at=transaction.created_at,
        )


def get_transaction_service(
    db: Session = Depends(get_db),
) -> TransactionService:
    """Dependency factory for TransactionService."""
    return TransactionService(
        get_transaction_repository(db),
        get_category_repository(db),
    )
