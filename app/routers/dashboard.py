from __future__ import annotations

"""Dashboard API routes — summary and chart data (Phase 2+)."""

from typing import Dict

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas.auth import UserRead

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/status")
async def dashboard_status(
    current_user: UserRead = Depends(get_current_user),
) -> Dict[str, str]:
    """Placeholder endpoint — requires authentication."""
    return {
        "status": "dashboard router ready",
        "phase": "auth",
        "user": current_user.email,
    }
