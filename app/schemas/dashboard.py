from __future__ import annotations

"""Dashboard schemas — implemented in Phase 2+."""

from decimal import Decimal

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    """Dashboard summary card data."""

    total_balance: Decimal
    income: Decimal
    expense_total: Decimal
    category_expense: dict[str, Decimal]
    recent_transactions: list[dict]


class ChartData(BaseModel):
    """Monthly chart data."""

    months: list[str]
    income: list[float]
    expenses: list[float]
    category_expense: dict[str, float]
