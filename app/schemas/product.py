"""Product schemas for request/response validation."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
# UUID is now stored as string for SQLite compatibility
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema."""

    name: str = Field(..., min_length=1, max_length=200)
    brand: str = Field(..., min_length=1, max_length=100)
    model: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    specifications: Optional[Dict[str, Any]] = None


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    category_id: str  # UUID stored as string for SQLite compatibility
    quantity_in_stock: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    quantity_in_stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[str] = None  # UUID stored as string for SQLite compatibility
    specifications: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product responses."""

    id: str  # UUID stored as string for SQLite compatibility
    category_id: str
    quantity_in_stock: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
