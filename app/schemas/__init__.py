"""Pydantic schemas for request/response validation."""
from app.schemas.token import Token, TokenPayload, RefreshTokenRequest
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
    UserResponse,
    UserLogin,
)
from app.schemas.client import (
    ClientBase,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
)
from app.schemas.product_category import (
    ProductCategoryBase,
    ProductCategoryCreate,
    ProductCategoryUpdate,
    ProductCategoryResponse,
)
from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from app.schemas.client_racket import (
    ClientRacketBase,
    ClientRacketCreate,
    ClientRacketUpdate,
    ClientRacketResponse,
)
from app.schemas.maintenance_record import (
    MaintenanceRecordBase,
    MaintenanceRecordCreate,
    MaintenanceRecordUpdate,
    MaintenanceRecordResponse,
)

__all__ = [
    # Token schemas
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserUpdatePassword",
    "UserResponse",
    "UserLogin",
    # Client schemas
    "ClientBase",
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    # Product Category schemas
    "ProductCategoryBase",
    "ProductCategoryCreate",
    "ProductCategoryUpdate",
    "ProductCategoryResponse",
    # Product schemas
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    # Client Racket schemas
    "ClientRacketBase",
    "ClientRacketCreate",
    "ClientRacketUpdate",
    "ClientRacketResponse",
    # Maintenance Record schemas
    "MaintenanceRecordBase",
    "MaintenanceRecordCreate",
    "MaintenanceRecordUpdate",
    "MaintenanceRecordResponse",
]
