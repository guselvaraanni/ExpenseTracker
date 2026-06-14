"""Pytest fixtures and test configuration."""

import os

# Use in-memory SQLite for tests before any app/database imports.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.seed import seed_demo_user
from app.db.session import get_session_factory, reset_engine
from app.models import Base, Category, Transaction, User, UserProfile

get_settings.cache_clear()
reset_engine()

from app.db.session import get_engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.create_all(bind=get_engine())


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_database() -> None:
    """Clear all rows and re-seed demo user before each test."""
    db = get_session_factory()()
    try:
        db.query(Transaction).delete()
        db.query(Category).delete()
        db.query(UserProfile).delete()
        db.query(User).delete()
        db.commit()
        seed_demo_user(db)
    finally:
        db.close()


@pytest.fixture
def auth_client(client: TestClient) -> TestClient:
    """Return a test client with an authenticated session."""
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "1234"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"
    return client


@pytest.fixture
def db_session():
    """Provide a database session for unit tests."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
