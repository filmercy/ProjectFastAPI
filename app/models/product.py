"""Product model for inventory items."""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, Column, String, DateTime, Integer, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    """Product model for inventory (Racquets, Strings, Grips, etc.)."""

    __tablename__ = "products"

    # Using String for UUID to ensure SQLite compatibility
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    category_id = Column(String(36), ForeignKey("product_categories.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False, index=True)
    model = Column(String, nullable=True)
    sku = Column(String, unique=True, nullable=True)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)  # Retail price
    cost_price = Column(Numeric(10, 2), nullable=True)  # Cost for profit tracking
    quantity_in_stock = Column(Integer, default=0, nullable=False)
    image_url = Column(String, nullable=True)

    # JSONB field for flexible product-specific attributes
    # Example: {"gauge": "1.25mm", "color": "black", "material": "polyester"}
    specifications = Column(JSON, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("ProductCategory", back_populates="products")

    # Maintenance record relationships (products used in services)
    main_string_records = relationship("MaintenanceRecord", foreign_keys="MaintenanceRecord.main_string_id", back_populates="main_string")
    cross_string_records = relationship("MaintenanceRecord", foreign_keys="MaintenanceRecord.cross_string_id", back_populates="cross_string")
    base_grip_records = relationship("MaintenanceRecord", foreign_keys="MaintenanceRecord.base_grip_id", back_populates="base_grip")
    overgrip_records = relationship("MaintenanceRecord", foreign_keys="MaintenanceRecord.overgrip_id", back_populates="overgrip")
    dampener_records = relationship("MaintenanceRecord", foreign_keys="MaintenanceRecord.dampener_id", back_populates="dampener")

    def __repr__(self):
        return f"<Product {self.brand} {self.name}>"
