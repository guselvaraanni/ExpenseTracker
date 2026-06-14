from __future__ import annotations

"""User profile API routes — profile and salary (Phase 2+)."""

from typing import Dict

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas.auth import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/status")
async def users_status(
    current_user: UserRead = Depends(get_current_user),
) -> Dict[str, str]:
    """Placeholder endpoint — requires authentication."""
    return {
        "status": "users router ready",
        "phase": "auth",
        "user": current_user.email,
    }


@router.get("/me", response_model=UserRead)
async def read_current_user(
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    """Return the currently authenticated user."""
    return current_user
