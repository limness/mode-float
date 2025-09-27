"""Add Region model and update UavFlightModel

Revision ID: efb5b4c0c473
Revises: e37f40e4e50f
Create Date: 2025-09-27 19:27:57.841927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = 'efb5b4c0c473'
down_revision: Union[str, None] = 'e37f40e4e50f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- таблица regions ---
    op.create_table(
        "regions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("area", sa.Integer(), nullable=False),
        sa.Column("geopolygon", Geometry(
            geometry_type="POLYGON", srid=4326), nullable=False),
    )
    op.create_index("ix_regions_geopolygon_gist", "regions",
                    ["geopolygon"], postgresql_using="gist")

    # --- изменить uav_flights ---
    with op.batch_alter_table("uav_flights") as batch_op:
        # удалить старые колонки
        batch_op.drop_column("takeoff_lat")
        batch_op.drop_column("takeoff_lon")
        batch_op.drop_column("landing_lat")
        batch_op.drop_column("landing_lon")
        batch_op.drop_column("started_at")
        batch_op.drop_column("duration_min")
        batch_op.drop_column("gc_distance_km")
        batch_op.drop_column("avg_speed_kmh")
        batch_op.drop_column("year")
        batch_op.drop_column("month")
        batch_op.drop_column("dow")
        batch_op.drop_column("hour")
        batch_op.drop_column("is_weekend")
        batch_op.drop_column("is_holiday")
        batch_op.drop_column("takeoff_region")
        batch_op.drop_column("landing_region")

        # добавить новые
        batch_op.add_column(sa.Column("takeoff_point", Geometry(
            geometry_type="POINT", srid=4326), nullable=True))
        batch_op.add_column(sa.Column("landing_point", Geometry(
            geometry_type="POINT", srid=4326), nullable=True))
        batch_op.add_column(sa.Column("coordinates", Geometry(
            geometry_type="POINT", srid=4326), nullable=True))
        batch_op.add_column(sa.Column("root_points", Geometry(
            geometry_type="MULTIPOINT", srid=4326), nullable=True))

        batch_op.add_column(sa.Column("takeoff_datetime", sa.DateTime(
            timezone=True), nullable=True, index=True))
        batch_op.add_column(sa.Column("landing_datetime", sa.DateTime(
            timezone=True), nullable=True, index=True))
        batch_op.add_column(sa.Column("date", sa.DateTime(
            timezone=True), nullable=True, index=True))
        batch_op.add_column(sa.Column("duration_seconds",
                            sa.Integer(), nullable=True))

        batch_op.add_column(sa.Column(
            "takeoff_region_id", sa.Integer(), sa.ForeignKey("regions.id"), nullable=True))
        batch_op.add_column(sa.Column(
            "landing_region_id", sa.Integer(), sa.ForeignKey("regions.id"), nullable=True))
        batch_op.add_column(sa.Column(
            "region_region_id", sa.Integer(), sa.ForeignKey("regions.id"), nullable=True))

        batch_op.add_column(
            sa.Column("distance_km", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column("average_speed_kmh", sa.Float(), nullable=True))

        # индексы/ограничения
        batch_op.create_check_constraint(
            "ck_duration_non_negative", "duration_seconds >= 0")
        batch_op.create_index("ix_uav_flights_takeoff_point_gist", [
                              "takeoff_point"], postgresql_using="gist")
        batch_op.create_index("ix_uav_flights_landing_point_gist", [
                              "landing_point"], postgresql_using="gist")
        batch_op.create_index("ix_uav_flights_coordinates_gist", [
                              "coordinates"], postgresql_using="gist")
        batch_op.create_index("ix_uav_flights_root_points_gist", [
                              "root_points"], postgresql_using="gist")

    op.alter_column(
        "uav_flights",
        "flight_id",
        existing_type=sa.String(length=128),
        nullable=True,
    )

    op.alter_column(
        "uav_flights",
        "uav_type",
        existing_type=sa.String(length=64),
        nullable=True,
    )


def downgrade() -> None:
    # --- вернуть старую схему uav_flights ---
    with op.batch_alter_table("uav_flights") as batch_op:
        # удалить новые
        batch_op.drop_index("ix_uav_flights_root_points_gist")
        batch_op.drop_index("ix_uav_flights_coordinates_gist")
        batch_op.drop_index("ix_uav_flights_landing_point_gist")
        batch_op.drop_index("ix_uav_flights_takeoff_point_gist")
        batch_op.drop_constraint("ck_duration_non_negative", type_="check")

        batch_op.drop_column("average_speed_kmh")
        batch_op.drop_column("distance_km")
        batch_op.drop_column("landing_region_id")
        batch_op.drop_column("takeoff_region_id")
        batch_op.drop_column("region_region_id")
        batch_op.drop_column("duration_seconds")
        batch_op.drop_column("date")
        batch_op.drop_column("landing_datetime")
        batch_op.drop_column("takeoff_datetime")
        batch_op.drop_column("root_points")
        batch_op.drop_column("coordinates")
        batch_op.drop_column("landing_point")
        batch_op.drop_column("takeoff_point")

        # добавить обратно старые
        batch_op.add_column(
            sa.Column("landing_region", sa.String(length=128), nullable=True))
        batch_op.add_column(
            sa.Column("takeoff_region", sa.String(length=128), nullable=True))
        batch_op.add_column(
            sa.Column("is_holiday", sa.Boolean(), nullable=True))
        batch_op.add_column(
            sa.Column("is_weekend", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("hour", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("dow", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("month", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("year", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("avg_speed_kmh", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column("gc_distance_km", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column("duration_min", sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column("started_at", sa.DateTime(
            timezone=True), nullable=False, index=True))
        batch_op.add_column(
            sa.Column("landing_lon", sa.Float(), nullable=False))
        batch_op.add_column(
            sa.Column("landing_lat", sa.Float(), nullable=False))
        batch_op.add_column(
            sa.Column("takeoff_lon", sa.Float(), nullable=False))
        batch_op.add_column(
            sa.Column("takeoff_lat", sa.Float(), nullable=False))

        # восстановить check-constraints
        batch_op.create_check_constraint(
            "ck_takeoff_lat_range", "takeoff_lat >= -90 AND takeoff_lat <= 90")
        batch_op.create_check_constraint(
            "ck_landing_lat_range", "landing_lat >= -90 AND landing_lat <= 90")
        batch_op.create_check_constraint(
            "ck_takeoff_lon_range", "takeoff_lon >= -180 AND takeoff_lon <= 180")
        batch_op.create_check_constraint(
            "ck_landing_lon_range", "landing_lon >= -180 AND landing_lon <= 180")
        batch_op.create_check_constraint(
            "ck_duration_non_negative", "duration_min >= 0")
        batch_op.create_check_constraint(
            "ck_month_range", "(month IS NULL) OR (month BETWEEN 1 AND 12)")
        batch_op.create_check_constraint(
            "ck_dow_range", "(dow IS NULL) OR (dow BETWEEN 0 AND 6)")
        batch_op.create_check_constraint(
            "ck_hour_range", "(hour IS NULL) OR (hour BETWEEN 0 AND 23)")

        batch_op.create_index(
            "ix_uav_flights_takeoff_point_gist",
            [sa.text("point(cast(takeoff_lon as float), cast(takeoff_lat as float))")],
            postgresql_using="gist"
        )
        batch_op.create_index(
            "ix_uav_flights_landing_point_gist",
            [sa.text("point(cast(landing_lon as float), cast(landing_lat as float))")],
            postgresql_using="gist"
        )

    # --- удалить таблицу regions ---
    op.drop_index("ix_regions_geopolygon_gist", table_name="regions")
    op.drop_table("regions")

    op.alter_column(
        "uav_flights",
        "flight_id",
        existing_type=sa.String(length=128),
        nullable=False,
    )

    op.alter_column(
        "uav_flights",
        "uav_type",
        existing_type=sa.String(length=64),
        nullable=False,
    )
