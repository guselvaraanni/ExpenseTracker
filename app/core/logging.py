"""Structured logging configuration."""

import logging
import sys

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure application-wide logging."""
    settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries in development
    if settings.is_development:
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("watchfiles").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)
