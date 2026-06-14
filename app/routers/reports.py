from __future__ import annotations

"""Report API routes — filtered analytics (Phase 2+)."""

from typing import Dict

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas.auth import UserRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/status")
async def reports_status(
    current_user: UserRead = Depends(get_current_user),
) -> Dict[str, str]:
    """Placeholder endpoint — requires authentication."""
    return {
        "status": "reports router ready",
        "phase": "auth",
        "user": current_user.email,
    }
