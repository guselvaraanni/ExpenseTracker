"""HTML page routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.dependencies import get_optional_user, get_templates, require_login
from app.schemas.auth import UserRead

router = APIRouter(tags=["pages"])


@router.get("/", include_in_schema=False)
async def root(
    current_user: Optional[UserRead] = Depends(get_optional_user),
) -> RedirectResponse:
    """Redirect to dashboard when logged in, otherwise to login."""
    if current_user is not None:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def dashboard(
    request: Request,
    current_user: UserRead = Depends(require_login),
) -> HTMLResponse:
    """Protected dashboard placeholder (metrics in a later phase)."""
    templates = get_templates()
    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={
            "page_title": "Dashboard",
            "active_page": "dashboard",
            "user_email": current_user.email,
        },
    )


@router.get("/expense", response_class=HTMLResponse, name="expense")
async def expense_page(
    request: Request,
    current_user: UserRead = Depends(require_login),
) -> HTMLResponse:
    """Add and manage transactions."""
    templates = get_templates()
    return templates.TemplateResponse(
        request=request,
        name="transactions/form.html",
        context={
            "page_title": "Add Expense",
            "active_page": "expense",
            "user_email": current_user.email,
        },
    )


@router.get("/reports", response_class=HTMLResponse, name="reports")
async def reports_page(
    request: Request,
    current_user: UserRead = Depends(require_login),
) -> HTMLResponse:
    """Reports placeholder (charts in a later phase)."""
    templates = get_templates()
    return templates.TemplateResponse(
        request=request,
        name="reports/index.html",
        context={
            "page_title": "Reports",
            "active_page": "reports",
            "user_email": current_user.email,
        },
    )


@router.get("/settings", response_class=HTMLResponse, name="settings")
async def settings_page(
    request: Request,
    current_user: UserRead = Depends(require_login),
) -> HTMLResponse:
    """Category and profile settings."""
    templates = get_templates()
    return templates.TemplateResponse(
        request=request,
        name="settings/index.html",
        context={
            "page_title": "Settings",
            "active_page": "settings",
            "user_email": current_user.email,
        },
    )
