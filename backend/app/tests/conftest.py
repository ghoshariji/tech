import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.security.password import hash_password

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/inventory_test_db"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    repo = UserRepository(db)
    user = await repo.create({
        "full_name": "Test Admin",
        "email": "admin@test.com",
        "hashed_password": hash_password("Admin@123456"),
        "role": UserRole.ADMIN,
        "is_active": True,
        "is_verified": True,
    })
    await db.commit()
    return user


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, admin_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@123456",
    })
    return response.json()["data"]["access_token"]


@pytest_asyncio.fixture
def admin_headers(admin_token: str):
    return {"Authorization": f"Bearer {admin_token}"}
