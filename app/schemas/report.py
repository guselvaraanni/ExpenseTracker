from __future__ import annotations

"""Report schemas — implemented in Phase 2+."""

from pydantic import BaseModel, Field


class ReportFilter(BaseModel):
    """Query parameters for report filtering."""

    range_days: int = Field(default=30, alias="range", ge=1, le=365)
    category: str = "All"


class ReportResponse(BaseModel):
    """Report API response."""

    months: list[str]
    income: list[float]
    expenses: list[float]
    category_expense: dict[str, float]
    transactions: list[dict]
