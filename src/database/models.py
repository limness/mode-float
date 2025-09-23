from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import expression

from .base import Base


class UavFlightModel(Base):
    __tablename__ = "uav_flights"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flight_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    uav_type: Mapped[str] = mapped_column(String(64), nullable=False)

    takeoff_lat: Mapped[float] = mapped_column(Float, nullable=False)
    takeoff_lon: Mapped[float] = mapped_column(Float, nullable=False)
    landing_lat: Mapped[float] = mapped_column(Float, nullable=False)
    landing_lon: Mapped[float] = mapped_column(Float, nullable=False)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    takeoff_region: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    landing_region: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    gc_distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_speed_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dow: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    is_weekend: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_holiday: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    __table_args__ = (
        CheckConstraint("takeoff_lat >= -90 AND takeoff_lat <= 90", name="ck_takeoff_lat_range"),
        CheckConstraint("landing_lat >= -90 AND landing_lat <= 90", name="ck_landing_lat_range"),
        CheckConstraint("takeoff_lon >= -180 AND takeoff_lon <= 180", name="ck_takeoff_lon_range"),
        CheckConstraint("landing_lon >= -180 AND landing_lon <= 180", name="ck_landing_lon_range"),
        CheckConstraint("duration_min >= 0", name="ck_duration_non_negative"),
        CheckConstraint("(month IS NULL) OR (month BETWEEN 1 AND 12)", name="ck_month_range"),
        CheckConstraint("(dow IS NULL) OR (dow BETWEEN 0 AND 6)", name="ck_dow_range"),
        CheckConstraint("(hour IS NULL) OR (hour BETWEEN 0 AND 23)", name="ck_hour_range"),
        Index(
            "ix_uav_flights_takeoff_point_gist",
            func.point(func.cast("takeoff_lon", Float), func.cast("takeoff_lat", Float)),
            postgresql_using="gist",
        ),
        Index(
            "ix_uav_flights_landing_point_gist",
            func.point(func.cast("landing_lon", Float), func.cast("landing_lat", Float)),
            postgresql_using="gist",
        ),
    )
