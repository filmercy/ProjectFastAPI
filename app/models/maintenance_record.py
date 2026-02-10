"""Maintenance record model for stringing history and services."""
import uuid
from datetime import datetime, date
from decimal import Decimal
import enum
from sqlalchemy import Boolean, Column, String, DateTime, Date, Numeric, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class ServiceType(str, enum.Enum):
    """Service type enum."""
    STRINGING = "stringing"
    REPAIR = "repair"
    OTHER = "other"


class MaintenanceRecord(Base):
    """Maintenance record for racket stringing and services."""

    __tablename__ = "maintenance_records"

    # Using String for UUID to ensure SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    client_racket_id = Column(String(36), ForeignKey("client_rackets.id"), nullable=False, index=True)
    performed_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    service_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    service_type = Column(Enum(ServiceType), nullable=False, default=ServiceType.STRINGING)

    # STRING CONFIGURATION
    main_string_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    cross_string_id = Column(String(36), ForeignKey("products.id"), nullable=True)  # Can be different from mains
    main_tension_kg = Column(Numeric(5, 2), nullable=True)  # e.g., 24.5 kg
    cross_tension_kg = Column(Numeric(5, 2), nullable=True)  # e.g., 23.0 kg
    string_pattern = Column(String, nullable=True)  # e.g., "16x19"

    # GRIP CONFIGURATION
    base_grip_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    overgrip_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    number_of_overgrips = Column(Integer, default=1, nullable=False)

    # ADDITIONAL ACCESSORIES
    dampener_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    dampener_position = Column(String, nullable=True)  # e.g., "center", "bottom"

    # SERVICE DETAILS
    service_cost = Column(Numeric(10, 2), nullable=False)  # Cost charged to client
    duration_minutes = Column(Integer, nullable=True)  # How long the service took
    notes = Column(String, nullable=True)  # Any special requests or observations
    is_warranty_service = Column(Boolean, default=False, nullable=False)
    next_service_due_date = Column(Date, nullable=True)  # Estimated next service date

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    racket = relationship("ClientRacket", back_populates="maintenance_records")
    performed_by_user = relationship("User", back_populates="maintenance_records")

    # Product relationships (products used in this service)
    main_string = relationship("Product", foreign_keys=[main_string_id], back_populates="main_string_records")
    cross_string = relationship("Product", foreign_keys=[cross_string_id], back_populates="cross_string_records")
    base_grip = relationship("Product", foreign_keys=[base_grip_id], back_populates="base_grip_records")
    overgrip = relationship("Product", foreign_keys=[overgrip_id], back_populates="overgrip_records")
    dampener = relationship("Product", foreign_keys=[dampener_id], back_populates="dampener_records")

    def __repr__(self):
        return f"<MaintenanceRecord {self.service_type} on {self.service_date} - Racket: {self.client_racket_id}>"
