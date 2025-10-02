import pytest
from sqlalchemy import select

from typing import TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.base_repository import BaseRepository



from backend.database.base import Base

from sqlalchemy import String, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

class TestEntity(Base):
    __tablename__ = "test_entities"
    __table_args__ = (UniqueConstraint("name", name="uq_test_entities_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


T = TypeVar("T")

class TestEntityRepository(BaseRepository[TestEntity]):
    pass


@pytest.fixture()
def repo() -> TestEntityRepository:
    return TestEntityRepository()


class TestBaseRepository:
    @pytest.mark.asyncio
    async def test_create_one_success(self, repo: TestEntityRepository, db_session: AsyncSession):
        created = await repo.create_one(db_session, name="Alice", age=30)
        assert created.id is not None
        assert created.name == "Alice"
        assert created.age == 30

        rows = (await db_session.scalars(select(TestEntity))).all()
        assert len(rows) == 1

    @pytest.mark.asyncio
    async def test_create_one_duplicate_returns_none_and_rolls_back(self, repo: TestEntityRepository, db_session: AsyncSession):
        first = await repo.create_one(db_session, name="Fly Potato", age=20)
        assert first is not None

        dup = await repo.create_one(db_session, name="Fly Potato", age=99)
        assert dup is None

        rows = (await db_session.scalars(select(TestEntity))).all()
        assert len(rows) == 1
        assert rows[0].age == 20

    @pytest.mark.asyncio
    async def test_create_many_inserts_and_returns_pk(self, repo: TestEntityRepository, db_session: AsyncSession):
        rows = [
            {"name": "u1", "age": 1},
            {"name": "u2", "age": 2},
            {"name": "u3", "age": 3},
        ]
        pks = await repo.create_many(db_session, rows)
        assert len(pks) == 3
        assert all(isinstance(pk[0], int) for pk in pks)

        pks_again = await repo.create_many(db_session, rows)
        assert pks_again == []

        all_rows = (await db_session.scalars(select(TestEntity))).all()
        assert len(all_rows) == 3

    @pytest.mark.asyncio
    async def test_get_one_found_and_none(self, repo: TestEntityRepository, db_session: AsyncSession):
        await repo.create_one(db_session, name="X", age=10)
        item = await repo.get_one(db_session, name="X")
        assert item is not None
        assert item.name == "X"

        missing = await repo.get_one(db_session, name="nope")
        assert missing is None

    @pytest.mark.asyncio
    async def test_get_all_with_and_without_filters(self, repo: TestEntityRepository, db_session: AsyncSession):
        await repo.create_many(db_session, [
            {"name": "A", "age": 10},
            {"name": "B", "age": 20},
            {"name": "C", "age": 20},
        ])
        all_items = await repo.get_all(db_session)
        assert len(all_items) == 3

        only_20 = await repo.get_all(db_session, age=20)
        assert {x.name for x in only_20} == {"B", "C"}

    @pytest.mark.asyncio
    async def test_update_one_updates_values(self, repo: TestEntityRepository, db_session: AsyncSession):
        created = await repo.create_one(db_session, name="Not Fly", age=25)
        await repo.update_one({"id": created.id}, db_session, age=26)
        updated = await repo.get_one(db_session, id=created.id)
        assert updated is not None
        assert updated.age == 26

    @pytest.mark.asyncio
    async def test_delete_removes_rows(self, repo: TestEntityRepository, db_session: AsyncSession):
        await repo.create_one(db_session, name="Del", age=1)
        await repo.create_one(db_session, name="Keep", age=2)
        await repo.delete(db_session, name="Del")

        remaining = await repo.get_all(db_session)
        assert len(remaining) == 1
        assert remaining[0].name == "Keep"
