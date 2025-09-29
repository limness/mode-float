from datetime import datetime
from typing import Optional
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RegionModel(Base):
    __tablename__ = 'regions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    area: Mapped[int] = mapped_column(Integer, nullable=False)
    geopolygon: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type='POLYGON', srid=4326), nullable=False
    )
    geopolygon_str: Mapped[str] = mapped_column(Text, nullable=False)

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

    __table_args__ = (Index('idx_regions_geopolygon', 'geopolygon', postgresql_using='gist'),)


class UavFlightModel(Base):
    __tablename__ = 'uav_flights'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flight_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=True)
    file_id: Mapped[UUID] = mapped_column(ForeignKey('file_metadata.file_id'), nullable=True)
    uav_type: Mapped[str] = mapped_column(String(64), nullable=True)
    takeoff_point: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type='POINT', srid=4326), nullable=True
    )
    landing_point: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type='POINT', srid=4326), nullable=True
    )
    coordinates: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type='POINT', srid=4326), nullable=True
    )
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
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    major_region_id: Mapped[Optional[int]] = mapped_column(ForeignKey('regions.id'), nullable=True)
    takeoff_region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('regions.id'), nullable=True
    )
    landing_region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('regions.id'), nullable=True
    )
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_speed_kmh: Mapped[float | None] = mapped_column(Float, nullable=True)

    takeoff_region: Mapped[Optional['RegionModel']] = relationship(
        'RegionModel', foreign_keys=[takeoff_region_id], back_populates='takeoff_flights'
    )
    landing_region: Mapped[Optional['RegionModel']] = relationship(
        'RegionModel', foreign_keys=[landing_region_id], back_populates='landing_flights'
    )

    __table_args__ = (
        CheckConstraint('duration_minutes >= 0', name='ck_duration_non_negative'),
        Index('idx_uav_flights_takeoff_point', 'takeoff_point', postgresql_using='gist'),
        Index('idx_uav_flights_landing_point', 'landing_point', postgresql_using='gist'),
        Index('idx_uav_flights_coordinates', 'coordinates', postgresql_using='gist'),
    )


class FileMetadataModel(Base):
    __tablename__ = 'file_metadata'

    file_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename: Mapped[str] = mapped_column(String(256), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(String(128), nullable=False)
    sheet_names: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,
        default=True,
    )
