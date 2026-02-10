"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Tennis Shop Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    # SQLite for development (file-based, no setup needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///./tennis_shop.db"
    # PostgreSQL for production (uncomment and use when ready)
    # DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/tennis_shop_db"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours (work day)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB in bytes
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    UPLOAD_DIR: str = "app/static/uploads"

    # CORS (for frontend app)
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Email (for password reset)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@tennisshop.com"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Business Settings
    LOW_STOCK_THRESHOLD: int = 5
    DEFAULT_CURRENCY: str = "EUR"
    TIMEZONE: str = "Europe/Rome"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
