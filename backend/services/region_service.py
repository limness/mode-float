from typing import Dict, List, Tuple

import shapefile
from geoalchemy2.shape import from_shape
from pyproj import Transformer
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.ops import transform
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import RegionModel

Coordinate = Tuple[float, float]
Polygon = List[Coordinate]
RegionPolygons = Dict[str, List[Polygon]]

project = Transformer.from_crs('EPSG:4326', 'EPSG:6933', always_xy=True).transform


def _detect_name_field_index(sf: shapefile.Reader) -> int | None:
    fields = [f[0] for f in sf.fields[1:]]
    preferred = {'NAME', 'NAME_1', 'NAME_RU', 'REGION', 'SUBJECT', 'NAME_RUS', 'NAME_RU_1'}
    for i, field in enumerate(fields):
        if field.upper() in preferred:
            return i
    return 1 if len(fields) > 1 else (0 if fields else None)


def _safe_record_name(rec, field_index: int | None) -> str:
    if field_index is not None and 0 <= field_index < len(rec):
        value = rec[field_index]
        if value is None:
            return 'UNKNOWN'
        return str(value)
    return 'UNKNOWN'


def _shape_to_polygons(points, parts) -> List[Polygon]:
    pts = list(points)
    part_indices = list(parts)
    if not pts:
        return []
    bounds = part_indices + [len(pts)]
    polygons: List[Polygon] = []
    for i in range(len(bounds) - 1):
        start = bounds[i]
        end = bounds[i + 1]
        ring = pts[start:end]
        if len(ring) >= 3:
            polygons.append([(float(x), float(y)) for x, y in ring])
    return polygons


def group_polygons_by_region(sf: shapefile.Reader) -> RegionPolygons:
    records = sf.records()
    shapes = sf.shapes()
    if len(records) != len(shapes):
        raise ValueError('Shapefile records and shapes length mismatch')
    name_field_index = _detect_name_field_index(sf)
    regions: RegionPolygons = {}
    for idx, shape in enumerate(shapes):
        rec = records[idx]
        region_name = _safe_record_name(rec, name_field_index)
        polygons = _shape_to_polygons(shape.points, shape.parts)
        if not polygons:
            continue
        bucket = regions.setdefault(region_name, [])
        bucket.extend(polygons)
    return regions


async def save_regions_to_db(region_polygons: RegionPolygons, db_session: AsyncSession):
    for name, polygons in region_polygons.items():
        try:
            valid_polygons = [ShapelyPolygon(ring) for ring in polygons if len(ring) >= 3]
            if not valid_polygons:
                continue
            shapely_poly = max(valid_polygons, key=lambda p: p.area)
            geopolygon = from_shape(shapely_poly, srid=4326)
            geopolygon_str = [[y, x] for x, y in shapely_poly.exterior.coords]
            shapely_poly_m = transform(project, shapely_poly)
            area = int(shapely_poly_m.area) / 1000000
            existing = await db_session.execute(
                RegionModel.__table__.select().where(RegionModel.name == name)
            )
            row = existing.first()
            if row:
                await db_session.execute(
                    RegionModel.__table__.update()
                    .where(RegionModel.name == name)
                    .values(area=area, geopolygon=geopolygon, geopolygon_str=geopolygon_str)
                )
            else:
                await db_session.execute(
                    RegionModel.__table__.insert().values(
                        name=name, area=area, geopolygon=geopolygon, geopolygon_str=geopolygon_str
                    )
                )
        except Exception as e:
            print(f'[ERROR] {name}: {e}')
