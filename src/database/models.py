from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Region(Base):
    __tablename__ = 'regions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    area: Mapped[int] = mapped_column(Integer, nullable=False)
    geopolygon: Mapped[str] = mapped_column(Text, nullable=False)
    takeoff_flights: Mapped[list['UavFlightModel']] = relationship(
        'UavFlightModel',
        foreign_keys='UavFlightModel.takeoff_region_id',
        back_populates='takeoff_region',
    )
    landing_flights: Mapped[list['UavFlightModel']] = relationship(
        'UavFlightModel',
        foreign_keys='UavFlightModel.landing_region_id',
        back_populates='landing_region',
    )


class UavFlightModel(Base):
    __tablename__ = 'uav_flights'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flight_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=True)
    uav_type: Mapped[str] = mapped_column(String(64), nullable=True)
    takeoff_lat: Mapped[float] = mapped_column(Float, nullable=True)
    takeoff_lon: Mapped[float] = mapped_column(Float, nullable=True)
    landing_lat: Mapped[float] = mapped_column(Float, nullable=True)
    landing_lon: Mapped[float] = mapped_column(Float, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    takeoff_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    landing_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    major_region_id: Mapped[Optional[int]] = mapped_column(ForeignKey('regions.id'), nullable=True)
    takeoff_region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('regions.id'), nullable=True
    )
    landing_region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('regions.id'), nullable=True
    )
    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_speed_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    takeoff_region: Mapped[Optional['Region']] = relationship(
        'Region', foreign_keys=[takeoff_region_id], back_populates='takeoff_flights'
    )
    landing_region: Mapped[Optional['Region']] = relationship(
        'Region', foreign_keys=[landing_region_id], back_populates='landing_flights'
    )

    __table_args__ = (
        CheckConstraint('duration_minutes >= 0', name='ck_duration_non_negative'),
    )
