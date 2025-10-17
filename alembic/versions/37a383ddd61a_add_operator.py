"""add operator

Revision ID: 37a383ddd61a
Revises: 3893d4b3641d
Create Date: 2025-10-17 15:56:33.041655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37a383ddd61a'
down_revision: Union[str, None] = '3893d4b3641d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('uav_flights', sa.Column('operator_name', sa.String(128), nullable=True))
    op.create_index('idx_uav_flights_operator_name', 'uav_flights', ['operator_name'])
    op.create_index('idx_regions_name', 'regions', ['name'])
    op.create_index('idx_regions_area', 'regions', ['area'])
    op.create_index('idx_uav_flights_file_id', 'uav_flights', ['file_id'])
    op.create_index('idx_uav_flights_uav_type', 'uav_flights', ['uav_type'])
    op.create_index('idx_uav_flights_city', 'uav_flights', ['city'])
    op.create_index('idx_uav_flights_major_region_id', 'uav_flights', ['major_region_id'])
    op.create_index('idx_uav_flights_takeoff_region_id', 'uav_flights', ['takeoff_region_id'])
    op.create_index('idx_uav_flights_landing_region_id', 'uav_flights', ['landing_region_id'])
    op.create_index('idx_uav_flights_distance_km', 'uav_flights', ['distance_km'])
    op.create_index('idx_uav_flights_average_speed_kmh', 'uav_flights', ['average_speed_kmh'])
    op.create_index('idx_file_metadata_filename', 'file_metadata', ['filename'])
    op.create_index('idx_file_metadata_status', 'file_metadata', ['status'])
    op.create_index('idx_file_metadata_is_active', 'file_metadata', ['is_active'])
    op.add_column('uav_flights', sa.Column('operator_type', sa.String(64), nullable=True))
    op.create_index('idx_uav_flights_operator_type', 'uav_flights', ['operator_type'])

def downgrade() -> None:
    op.drop_column('uav_flights', 'operator_name')
    op.drop_index('idx_uav_flights_operator_name', 'uav_flights')
    op.drop_index('idx_regions_name', 'regions')
    op.drop_index('idx_regions_area', 'regions')
    op.drop_index('idx_uav_flights_file_id', 'uav_flights')
    op.drop_index('idx_uav_flights_uav_type', 'uav_flights')
    op.drop_index('idx_uav_flights_city', 'uav_flights')
    op.drop_index('idx_uav_flights_major_region_id', 'uav_flights')
    op.drop_index('idx_uav_flights_takeoff_region_id', 'uav_flights')
    op.drop_index('idx_uav_flights_landing_region_id', 'uav_flights')
    op.drop_index('idx_uav_flights_distance_km', 'uav_flights')
    op.drop_index('idx_uav_flights_average_speed_kmh', 'uav_flights')
    op.drop_index('idx_file_metadata_filename', 'file_metadata')
    op.drop_index('idx_file_metadata_status', 'file_metadata')
    op.drop_index('idx_file_metadata_is_active', 'file_metadata')
    op.drop_column('uav_flights', 'operator_type')
    op.drop_index('idx_uav_flights_operator_type', 'uav_flights')
