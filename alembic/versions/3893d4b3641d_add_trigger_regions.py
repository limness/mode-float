"""Add trigger regions

Revision ID: 3893d4b3641d
Revises: 90ae82e041a4
Create Date: 2025-10-02 17:38:46.990258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3893d4b3641d'
down_revision: Union[str, None] = '90ae82e041a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION uav_flights_before_insert_update()
        RETURNS trigger AS $$
        BEGIN
            IF NEW.takeoff_lat IS NOT NULL AND NEW.takeoff_lon IS NOT NULL THEN
                NEW.takeoff_point := ST_SetSRID(ST_MakePoint(NEW.takeoff_lon, NEW.takeoff_lat), 4326);
            ELSE
                NEW.takeoff_point := NULL;
            END IF;

            IF NEW.landing_lat IS NOT NULL AND NEW.landing_lon IS NOT NULL THEN
                NEW.landing_point := ST_SetSRID(ST_MakePoint(NEW.landing_lon, NEW.landing_lat), 4326);
            ELSE
                NEW.landing_point := NULL;
            END IF;

            IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
                NEW.coordinates := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
            ELSE
                NEW.coordinates := NULL;
            END IF;

            IF NEW.takeoff_point IS NOT NULL THEN
                SELECT id INTO NEW.takeoff_region_id
                FROM regions
                WHERE ST_Contains(regions.geopolygon, NEW.takeoff_point)
                LIMIT 1;
            ELSE
                NEW.takeoff_region_id := NULL;
            END IF;

            IF NEW.landing_point IS NOT NULL THEN
                SELECT id INTO NEW.landing_region_id
                FROM regions
                WHERE ST_Contains(regions.geopolygon, NEW.landing_point)
                LIMIT 1;
            ELSE
                NEW.landing_region_id := NULL;
            END IF;

            IF NEW.takeoff_region_id IS NOT NULL THEN
                NEW.major_region_id := NEW.takeoff_region_id;
            ELSIF NEW.landing_region_id IS NOT NULL THEN
                NEW.major_region_id := NEW.landing_region_id;
            ELSE
                NEW.major_region_id := NULL;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_uav_flights_before_ins_upd ON uav_flights;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_uav_flights_before_ins_upd
        BEFORE INSERT OR UPDATE
        ON uav_flights
        FOR EACH ROW
        EXECUTE FUNCTION uav_flights_before_insert_update();
        """
    )


def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_uav_flights_before_ins_upd ON uav_flights;")
    op.execute("DROP FUNCTION IF EXISTS uav_flights_before_insert_update;")
