from datetime import datetime
from typing import Optional

from geoalchemy2 import Geometry
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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from .base import Base


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    area: Mapped[int] = mapped_column(Integer, nullable=False)
    geopolygon: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=False
    )

    takeoff_flights: Mapped[list["UavFlightModel"]] = relationship(
        "UavFlightModel", foreign_keys="UavFlightModel.takeoff_region_id", back_populates="takeoff_region"
    )
    landing_flights: Mapped[list["UavFlightModel"]] = relationship(
        "UavFlightModel", foreign_keys="UavFlightModel.landing_region_id", back_populates="landing_region"
    )

    __table_args__ = (
        Index("ix_regions_geopolygon_gist",
              "geopolygon", postgresql_using="gist"),
    )


class UavFlightModel(Base):
    __tablename__ = "uav_flights"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flight_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)
    uav_type: Mapped[str] = mapped_column(String(64), nullable=True)

    takeoff_point: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    landing_point: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    coordinates: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )
    root_points: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="MULTIPOINT", srid=4326), nullable=True
    )

    takeoff_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    landing_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    takeoff_region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("regions.id"), nullable=True
    )
    landing_region_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("regions.id"), nullable=True
    )

    distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    average_speed_kmh: Mapped[Optional[float]
                              ] = mapped_column(Float, nullable=True)

    takeoff_region: Mapped[Optional["Region"]] = relationship(
        "Region", foreign_keys=[takeoff_region_id], back_populates="takeoff_flights"
    )
    landing_region: Mapped[Optional["Region"]] = relationship(
        "Region", foreign_keys=[landing_region_id], back_populates="landing_flights"
    )

    __table_args__ = (
        CheckConstraint("duration_seconds >= 0",
                        name="ck_duration_non_negative"),
        Index("ix_uav_flights_takeoff_point_gist",
              "takeoff_point", postgresql_using="gist"),
        Index("ix_uav_flights_landing_point_gist",
              "landing_point", postgresql_using="gist"),
        Index("ix_uav_flights_coordinates_gist",
              "coordinates", postgresql_using="gist"),
        Index("ix_uav_flights_root_points_gist",
              "root_points", postgresql_using="gist"),
    )
