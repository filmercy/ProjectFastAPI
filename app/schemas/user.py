"""User schemas for request/response validation."""
from datetime import datetime
from typing import Optional
# UUID is now stored as string for SQLite compatibility
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = None
    role: UserRole = UserRole.STAFF


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserUpdatePassword(BaseModel):
    """Schema for updating user password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user responses."""

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str
