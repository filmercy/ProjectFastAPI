"""Client racket schemas for request/response validation."""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
# UUID is now stored as string for SQLite compatibility
from pydantic import BaseModel, Field


class ClientRacketBase(BaseModel):
    """Base client racket schema."""

    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    custom_name: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    weight_unstrung: Optional[Decimal] = Field(None, ge=0)
    grip_size: str = Field(..., min_length=1)
    notes: Optional[str] = None


class ClientRacketCreate(ClientRacketBase):
    """Schema for creating a client racket."""

    client_id: str
    product_id: Optional[str] = None


class ClientRacketUpdate(BaseModel):
    """Schema for updating a client racket."""

    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    custom_name: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    weight_unstrung: Optional[Decimal] = Field(None, ge=0)
    grip_size: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientRacketResponse(ClientRacketBase):
    """Schema for client racket responses."""

    id: str
    client_id: str
    product_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
