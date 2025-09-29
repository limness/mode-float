import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

from src.core.settings import postgres_settings

__all__ = ['Base', 'db_manager', 'get_database']


class DatabaseManager:
    def __init__(self, database_url: str) -> None:
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=10,
            pool_recycle=1800,
            max_overflow=0,
        )
        self.async_session = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )


async def get_database() -> AsyncGenerator[AsyncSession | Any, None]:
    async with db_manager.async_session() as session:
        async with session.begin():
            try:
                yield session
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                raise Exception(f'Database error. Detail: {traceback.format_exc()}')
            finally:
                await session.close()


db_manager = DatabaseManager(postgres_settings.POSTGRES_URI)
Base = declarative_base()
