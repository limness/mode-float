from datetime import datetime
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import RegionModel, UavFlightModel
from backend.repositories.uav_repository import region_repo, uav_flight_repo
from backend.services.exceptions import RegionCreateError, UavFlightCreateError


async def create_region(
    db_session: AsyncSession,
    *,
    name: str,
    area: int,
    geopolygon,
    geopolygon_str: str,
    **extra: Any,
) -> RegionModel:
    """Create a new region.

    Args:
        db_session: Active async DB session.
        name: Region name.
        area: Region area (integer units).
        geopolygon: POLYGON geometry (SRID=4326).
        geopolygon_str: String representation of polygon (e.g., WKT/GeoJSON).
        **extra: Any additional mapped columns if later added.

    Returns:
        Region: Created region instance (persistent).

    Raises:
        RegionCreateError: On DB errors or constraint violations.
    """
    try:
        region = await region_repo.create_one(
            db_session,
            name=name,
            area=area,
            geopolygon=geopolygon,
            geopolygon_str=geopolygon_str,
            **extra,
        )
        return region
    except SQLAlchemyError as exc:
        raise RegionCreateError(f"Failed to create region '{name}': {exc}") from exc


async def create_uav_flight(
    db_session: AsyncSession,
    *,
    file_id: str | None = None,
    uav_type: str | None = None,
    takeoff_point=None,
    landing_point=None,
    coordinates=None,
    takeoff_lat: float | None = None,
    takeoff_lon: float | None = None,
    landing_lat: float | None = None,
    landing_lon: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    takeoff_datetime: datetime | None = None,
    landing_datetime: datetime | None = None,
    date: datetime | None = None,
    duration_minutes: int | None = None,
    city: str | None = None,
    major_region_id: int | None = None,
    takeoff_region_id: int | None = None,
    landing_region_id: int | None = None,
    distance_km: float | None = None,
    average_speed_kmh: float | None = None,
    **extra: Any,
) -> UavFlightModel:
    """Create a UAV flight record.

    Args:
        db_session: Active async DB session.
        file_id: Optional associated file metadata UUID.
        uav_type: UAV type.
        takeoff_point: SRID 4326 point.
        landing_point: SRID 4326 point.
        coordinates: SRID 4326 point (generic).
        takeoff_lat: Takeoff latitude.
        takeoff_lon: Takeoff longitude.
        landing_lat: Landing latitude.
        landing_lon: Landing longitude.
        latitude: Generic latitude.
        longitude: Generic longitude.
        takeoff_datetime: Takeoff datetime (tz-aware recommended).
        landing_datetime: Landing datetime (tz-aware recommended).
        date: General flight date (tz-aware recommended).
        duration_minutes: Flight duration in minutes (>= 0).
        city: City name.
        major_region_id: Major region FK.
        takeoff_region_id: Takeoff region FK.
        landing_region_id: Landing region FK.
        distance_km: Flight distance.
        average_speed_kmh: Average speed.
        **extra: Future-proof extra mapped columns.

    Returns:
        UavFlightModel: Created flight.

    Raises:
        UavFlightCreateError: On DB errors or constraint violations.
    """
    try:
        flight = await uav_flight_repo.create_one(
            db_session,
            file_id=file_id,
            uav_type=uav_type,
            takeoff_point=takeoff_point,
            landing_point=landing_point,
            coordinates=coordinates,
            takeoff_lat=takeoff_lat,
            takeoff_lon=takeoff_lon,
            landing_lat=landing_lat,
            landing_lon=landing_lon,
            latitude=latitude,
            longitude=longitude,
            takeoff_datetime=takeoff_datetime,
            landing_datetime=landing_datetime,
            date=date,
            duration_minutes=duration_minutes,
            city=city,
            major_region_id=major_region_id,
            takeoff_region_id=takeoff_region_id,
            landing_region_id=landing_region_id,
            distance_km=distance_km,
            average_speed_kmh=average_speed_kmh,
            **extra,
        )
        return flight
    except SQLAlchemyError as exc:
        raise UavFlightCreateError(f'Failed to create UAV flight: {exc}') from exc


async def get_uav_date_bounds(db_session: AsyncSession):
    try:
        min_date, max_date = await uav_flight_repo.get_date_bounds(db_session)
        return min_date, max_date
    except SQLAlchemyError as exc:
        raise UavFlightCreateError(f'Failed to get date bounds: {exc}') from exc
