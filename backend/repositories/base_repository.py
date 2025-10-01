import logging
from typing import Any, Generic, List, Optional, TypeVar

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import Base

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository class for database operations.
    Provides common CRUD operations for all models.
    """

    __model__ = type[T]

    def __init__(self):
        # Get the actual model class from the generic type
        model = self.__orig_bases__[0].__args__[0]  # type: ignore
        if not isinstance(model, type) or not issubclass(model, Base):
            raise TypeError(f'Repository must be parameterized with a model class, got {model}')
        self.__model__ = model

    async def create_one(self, db_session: AsyncSession, **data: Any) -> T | None:
        """
        Create and persist a new instance of the model with the provided data.
        """
        statement = insert(self.__model__).values(data).returning(self.__model__)
        try:
            result = await db_session.execute(statement)
            await db_session.flush()
        except IntegrityError as ex:
            if not isinstance(ex.orig, UniqueViolationError):
                raise ex
            await db_session.rollback()
            logger.error(f'Failed to insert {self.__model__} due to duplicate key value!')
            return None
        # return self.get_one(db_session=db_session, **dict(result.inserted_primary_key))
        return result.scalars().one()

    async def create_many(self, db_session: AsyncSession, rows: list[Any]) -> set:
        """
        Create and persist a new instance of the model with the provided data.
        """
        saved_rows = set()
        for row in rows:
            nested_session = await db_session.begin_nested()
            statement = insert(self.__model__).values(row)
            try:
                result = await db_session.execute(statement)
                await db_session.flush()
                saved_rows.add(result)
            except IntegrityError as ex:
                if not isinstance(ex.orig, UniqueViolationError):
                    raise ex
                await nested_session.rollback()
                logger.error(f'Failed to insert {self.__model__} due to duplicate key value!')
            else:
                await nested_session.commit()
        return saved_rows

    async def delete(self, db_session: AsyncSession, **filters: Any) -> None:
        """
        Delete a record from the database matching the given filters.
        """
        await db_session.execute(delete(self.__model__).filter_by(**filters))
        await db_session.flush()

    async def get_one(self, db_session: AsyncSession, **filters: Any) -> Optional[T]:
        """
        Retrieve a single record matching the given filters, or None if not found.
        """
        row = await db_session.scalars(select(self.__model__).filter_by(**filters))
        return row.one_or_none()

    async def get_all(self, db_session: AsyncSession, **filters: Any) -> List[T]:
        """
        Retrieve all records matching the given filters.
        """
        row = await db_session.scalars(select(self.__model__).filter_by(**filters))
        return list(row.all())

    async def update_one(
        self,
        filters: dict[str, Any],
        db_session: AsyncSession,
        **values: Any,
    ) -> None:
        """
        Update a record matching the filters with the provided values.
        """
        await db_session.execute(update(self.__model__).filter_by(**filters).values(values))
        await db_session.flush()
