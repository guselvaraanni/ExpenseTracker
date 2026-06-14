from __future__ import annotations

"""Transaction API routes — CRUD."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.transaction import (
    CreateTransactionRequest,
    TransactionListResponse,
    TransactionResponse,
    UpdateTransactionRequest,
)
from app.services.transaction_service import TransactionService, get_transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    type: Optional[str] = Query(default=None, alias="type"),
    current_user: UserRead = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionListResponse:
    """List transactions for the current user with pagination."""
    return service.list_transactions(
        current_user,
        page=page,
        per_page=per_page,
        category_type=type,
    )


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: CreateTransactionRequest,
    current_user: UserRead = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    """Create a new transaction."""
    return service.create_transaction(current_user, payload)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: UserRead = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    """Return a single transaction."""
    return service.get_transaction(current_user, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    payload: UpdateTransactionRequest,
    current_user: UserRead = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    """Update an existing transaction."""
    return service.update_transaction(current_user, transaction_id, payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: UserRead = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> None:
    """Delete a transaction."""
    service.delete_transaction(current_user, transaction_id)
