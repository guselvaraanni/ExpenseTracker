"""Integration tests for category CRUD."""

from fastapi.testclient import TestClient

from app.db.session import get_session_factory
from app.repositories.category_repository import CategoryRepository


def _get_food_category_id(auth_client: TestClient) -> int:
    response = auth_client.get("/api/v1/categories")
    assert response.status_code == 200
    food = next(item for item in response.json()["items"] if item["name"] == "Food")
    return food["id"]


def test_categories_require_auth(client: TestClient) -> None:
    """Category endpoints require authentication."""
    assert client.get("/api/v1/categories").status_code == 401


def test_default_categories_seeded(auth_client: TestClient) -> None:
    """Demo user receives default expense and income categories."""
    response = auth_client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 8
    names = {item["name"] for item in data["items"]}
    assert "Food" in names
    assert "Salary" in names


def test_create_category(auth_client: TestClient) -> None:
    """POST /api/v1/categories creates a category."""
    response = auth_client.post(
        "/api/v1/categories",
        json={"name": "Gifts", "type": "expense"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Gifts"
    assert data["type"] == "expense"


def test_create_duplicate_category_rejected(auth_client: TestClient) -> None:
    """Duplicate category names are rejected."""
    response = auth_client.post(
        "/api/v1/categories",
        json={"name": "Food", "type": "expense"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_category(auth_client: TestClient) -> None:
    """PUT /api/v1/categories/{id} updates a category."""
    category_id = _get_food_category_id(auth_client)
    response = auth_client.put(
        f"/api/v1/categories/{category_id}",
        json={"name": "Groceries", "type": "expense"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Groceries"


def test_delete_unused_category(auth_client: TestClient) -> None:
    """DELETE removes a category with no transactions."""
    create = auth_client.post(
        "/api/v1/categories",
        json={"name": "Temporary", "type": "expense"},
    )
    category_id = create.json()["id"]

    response = auth_client.delete(f"/api/v1/categories/{category_id}")
    assert response.status_code == 204


def test_delete_category_in_use_rejected(auth_client: TestClient) -> None:
    """Categories linked to transactions cannot be deleted."""
    category_id = _get_food_category_id(auth_client)
    auth_client.post(
        "/api/v1/transactions",
        json={
            "amount": "12.50",
            "description": "Lunch",
            "transaction_date": "2026-06-01",
            "category_id": category_id,
        },
    )

    response = auth_client.delete(f"/api/v1/categories/{category_id}")
    assert response.status_code == 400
    assert "transactions" in response.json()["detail"]


def test_signup_seeds_default_categories(client: TestClient) -> None:
    """New users receive default categories on registration."""
    response = client.post(
        "/signup",
        data={
            "email": "categories@example.com",
            "password": "secret123",
            "confirm-password": "secret123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    login = client.post(
        "/login",
        data={"username": "categories@example.com", "password": "secret123"},
        follow_redirects=False,
    )
    assert login.status_code == 303

    db = get_session_factory()()
    try:
        from app.repositories.user_repository import UserRepository

        user = UserRepository(db).get_by_email("categories@example.com")
        assert user is not None
        categories = CategoryRepository(db).list_by_user(user.id)
        assert len(categories) == 8
    finally:
        db.close()


def test_settings_page_renders(auth_client: TestClient) -> None:
    """GET /settings renders the category management page."""
    response = auth_client.get("/settings")
    assert response.status_code == 200
    assert "Categories" in response.text
    assert 'id="categories-table"' in response.text
