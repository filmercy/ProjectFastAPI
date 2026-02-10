"""Client schemas for request/response validation."""
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
# UUID is now stored as string for SQLite compatibility
from pydantic import BaseModel, EmailStr, Field


class ClientBase(BaseModel):
    """Base client schema with common fields."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: str = Field(..., min_length=1)
    date_of_birth: Optional[date] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    """Schema for creating a new client."""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating a client."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=1)
    date_of_birth: Optional[date] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    """Schema for client responses."""

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RacketDataForClient(BaseModel):
    """Schema for racket data when creating with client (no client_id needed)."""

    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    custom_name: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    weight_unstrung: Optional[Decimal] = Field(None, ge=0)
    grip_size: str = Field(..., min_length=1)
    product_id: Optional[str] = None
    notes: Optional[str] = None


class ClientWithRacketsCreate(ClientBase):
    """Schema for creating a client with optional rackets."""

    rackets: Optional[List[RacketDataForClient]] = Field(default_factory=list)


class ClientWithRacketsResponse(ClientResponse):
    """Schema for client with rackets response."""

    rackets: List[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True
