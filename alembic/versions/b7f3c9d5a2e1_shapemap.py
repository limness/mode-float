"""Load regions from shapefile (synchronous)

Revision ID: b7f3c9d5a2e1
Revises: 90ae82e041a4
Create Date: 2025-09-30 13:45:00.000000
"""
from alembic import op
import sqlalchemy as sa
import requests
import shapefile
from io import BytesIO
from typing import Union, Sequence
from shapely.geometry import Polygon as ShapelyPolygon
from geoalchemy2.shape import from_shape
from shapely.ops import transform
from pyproj import Transformer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.settings import postgres_settings
from backend.database.models import RegionModel

revision: str = 'b7f3c9d5a2e1'
down_revision: Union[str, None] = '90ae82e041a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


sync_engine = create_engine(
    postgres_settings.POSTGRES_URI.replace("+asyncpg", ""),
    future=True
)
SessionLocal = sessionmaker(bind=sync_engine)

project = Transformer.from_crs("EPSG:4326", "EPSG:6933", always_xy=True).transform


def get_region_polygons(shp_url: str):
    """Скачивает shapefile и собирает полигоны по регионам."""
    shx_url = shp_url[:-4] + ".shx"
    dbf_url = shp_url[:-4] + ".dbf"

    shp_resp = requests.get(shp_url)
    shx_resp = requests.get(shx_url)
    dbf_resp = requests.get(dbf_url)

    for resp, ext in ((shp_resp, "shp"), (shx_resp, "shx"), (dbf_resp, "dbf")):
        resp.raise_for_status()
        if not resp.content:
            raise ValueError(f"Downloaded empty {ext} file from {resp.url}")

    with shapefile.Reader(
        shp=BytesIO(shp_resp.content),
        shx=BytesIO(shx_resp.content),
        dbf=BytesIO(dbf_resp.content),
    ) as sf:
        return _group_polygons_by_region(sf)


def _group_polygons_by_region(sf: shapefile.Reader):
    records = sf.records()
    shapes = sf.shapes()
    if len(records) != len(shapes):
        raise ValueError("Shapefile records and shapes length mismatch")

    name_field_index = _detect_name_field_index(sf)
    regions = {}
    for idx, shape in enumerate(shapes):
        rec = records[idx]
        name = _safe_record_name(rec, name_field_index)
        polygons = _shape_to_polygons(shape.points, shape.parts)
        if polygons:
            regions.setdefault(name, []).extend(polygons)
    return regions


def _detect_name_field_index(sf: shapefile.Reader):
    fields = [f[0] for f in sf.fields[1:]]
    preferred = {"NAME", "NAME_1", "NAME_RU", "REGION", "SUBJECT", "NAME_RUS", "NAME_RU_1"}
    for i, field in enumerate(fields):
        if field.upper() in preferred:
            return i
    return 1 if len(fields) > 1 else (0 if fields else None)


def _safe_record_name(rec, idx):
    if idx is not None and 0 <= idx < len(rec):
        return str(rec[idx]) if rec[idx] is not None else "UNKNOWN"
    return "UNKNOWN"


def _shape_to_polygons(points, parts):
    pts = list(points)
    part_indices = list(parts)
    if not pts:
        return []
    bounds = part_indices + [len(pts)]
    polygons = []
    for i in range(len(bounds) - 1):
        start, end = bounds[i], bounds[i + 1]
        ring = pts[start:end]
        if len(ring) >= 3:
            polygons.append([(float(x), float(y)) for x, y in ring])
    return polygons


def save_regions_to_db(region_polygons):
    """Сохраняет регионы в базу bulk insert'ом."""
    with SessionLocal() as session:
        objs = []
        for name, polygons in region_polygons.items():
            valid_polygons = [ShapelyPolygon(r) for r in polygons if len(r) >= 3]
            if not valid_polygons:
                print(f"[SKIP] {name}: нет валидных полигонов")
                continue
            shapely_poly = max(valid_polygons, key=lambda p: p.area)
            shapely_poly_m = transform(project, shapely_poly)
            area = int(shapely_poly_m.area) / 1000000
            geopolygon = from_shape(shapely_poly, srid=4326)
            geopolygon_str = str([[[pt[1], pt[0]] for poly in polygons for pt in poly]])
            objs.append(
                RegionModel(
                    name=name,
                    area=area,
                    geopolygon=geopolygon,
                    geopolygon_str=geopolygon_str,
                )
            )
        if objs:
            session.bulk_save_objects(objs)
            session.commit()


def upgrade():
    shp_url = "https://raw.githubusercontent.com/Ar4ikov/Russia-Admin-Shapemap/refs/heads/main/RF/admin_4.shp"
    region_polygons = get_region_polygons(shp_url)
    save_regions_to_db(region_polygons)


def downgrade():
    with SessionLocal() as session:
        session.execute(sa.delete(RegionModel))
        session.commit()