from io import BytesIO

import shapefile
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.base import get_database
from backend.exc import IDException
from backend.services.region_service import group_polygons_by_region, save_regions_to_db

router = APIRouter(tags=['Regions'])


@router.post('/upload-shapefile', status_code=status.HTTP_201_CREATED)
async def upload_shapefile(
    shp: UploadFile = File(...),
    dbf: UploadFile = File(...),
    db_session: AsyncSession = Depends(get_database),
):
    """Загрузка границ регионов из пары файлов Shapefile (.shp и .dbf).

    Ожидает два файла: основной геометрический файл `.shp` и файл атрибутов `.dbf`.
    После чтения и парсинга полигоны группируются по региону и сохраняются в БД.

    Возвращает список идентификаторов/названий регионов, которые были распознаны.

    - 201: файлы успешно обработаны и регионы сохранены
    - 400: переданы файлы неверного формата
    - 404: ошибка чтения/парсинга или сохранения
    """
    if not (shp.filename.lower().endswith('.shp') and dbf.filename.lower().endswith('.dbf')):
        raise IDException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Only .shp and .dbf files are allowed!'
        )
    shp_bytes = await shp.read()
    dbf_bytes = await dbf.read()
    try:
        with shapefile.Reader(
            shp=BytesIO(shp_bytes),
            dbf=BytesIO(dbf_bytes),
        ) as sf:
            region_polygons = group_polygons_by_region(sf)
        await save_regions_to_db(region_polygons, db_session)
        return {'status': 'ok', 'regions': list(region_polygons.keys())}
    except Exception as exc:
        raise IDException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
