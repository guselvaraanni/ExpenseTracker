from __future__ import annotations

"""
FastAPI application entry point.

Creates the app, registers middleware, mounts static files, and includes routers.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.core.exceptions import AppException, LoginRequiredRedirect, NotFoundError
from app.core.logging import get_logger, setup_logging
from app.db.seed import seed_all
from app.db.session import get_session_factory
from app.routers import auth, categories, dashboard, pages, reports, transactions, users

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown lifecycle hooks."""
    settings = get_settings()
    setup_logging()
    db = get_session_factory()()
    try:
        seed_all(db)
        logger.info("Database seed completed")
    except Exception as exc:
        logger.error("Database seed failed: %s", exc)
        raise
    finally:
        db.close()

    logger.info("Starting %s [%s]", settings.app_name, settings.app_env)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Personal expense tracking application",
        version="0.1.0",
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie=settings.session_cookie_name,
        max_age=settings.session_max_age,
        same_site="lax",
        https_only=not settings.is_development,
    )

    app.mount(
        "/static",
        StaticFiles(directory=str(settings.static_dir)),
        name="static",
    )

    app.include_router(pages.router)
    app.include_router(auth.router)
    app.include_router(transactions.router, prefix="/api/v1")
    app.include_router(dashboard.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")
    app.include_router(categories.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")

    @app.get("/health", tags=["system"])
    async def health_check() -> Dict[str, str]:
        """Health check endpoint for monitoring and verification."""
        return {
            "status": "ok",
            "app": settings.app_name,
            "environment": settings.app_env,
        }

    @app.exception_handler(LoginRequiredRedirect)
    async def login_required_handler(
        request: Request,
        exc: LoginRequiredRedirect,
    ) -> RedirectResponse:
        """Redirect unauthenticated HTML requests to login."""
        return RedirectResponse(url="/login", status_code=303)

    @app.exception_handler(NotFoundError)
    async def not_found_handler(
        request: Request,
        exc: NotFoundError,
    ) -> JSONResponse:
        """Handle missing resources."""
        logger.warning("NotFoundError on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message},
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Handle custom application exceptions."""
        logger.warning("AppException on %s: %s", request.url.path, exc.message)
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message},
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    _settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=_settings.host,
        port=_settings.port,
        reload=_settings.debug,
    )
