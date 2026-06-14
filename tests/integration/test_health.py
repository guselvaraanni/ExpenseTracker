"""Integration tests for application bootstrap."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Health endpoint returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Expense Tracker"


def test_root_redirects_to_login(client: TestClient) -> None:
    """Unauthenticated root redirects to login."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_protected_api_requires_auth(client: TestClient) -> None:
    """Protected API endpoints return 401 without a session."""
    endpoints = [
        "/api/v1/transactions",
        "/api/v1/dashboard/status",
        "/api/v1/reports/status",
        "/api/v1/categories",
        "/api/v1/users/me",
    ]

    for path in endpoints:
        response = client.get(path)
        assert response.status_code == 401


def test_protected_api_with_auth(auth_client: TestClient) -> None:
    """API status endpoints succeed when authenticated."""
    response = auth_client.get("/api/v1/dashboard/status")
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] == "auth"
    assert data["user"] == "test@example.com"
