from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import RegionModel, UavFlightModel
from backend.schemas.uav_schema import DateBoundsResponse

from .base_repository import BaseRepository


class UavFlightRepository(BaseRepository[UavFlightModel]):
    """Repository for UavFlightModel model."""

    async def get_date_bounds(self, db_session: AsyncSession):
        result = await db_session.execute(
            select(func.min(UavFlightModel.date), func.max(UavFlightModel.date))
        )
        min_date, max_date = result.first()
        return min_date, max_date

    async def get_flights_between_dates(self, db_session: AsyncSession, bounds: DateBoundsResponse):
        query = select(UavFlightModel).where(
            UavFlightModel.date >= bounds.min_date,
            UavFlightModel.date <= bounds.max_date,
        )
        result = await db_session.execute(query)
        flights = result.scalars().all()
        return flights


class RegionRepository(BaseRepository[RegionModel]):
    """Repository for Region model."""

    ...


region_repo = RegionRepository()

uav_flight_repo = UavFlightRepository()
