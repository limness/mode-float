from src.database.models import RegionModel, UavFlightModel

from .base_repository import BaseRepository


class UavFlightRepository(BaseRepository[UavFlightModel]):
    """Repository for UavFlightModel model."""

    ...


class RegionRepository(BaseRepository[RegionModel]):
    """Repository for Region model."""

    ...


region_repo = RegionRepository()

uav_flight_repo = UavFlightRepository()
