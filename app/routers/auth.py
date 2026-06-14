from __future__ import annotations

"""Authentication routes — login, signup, logout."""

from typing import Optional, Union

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.dependencies import get_optional_user, get_templates
from app.core.exceptions import UnauthorizedError, UserAlreadyExistsError
from app.schemas.auth import AuthStatusResponse, SignupRequest, UserRead
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(tags=["auth"])


@router.api_route(
    "/login",
    methods=["GET", "POST"],
    response_class=HTMLResponse,
    response_model=None,
    name="login",
)
async def login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: Optional[UserRead] = Depends(get_optional_user),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
) -> Union[HTMLResponse, RedirectResponse]:
    """Render login page or authenticate user."""
    if current_user is not None:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    templates = get_templates()
    error: Optional[str] = None

    if request.method == "POST":
        email = (username or "").strip()
        if not email or not password:
            error = "Email and password are required."
        else:
            try:
                user = auth_service.authenticate(email, password)
                auth_service.create_session(request, user)
                return RedirectResponse(
                    url="/dashboard",
                    status_code=status.HTTP_303_SEE_OTHER,
                )
            except UnauthorizedError as exc:
                error = exc.message

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"error": error},
    )


@router.api_route(
    "/signup",
    methods=["GET", "POST"],
    response_class=HTMLResponse,
    response_model=None,
    name="signup",
)
async def signup(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: Optional[UserRead] = Depends(get_optional_user),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    confirm_password: Optional[str] = Form(None, alias="confirm-password"),
) -> Union[HTMLResponse, RedirectResponse]:
    """Render signup page or register a new user."""
    if current_user is not None:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    templates = get_templates()
    error: Optional[str] = None

    if request.method == "POST":
        try:
            payload = SignupRequest(
                email=email or "",
                password=password or "",
                confirm_password=confirm_password or "",
            )
            auth_service.register(payload)
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        except PydanticValidationError as exc:
            error = exc.errors()[0]["msg"]
        except UserAlreadyExistsError as exc:
            error = exc.message

    return templates.TemplateResponse(
        request=request,
        name="auth/signup.html",
        context={"error": error},
    )


@router.post("/logout", name="logout")
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """Clear session and redirect to login."""
    auth_service.destroy_session(request)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout", name="logout_get")
async def logout_get(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> RedirectResponse:
    """Allow logout via GET for sidebar links."""
    auth_service.destroy_session(request)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/auth/status", response_model=AuthStatusResponse)
async def auth_status(
    current_user: Optional[UserRead] = Depends(get_optional_user),
) -> AuthStatusResponse:
    """Return current authentication status (JSON)."""
    if current_user is None:
        return AuthStatusResponse(authenticated=False, email=None)
    return AuthStatusResponse(authenticated=True, email=current_user.email)
