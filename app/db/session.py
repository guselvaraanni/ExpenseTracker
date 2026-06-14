"""Database session management."""

from __future__ import annotations

from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _build_engine() -> Engine:
    """Create a SQLAlchemy engine from application settings."""
    settings = get_settings()

    if settings.is_sqlite:
        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        future=True,
    )


def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_session_factory() -> sessionmaker:
    """Return the shared session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def reset_engine() -> None:
    """Reset engine and session factory (used in tests)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
