"""Transaction data access — PostgreSQL via SQLAlchemy."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models import Category, CategoryType, Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository):
    """CRUD operations for transactions."""

    def get_by_id(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        """Return a transaction owned by the given user."""
        return (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
            .first()
        )

    def list_by_user(
        self,
        user_id: int,
        *,
        page: int = 1,
        per_page: int = 10,
        category_type: Optional[CategoryType] = None,
    ) -> Tuple[List[Transaction], int]:
        """Return paginated transactions for a user."""
        query = (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(Transaction.user_id == user_id)
        )
        if category_type is not None:
            query = query.join(Category, Transaction.category).filter(
                Category.type == category_type
            )

        total = query.count()
        items = (
            query.order_by(
                Transaction.transaction_date.desc(),
                Transaction.id.desc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return items, total

    def count_by_category(self, category_id: int, user_id: int) -> int:
        """Return how many transactions use a category."""
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.category_id == category_id,
                Transaction.user_id == user_id,
            )
            .count()
        )

    def create(
        self,
        user_id: int,
        amount: Decimal,
        description: str,
        transaction_date: date,
        category_id: int,
    ) -> Transaction:
        """Create a transaction for a user."""
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            description=description,
            transaction_date=transaction_date,
            category_id=category_id,
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return self.get_by_id(transaction.id, user_id)

    def update(
        self,
        transaction: Transaction,
        *,
        amount: Decimal,
        description: str,
        transaction_date: date,
        category_id: int,
    ) -> Transaction:
        """Update an existing transaction."""
        transaction.amount = amount
        transaction.description = description
        transaction.transaction_date = transaction_date
        transaction.category_id = category_id
        self.db.commit()
        self.db.refresh(transaction)
        return self.get_by_id(transaction.id, transaction.user_id)

    def delete(self, transaction: Transaction) -> None:
        """Delete a transaction."""
        self.db.delete(transaction)
        self.db.commit()


def get_transaction_repository(db: Session) -> TransactionRepository:
    """Factory for request-scoped transaction repository."""
    return TransactionRepository(db)
