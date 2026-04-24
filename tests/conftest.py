"""
Shared test fixtures.

How it works:
- Each test gets a fresh in-memory SQLite database (via the `engine` fixture).
- StaticPool ensures all SQLAlchemy sessions within a test reuse the same
  underlying connection, so data seeded in one session is visible to requests
  made through the HTTP client.
- The `get_db` dependency is overridden to point at the test database instead
  of the real tennis_shop.db file.
"""
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from main import app  # importing app registers all models on Base.metadata

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# Hardcoded in maintenance.py — must exist in DB for maintenance records to save.
DEFAULT_USER_ID = "c4fa281e-11af-4510-82f6-509ae30ffc98"


@pytest_asyncio.fixture
async def engine():
    """Fresh in-memory database per test function."""
    _engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture
async def api_client(engine):
    """Async HTTP client wired to the test database."""
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with Session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seeded_user(engine):
    """
    Inserts the default admin user directly into the test DB.

    Maintenance records have a FK to users.id and the router hardcodes
    DEFAULT_USER_ID, so this row must exist before any maintenance record
    can be saved.
    """
    from app.models.user import User, UserRole

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        user = User(
            id=DEFAULT_USER_ID,
            email="admin@test.com",
            username="admin",
            hashed_password="fakehashed",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
        )
        session.add(user)
        await session.commit()
