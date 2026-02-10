"""Authentication router for login, register, and token management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from app.utils.exceptions import UnauthorizedException, ConflictException
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Password (min 8 characters)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **role**: User role (staff or admin)
    """
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise ConflictException("Username already registered")

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise ConflictException("Email already registered")

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password to receive JWT tokens.

    - **username**: User's username
    - **password**: User's password

    Returns access and refresh tokens.
    """
    # Find user by username
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedException("Incorrect username or password")

    if not user.is_active:
        raise UnauthorizedException("User account is deactivated")

    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.

    - **refresh_token**: Valid refresh token

    Returns new access and refresh tokens.
    """
    payload = decode_token(refresh_data.refresh_token)

    if not payload:
        raise UnauthorizedException("Invalid or expired refresh token")

    if not verify_token_type(payload, "refresh"):
        raise UnauthorizedException("Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or deactivated")

    # Create new tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user.

    Requires valid JWT access token in Authorization header.
    """
    return current_user
