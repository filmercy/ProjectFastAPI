"""Client racket model for rackets owned by clients."""
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Boolean, Column, String, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ClientRacket(Base):
    """Client racket model - rackets owned by tennis shop clients."""

    __tablename__ = "client_rackets"

    # Using String for UUID to ensure SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    client_id = Column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)  # If racket is in product catalog
    custom_name = Column(String, nullable=True)  # e.g., "My Wilson Pro Staff"
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    serial_number = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=True)
    weight_unstrung = Column(Numeric(10, 2), nullable=True)  # Weight in grams
    grip_size = Column(String, nullable=False)  # e.g., "4 1/4", "4 3/8"
    notes = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)  # If client still owns it
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("Client", back_populates="rackets")
    maintenance_records = relationship("MaintenanceRecord", back_populates="racket", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClientRacket {self.brand} {self.model} - Client: {self.client_id}>"
