"""Shared FastAPI dependencies (templates, database session, auth)."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings
from app.core.exceptions import LoginRequiredRedirect
from app.schemas.auth import UserRead
from app.services.auth_service import AuthService, get_auth_service


@lru_cache
def get_templates() -> Jinja2Templates:
    """Return a cached Jinja2Templates instance."""
    settings = get_settings()
    return Jinja2Templates(directory=str(settings.templates_dir))


async def get_optional_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[UserRead]:
    """Return the current user if authenticated, otherwise None."""
    return auth_service.get_user_from_session(request)


async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    """Return the current user or raise HTTP 401 for API routes."""
    user = auth_service.get_user_from_session(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


async def require_login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    """Return the current user or raise redirect to login for HTML routes."""
    user = auth_service.get_user_from_session(request)
    if user is None:
        raise LoginRequiredRedirect()
    return user
