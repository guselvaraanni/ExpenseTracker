"""Category ORM model."""

from __future__ import annotations

import enum
from typing import List

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CategoryType(str, enum.Enum):
    """Whether a category tracks income or expense."""

    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """User-owned transaction category."""

    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_categories_user_id_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType, name="category_type", native_enum=False),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="categories")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="category",
    )
