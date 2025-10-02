import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from backend.core.settings import postgres_settings
from backend.database.base import Base
from backend.main import create_app


@pytest.fixture(scope='session', autouse=True)
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def async_engine():
    engine = create_async_engine(postgres_settings.POSTGRES_URI, poolclass=NullPool, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    Session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.rollback()


@pytest.fixture(autouse=True, scope='session')
def app() -> FastAPI:
    return create_app()


@pytest.fixture(scope='session')
async def cli(app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://localhost:8000') as ac:
        ac.headers = {'Authorization': f'Bearer {"TEST_AUTH_TOKEN"}'}
        yield ac
