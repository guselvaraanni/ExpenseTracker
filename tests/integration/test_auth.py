"""Integration tests for authentication flows."""

from fastapi.testclient import TestClient

from app.db.session import get_session_factory
from app.repositories.user_repository import UserRepository


def test_login_page_renders(client: TestClient) -> None:
    """GET /login returns the login form."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "Welcome Back!" in response.text
    assert 'name="username"' in response.text


def test_signup_page_renders(client: TestClient) -> None:
    """GET /signup returns the signup form."""
    response = client.get("/signup")
    assert response.status_code == 200
    assert "Create an Account" in response.text


def test_demo_user_login_success(client: TestClient) -> None:
    """Demo credentials create a session and redirect to dashboard."""
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "1234"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "test@example.com" in dashboard.text


def test_login_invalid_password(client: TestClient) -> None:
    """Invalid credentials show an error message."""
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "wrong"},
    )
    assert response.status_code == 200
    assert "Invalid email or password" in response.text


def test_signup_success(client: TestClient) -> None:
    """New user registration stores a hashed password and redirects to login."""
    response = client.post(
        "/signup",
        data={
            "email": "newuser@example.com",
            "password": "secret123",
            "confirm-password": "secret123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    db = get_session_factory()()
    try:
        user = UserRepository(db).get_by_email("newuser@example.com")
        assert user is not None
        assert user.password_hash != "secret123"
    finally:
        db.close()

    login = client.post(
        "/login",
        data={"username": "newuser@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    assert login.status_code == 303


def test_signup_duplicate_email(client: TestClient) -> None:
    """Duplicate signup returns an error."""
    response = client.post(
        "/signup",
        data={
            "email": "test@example.com",
            "password": "secret123",
            "confirm-password": "secret123",
        },
    )
    assert response.status_code == 200
    assert "User already exists" in response.text


def test_signup_password_mismatch(client: TestClient) -> None:
    """Mismatched passwords are rejected."""
    response = client.post(
        "/signup",
        data={
            "email": "user@example.com",
            "password": "secret123",
            "confirm-password": "different",
        },
    )
    assert response.status_code == 200
    assert "match" in response.text.lower()


def test_logout_clears_session(auth_client: TestClient) -> None:
    """Logout removes access to protected routes."""
    response = auth_client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    protected = auth_client.get("/dashboard", follow_redirects=False)
    assert protected.status_code == 303
    assert protected.headers["location"] == "/login"


def test_logout_get_clears_session(auth_client: TestClient) -> None:
    """GET /logout also clears the session."""
    response = auth_client.get("/logout", follow_redirects=False)
    assert response.status_code == 303

    assert auth_client.get("/api/v1/users/me").status_code == 401


def test_auth_status_unauthenticated(client: TestClient) -> None:
    """Auth status reports unauthenticated state."""
    response = client.get("/auth/status")
    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "email": None}


def test_auth_status_authenticated(auth_client: TestClient) -> None:
    """Auth status reports authenticated user email."""
    response = auth_client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["email"] == "test@example.com"


def test_users_me_endpoint(auth_client: TestClient) -> None:
    """GET /api/v1/users/me returns current user."""
    response = auth_client.get("/api/v1/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_dashboard_requires_login(client: TestClient) -> None:
    """Unauthenticated dashboard access redirects to login."""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
