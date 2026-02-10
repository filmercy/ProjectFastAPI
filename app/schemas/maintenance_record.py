"""Maintenance record schemas for request/response validation."""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
# UUID is now stored as string for SQLite compatibility
from pydantic import BaseModel, Field

from app.models.maintenance_record import ServiceType


class MaintenanceRecordBase(BaseModel):
    """Base maintenance record schema."""

    service_type: ServiceType
    service_cost: Decimal = Field(..., ge=0)

    # String configuration
    main_string_id: Optional[str] = None
    cross_string_id: Optional[str] = None
    main_tension_kg: Optional[Decimal] = Field(None, ge=0, le=50)
    cross_tension_kg: Optional[Decimal] = Field(None, ge=0, le=50)
    string_pattern: Optional[str] = None

    # Grip configuration
    base_grip_id: Optional[str] = None
    overgrip_id: Optional[str] = None
    number_of_overgrips: int = Field(1, ge=0, le=10)

    # Dampener
    dampener_id: Optional[str] = None
    dampener_position: Optional[str] = None

    # Service details
    duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    is_warranty_service: bool = False
    next_service_due_date: Optional[date] = None


class MaintenanceRecordCreate(MaintenanceRecordBase):
    """Schema for creating a maintenance record."""

    client_racket_id: str
    service_date: Optional[datetime] = None  # If not provided, use current time


class MaintenanceRecordUpdate(BaseModel):
    """Schema for updating a maintenance record."""

    service_type: Optional[ServiceType] = None
    service_cost: Optional[Decimal] = Field(None, ge=0)

    main_string_id: Optional[str] = None
    cross_string_id: Optional[str] = None
    main_tension_kg: Optional[Decimal] = Field(None, ge=0, le=50)
    cross_tension_kg: Optional[Decimal] = Field(None, ge=0, le=50)
    string_pattern: Optional[str] = None

    base_grip_id: Optional[str] = None
    overgrip_id: Optional[str] = None
    number_of_overgrips: Optional[int] = Field(None, ge=0, le=10)

    dampener_id: Optional[str] = None
    dampener_position: Optional[str] = None

    duration_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    is_warranty_service: Optional[bool] = None
    next_service_due_date: Optional[date] = None


class MaintenanceRecordResponse(MaintenanceRecordBase):
    """Schema for maintenance record responses."""

    id: str
    client_racket_id: str
    performed_by_user_id: str
    service_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
