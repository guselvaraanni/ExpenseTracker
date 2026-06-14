from __future__ import annotations

"""Category API routes."""

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.category import (
    CategoryListResponse,
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from app.services.category_service import CategoryService, get_category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    current_user: UserRead = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryListResponse:
    """List all categories for the current user."""
    return service.list_categories(current_user)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CreateCategoryRequest,
    current_user: UserRead = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Create a new category."""
    return service.create_category(current_user, payload)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    payload: UpdateCategoryRequest,
    current_user: UserRead = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Update an existing category."""
    return service.update_category(current_user, category_id, payload)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: UserRead = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> None:
    """Delete a category."""
    service.delete_category(current_user, category_id)
