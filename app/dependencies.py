"""FastAPI dependencies for authentication and authorization."""
from typing import Optional
from uuid import UUID
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.security import decode_token, verify_token_type
from app.utils.exceptions import UnauthorizedException, ForbiddenException


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        authorization: The Authorization header with Bearer token
        db: Database session

    Returns:
        The authenticated user

    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        raise UnauthorizedException("Invalid or expired token")

    if not verify_token_type(payload, "access"):
        raise UnauthorizedException("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    # Validate UUID format
    try:
        UUID(user_id)  # Just validate format
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid user ID format")

    # Fetch user from database (ID is stored as string for SQLite compatibility)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is deactivated")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.

    Args:
        current_user: The current authenticated user

    Returns:
        The active user
    """
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require the current user to be an admin.

    Args:
        current_user: The current authenticated user

    Returns:
        The admin user

    Raises:
        ForbiddenException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required")

    return current_user
