from __future__ import annotations

"""Transaction Pydantic schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateTransactionRequest(BaseModel):
    """Payload for creating a transaction."""

    amount: Decimal = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)
    transaction_date: date
    category_id: int = Field(..., gt=0)


class UpdateTransactionRequest(BaseModel):
    """Payload for updating a transaction."""

    amount: Optional[Decimal] = Field(default=None, gt=0)
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    transaction_date: Optional[date] = None
    category_id: Optional[int] = Field(default=None, gt=0)


class TransactionResponse(BaseModel):
    """Transaction returned from API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    description: str
    transaction_date: date
    category_id: int
    category_name: str
    category_type: Literal["income", "expense"]
    user_id: int
    created_at: datetime


class TransactionListResponse(BaseModel):
    """Paginated transaction list."""

    items: List[TransactionResponse]
    total: int
    page: int
    per_page: int
    pages: int
