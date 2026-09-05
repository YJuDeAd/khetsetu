from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.models.base import Base


@pytest.fixture
def test_client() -> TestClient:
    """Synchronous test client suitable for WebSocket testing."""
    return TestClient(app)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """In-memory async session with PRAGMA foreign_keys=ON for constraint tests."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    @event.listens_for(test_engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def async_client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous test client for HTTP endpoint testing with test DB session."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
    app.dependency_overrides.clear()
