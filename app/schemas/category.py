from __future__ import annotations

"""Category Pydantic schemas."""

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


CategoryTypeLiteral = Literal["income", "expense"]


class CreateCategoryRequest(BaseModel):
    """Payload for creating a category."""

    name: str = Field(..., min_length=1, max_length=100)
    type: CategoryTypeLiteral


class UpdateCategoryRequest(BaseModel):
    """Payload for updating a category."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[CategoryTypeLiteral] = None


class CategoryResponse(BaseModel):
    """Category returned from API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: CategoryTypeLiteral
    user_id: int


class CategoryListResponse(BaseModel):
    """List of categories."""

    items: List[CategoryResponse]
    total: int
