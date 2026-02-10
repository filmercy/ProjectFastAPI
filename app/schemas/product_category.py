"""Product category schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductCategoryBase(BaseModel):
    """Base product category schema."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    sort_order: int = 0


class ProductCategoryCreate(ProductCategoryBase):
    """Schema for creating a product category."""
    pass


class ProductCategoryUpdate(BaseModel):
    """Schema for updating a product category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(ProductCategoryBase):
    """Schema for product category responses."""

    id: str  # UUID stored as string for SQLite compatibility
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
