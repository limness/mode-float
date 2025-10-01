import logging
from typing import Any

from dateutil.parser import isoparse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import RegionModel, UavFlightModel
from backend.dto import UavFlightCreateDTO
from backend.repositories.uav_repository import region_repo, uav_flight_repo
from backend.schemas.uav_schema import DateBoundsQuery, DateBoundsResponse
from backend.services.exceptions import RegionCreateError, UavFlightCreateError

logger = logging.getLogger(__name__)


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


async def create_uav_flights(
    db_session: AsyncSession,
    data: list[UavFlightCreateDTO],
) -> UavFlightModel | None:
    """Create a UAV flight record.

    Args:
        db_session: Active async DB session.
        data: Data for creation UAV

    Returns:
        UavFlightModel: Created flight.

    Raises:
        UavFlightCreateError: On DB errors or constraint violations.
    """
    try:
        flight = await uav_flight_repo.create_many(db_session, data)
    except IntegrityError as exc:
        logger.error(f'Failed to create UAV flight due to duplicate value: {exc}')
        return None
    except SQLAlchemyError as exc:
        raise UavFlightCreateError(f'Failed to create UAV flight: {exc}') from exc
    return flight


async def get_uav_date_bounds(db_session: AsyncSession):
    try:
        min_date, max_date = await uav_flight_repo.get_date_bounds(db_session)
        return min_date, max_date
    except SQLAlchemyError as exc:
        raise UavFlightCreateError(f'Failed to get date bounds: {exc}') from exc


async def get_uav_flights_between_dates(
    db_session: AsyncSession,
    *,
    query: DateBoundsQuery,
):
    try:
        if not query.min_date or not query.max_date:
            raise ValueError('Date bounds for search are not set')
        min_db, max_db = await uav_flight_repo.get_date_bounds(db_session)
        if min_db is None or max_db is None:
            raise ValueError('Date bounds for search are not set')
        min_user = isoparse(query.min_date)
        max_user = isoparse(query.max_date)
        if min_user < min_db or max_user > max_db:
            raise ValueError(
                f'Search bounds ({query.min_date} - {query.max_date}) are outside the allowed range ({min_db} - {max_db})'
            )
        limit = query.limit
        if limit is not None and limit <= 0:
            raise ValueError('Limit must be greater than zero')
        flights = await uav_flight_repo.get_flights_between_dates(
            db_session,
            start=min_user,
            end=max_user,
            limit=limit,
        )
        return [flight.__dict__ for flight in flights]
    except SQLAlchemyError as exc:
        raise UavFlightCreateError(f'Failed to get flights between dates: {exc}') from exc
