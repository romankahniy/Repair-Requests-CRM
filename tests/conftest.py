import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.auth.utils import hash_password
from src.core.config import settings
from src.core.dependencies import get_db
from src.database.base import Base
from src.main import app
from src.users.models import User, UserRole

TEST_DATABASE_URL = f"{settings.database_url}_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        email="admin@test.com",
        password=hash_password("admin123"),
        full_name="Test Admin",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def worker_user(db_session: AsyncSession) -> User:
    user = User(
        email="worker@test.com",
        password=hash_password("worker123"),
        full_name="Test Worker",
        role=UserRole.WORKER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user: User) -> str:
    response = await client.post(
        "/auth/login",
        data={
            "username": admin_user.email,
            "password": "admin123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def worker_token(client: AsyncClient, worker_user: User) -> str:
    response = await client.post(
        "/auth/login",
        data={
            "username": worker_user.email,
            "password": "worker123",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
async def worker_headers(worker_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {worker_token}"}
