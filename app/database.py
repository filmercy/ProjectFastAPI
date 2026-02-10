"""Database configuration and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine
# For SQLite: echo=True shows SQL queries in console (useful for debugging)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for all models
Base = declarative_base()


# Dependency to get database session
async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.

    Usage in FastAPI routes:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Function to create all tables (useful for development)
async def create_tables():
    """Create all database tables. Use Alembic migrations in production."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Function to drop all tables (useful for testing)
async def drop_tables():
    """Drop all database tables. Use with caution!"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
