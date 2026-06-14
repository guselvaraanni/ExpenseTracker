from __future__ import annotations

"""User profile schemas — implemented in Phase 2+."""

from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class ProfileUpdate(BaseModel):
    """Profile update payload."""

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None


class SalaryUpdate(BaseModel):
    """Salary update payload."""

    salary: Decimal = Field(..., ge=0)


class ProfileResponse(BaseModel):
    """Profile update response."""

    success: bool
    message: str
