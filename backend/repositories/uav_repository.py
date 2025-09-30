from backend.database.models import RegionModel, UavFlightModel

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .base_repository import BaseRepository


class UavFlightRepository(BaseRepository[UavFlightModel]):
    """Repository for UavFlightModel model."""

    async def get_date_bounds(self, db_session: AsyncSession):
        result = await db_session.execute(
            select(func.min(UavFlightModel.date), func.max(UavFlightModel.date))
        )
        min_date, max_date = result.first()
        return min_date, max_date


class RegionRepository(BaseRepository[RegionModel]):
    """Repository for Region model."""

    ...


region_repo = RegionRepository()

uav_flight_repo = UavFlightRepository()
