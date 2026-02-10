"""User model for shop staff and admin."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enum."""
    ADMIN = "admin"
    STAFF = "staff"


class User(Base):
    """User model for shop staff and administrators."""

    __tablename__ = "users"

    # Using String for UUID to ensure SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STAFF)
    is_active = Column(Boolean, default=True, nullable=False)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    maintenance_records = relationship("MaintenanceRecord", back_populates="performed_by_user")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
