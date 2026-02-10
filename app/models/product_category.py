"""Product category model."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, String, DateTime, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class ProductCategory(Base):
    """Product category model (Racquets, Strings, Grips, etc.)."""

    __tablename__ = "product_categories"

    # Using String for UUID to ensure SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<ProductCategory {self.name}>"
