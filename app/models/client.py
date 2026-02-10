"""Client model for tennis shop customers."""
import uuid
from datetime import datetime, date
from sqlalchemy import Boolean, Column, String, DateTime, Date
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    """Client model for tennis shop customers."""

    __tablename__ = "clients"

    # Using String for UUID to ensure SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    phone_number = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=True)
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    notes = Column(String, nullable=True)  # Special preferences or notes
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    rackets = relationship("ClientRacket", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.first_name} {self.last_name}>"
