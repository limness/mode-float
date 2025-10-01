from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import RegionModel, UavFlightModel

from .base_repository import BaseRepository


class UavFlightRepository(BaseRepository[UavFlightModel]):
    """Repository for UavFlightModel model."""

    async def get_date_bounds(self, db_session: AsyncSession):
        result = await db_session.execute(
            select(func.min(UavFlightModel.date), func.max(UavFlightModel.date))
        )
        min_date, max_date = result.first()
        return min_date, max_date

    async def get_flights_between_dates(
        self,
        db_session: AsyncSession,
        *,
        start: datetime,
        end: datetime,
        limit: int | None = None,
    ):
        query = (
            select(UavFlightModel)
            .where(
                UavFlightModel.date >= start,
                UavFlightModel.date <= end,
            )
            .order_by(desc(UavFlightModel.date))
        )
        if limit is not None:
            query = query.limit(limit)
        result = await db_session.execute(query)
        flights = result.scalars().all()
        return flights


class RegionRepository(BaseRepository[RegionModel]):
    """Repository for Region model."""

    ...


region_repo = RegionRepository()

uav_flight_repo = UavFlightRepository()
