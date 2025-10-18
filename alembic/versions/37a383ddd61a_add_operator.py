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


def index_exists(connection, index_name: str) -> bool:
    result = connection.execute(
        sa.text("SELECT to_regclass(:name)"),
        {"name": index_name}
    )
    return result.scalar() is not None


def create_index_if_not_exists(connection, name, table, columns, **kwargs):
    if not index_exists(connection, name):
        op.create_index(name, table, columns, **kwargs)


def upgrade() -> None:
    connection = op.get_bind()

    op.add_column('uav_flights', sa.Column('operator_name', sa.String(128), nullable=True))
    op.add_column('uav_flights', sa.Column('operator_type', sa.String(64), nullable=True))

    create_index_if_not_exists(connection, 'idx_uav_flights_operator_name', 'uav_flights', ['operator_name'])
    create_index_if_not_exists(connection, 'idx_regions_name', 'regions', ['name'])
    create_index_if_not_exists(connection, 'idx_regions_area', 'regions', ['area'])
    create_index_if_not_exists(connection, 'idx_uav_flights_file_id', 'uav_flights', ['file_id'])
    create_index_if_not_exists(connection, 'idx_uav_flights_uav_type', 'uav_flights', ['uav_type'])
    create_index_if_not_exists(connection, 'idx_uav_flights_city', 'uav_flights', ['city'])
    create_index_if_not_exists(connection, 'idx_uav_flights_major_region_id', 'uav_flights', ['major_region_id'])
    create_index_if_not_exists(connection, 'idx_uav_flights_takeoff_region_id', 'uav_flights', ['takeoff_region_id'])
    create_index_if_not_exists(connection, 'idx_uav_flights_landing_region_id', 'uav_flights', ['landing_region_id'])
    create_index_if_not_exists(connection, 'idx_uav_flights_distance_km', 'uav_flights', ['distance_km'])
    create_index_if_not_exists(connection, 'idx_uav_flights_average_speed_kmh', 'uav_flights', ['average_speed_kmh'])
    create_index_if_not_exists(connection, 'idx_file_metadata_filename', 'file_metadata', ['filename'])
    create_index_if_not_exists(connection, 'idx_file_metadata_status', 'file_metadata', ['status'])
    create_index_if_not_exists(connection, 'idx_file_metadata_is_active', 'file_metadata', ['is_active'])
    create_index_if_not_exists(connection, 'idx_uav_flights_operator_type', 'uav_flights', ['operator_type'])
    create_index_if_not_exists(connection, 'idx_uav_flights_coordinates', 'uav_flights', ['coordinates'], unique=False, postgresql_using='gist')
    create_index_if_not_exists(connection, 'idx_uav_flights_landing_point', 'uav_flights', ['landing_point'], unique=False, postgresql_using='gist')
    create_index_if_not_exists(connection, 'idx_uav_flights_takeoff_point', 'uav_flights', ['takeoff_point'], unique=False, postgresql_using='gist')


def downgrade() -> None:
    connection = op.get_bind()

    op.drop_column('uav_flights', 'operator_name')
    op.drop_column('uav_flights', 'operator_type')

    if index_exists(connection, 'idx_uav_flights_operator_name'):
        op.drop_index('idx_uav_flights_operator_name', table_name='uav_flights')
    if index_exists(connection, 'idx_regions_name'):
        op.drop_index('idx_regions_name', table_name='regions')
    if index_exists(connection, 'idx_regions_area'):
        op.drop_index('idx_regions_area', table_name='regions')
    if index_exists(connection, 'idx_uav_flights_file_id'):
        op.drop_index('idx_uav_flights_file_id', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_uav_type'):
        op.drop_index('idx_uav_flights_uav_type', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_city'):
        op.drop_index('idx_uav_flights_city', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_major_region_id'):
        op.drop_index('idx_uav_flights_major_region_id', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_takeoff_region_id'):
        op.drop_index('idx_uav_flights_takeoff_region_id', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_landing_region_id'):
        op.drop_index('idx_uav_flights_landing_region_id', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_distance_km'):
        op.drop_index('idx_uav_flights_distance_km', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_average_speed_kmh'):
        op.drop_index('idx_uav_flights_average_speed_kmh', table_name='uav_flights')
    if index_exists(connection, 'idx_file_metadata_filename'):
        op.drop_index('idx_file_metadata_filename', table_name='file_metadata')
    if index_exists(connection, 'idx_file_metadata_status'):
        op.drop_index('idx_file_metadata_status', table_name='file_metadata')
    if index_exists(connection, 'idx_file_metadata_is_active'):
        op.drop_index('idx_file_metadata_is_active', table_name='file_metadata')
    if index_exists(connection, 'idx_uav_flights_operator_type'):
        op.drop_index('idx_uav_flights_operator_type', table_name='uav_flights')
    if index_exists(connection, 'idx_uav_flights_takeoff_point'):
        op.drop_index('idx_uav_flights_takeoff_point', table_name='uav_flights', postgresql_using='gist')
    if index_exists(connection, 'idx_uav_flights_landing_point'):
        op.drop_index('idx_uav_flights_landing_point', table_name='uav_flights', postgresql_using='gist')
    if index_exists(connection, 'idx_uav_flights_coordinates'):
        op.drop_index('idx_uav_flights_coordinates', table_name='uav_flights', postgresql_using='gist')