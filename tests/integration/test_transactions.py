"""Integration tests for transaction CRUD."""

from datetime import date

from fastapi.testclient import TestClient


def _get_category_id(auth_client: TestClient, name: str) -> int:
    response = auth_client.get("/api/v1/categories")
    assert response.status_code == 200
    category = next(item for item in response.json()["items"] if item["name"] == name)
    return category["id"]


def test_transactions_require_auth(client: TestClient) -> None:
    """Transaction endpoints require authentication."""
    assert client.get("/api/v1/transactions").status_code == 401


def test_create_transaction(auth_client: TestClient) -> None:
    """POST /api/v1/transactions creates a transaction."""
    category_id = _get_category_id(auth_client, "Food")
    response = auth_client.post(
        "/api/v1/transactions",
        json={
            "amount": "25.00",
            "description": "Groceries",
            "transaction_date": "2026-06-10",
            "category_id": category_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Groceries"
    assert data["category_name"] == "Food"
    assert data["category_type"] == "expense"


def test_create_transaction_invalid_category(auth_client: TestClient) -> None:
    """Transactions reject categories that do not belong to the user."""
    response = auth_client.post(
        "/api/v1/transactions",
        json={
            "amount": "10.00",
            "description": "Bad category",
            "transaction_date": "2026-06-10",
            "category_id": 99999,
        },
    )
    assert response.status_code == 400
    assert "Invalid category" in response.json()["detail"]


def test_create_transaction_future_date_rejected(auth_client: TestClient) -> None:
    """Future transaction dates are rejected."""
    category_id = _get_category_id(auth_client, "Food")
    future = date.today().replace(year=date.today().year + 1).isoformat()
    response = auth_client.post(
        "/api/v1/transactions",
        json={
            "amount": "10.00",
            "description": "Future spend",
            "transaction_date": future,
            "category_id": category_id,
        },
    )
    assert response.status_code == 400
    assert "future" in response.json()["detail"].lower()


def test_list_transactions_with_pagination(auth_client: TestClient) -> None:
    """GET /api/v1/transactions supports pagination."""
    food_id = _get_category_id(auth_client, "Food")
    salary_id = _get_category_id(auth_client, "Salary")

    for index in range(3):
        auth_client.post(
            "/api/v1/transactions",
            json={
                "amount": f"{index + 1}.00",
                "description": f"Item {index}",
                "transaction_date": f"2026-06-{index + 1:02d}",
                "category_id": food_id,
            },
        )

    auth_client.post(
        "/api/v1/transactions",
        json={
            "amount": "1000.00",
            "description": "Paycheck",
            "transaction_date": "2026-06-05",
            "category_id": salary_id,
        },
    )

    page_one = auth_client.get("/api/v1/transactions?page=1&per_page=2")
    assert page_one.status_code == 200
    data = page_one.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2
    assert data["pages"] == 2

    expense_only = auth_client.get("/api/v1/transactions?type=expense")
    assert expense_only.status_code == 200
    assert expense_only.json()["total"] == 3


def test_get_update_delete_transaction(auth_client: TestClient) -> None:
    """Single transaction CRUD lifecycle works."""
    category_id = _get_category_id(auth_client, "Transport")
    create = auth_client.post(
        "/api/v1/transactions",
        json={
            "amount": "15.00",
            "description": "Bus fare",
            "transaction_date": "2026-06-08",
            "category_id": category_id,
        },
    )
    transaction_id = create.json()["id"]

    get_response = auth_client.get(f"/api/v1/transactions/{transaction_id}")
    assert get_response.status_code == 200
    assert get_response.json()["description"] == "Bus fare"

    update = auth_client.put(
        f"/api/v1/transactions/{transaction_id}",
        json={"description": "Updated fare", "amount": "16.50"},
    )
    assert update.status_code == 200
    assert update.json()["description"] == "Updated fare"

    delete = auth_client.delete(f"/api/v1/transactions/{transaction_id}")
    assert delete.status_code == 204

    missing = auth_client.get(f"/api/v1/transactions/{transaction_id}")
    assert missing.status_code == 404


def test_expense_page_renders(auth_client: TestClient) -> None:
    """GET /expense renders the transaction form and table."""
    response = auth_client.get("/expense")
    assert response.status_code == 200
    assert 'id="transaction-form"' in response.text
    assert 'id="transactions-table"' in response.text


def test_sidebar_navigation_links(auth_client: TestClient) -> None:
    """Protected pages expose working sidebar routes."""
    dashboard = auth_client.get("/dashboard")
    expense = auth_client.get("/expense")
    reports = auth_client.get("/reports")
    settings = auth_client.get("/settings")

    assert dashboard.status_code == 200
    assert expense.status_code == 200
    assert reports.status_code == 200
    assert settings.status_code == 200
    assert "/expense" in expense.text
    assert "/settings" in settings.text
