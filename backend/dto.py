from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UavFlightCreateDTO(BaseModel):
    flight_id: str | None = None
    file_id: Optional[UUID] = None
    uav_type: str | None = None
    operator_name: str | None = None
    operator_type: str | None = None

    takeoff_lat: float | None = None
    takeoff_lon: float | None = None
    landing_lat: float | None = None
    landing_lon: float | None = None
    latitude: float | None = None
    longitude: float | None = None

    takeoff_datetime: datetime | None = None
    landing_datetime: datetime | None = None
    date: datetime | None = None

    duration_minutes: int | None = None
    city: str | None = None
    distance_km: float | None = None
    average_speed_kmh: float | None = None

    takeoff_region_id: int | None = None
    landing_region_id: int | None = None
    major_region_id: int | None = None
