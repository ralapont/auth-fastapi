# tests/conftest.py
import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from app.core.db import get_session
from app.routers.users import router as user_router
from app.models.role import Role

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def seed_roles(async_session):
    async_session.add_all([
        Role(name="user"),
        Role(name="supervisor")
    ])
    await async_session.commit()
    return True

@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    # Crear tablas
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()

@pytest_asyncio.fixture
async def async_session(async_engine):
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with AsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def seed_roles(async_session: AsyncSession):
    """
    Si tu servicio register_user resuelve roles por nombre,
    asegúrate de que existan antes de llamar al endpoint.
    """
    # Crea los roles mínimos usados en los tests
    async_session.add_all([Role(name="user"), Role(name="supervisor")])
    await async_session.flush()
    await async_session.commit()
    return True

@pytest.fixture
def app(async_session: AsyncSession):
    """
    App de FastAPI con el router montado y el get_session override
    para que use la sesión async de pruebas.
    """
    app = FastAPI()
    app.include_router(user_router)

    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session
    return app