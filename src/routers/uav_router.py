import io

import openpyxl
import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_database
from src.exc import IDException
from src.schemas.file_schema import FileUploadResponseSchema
from src.services.exceptions import (
    FileCreateError,
    FileDeactivateError,
    ServiceError,
    UavFlightCreateError,
)
from src.services.file_service import create_file_metadata, deactivate_old_files, update_file_status
from src.services.parse_service.geocoder import DefaultGeocoder
from src.services.parse_service.loader import ExcelLoader
from src.services.parse_service.mapper import DefaultMapper
from src.services.parse_service.mapper import UavFlightModel as ParsedUavFlight
from src.services.uav_service import create_uav_flight

router = APIRouter(tags=['Files'])

MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post(
    '/upload/xlsx',
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_groups(['administrators']))]
)
async def upload_xlsx_file(
    # background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    description: str | None = Form(None),
    db_session: AsyncSession = Depends(get_database),
) -> FileUploadResponseSchema:
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise IDException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Only XLSX/XLS files are allowed!'
        )
    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise IDException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB!',
        )

    print('start001')

    file_io = io.BytesIO(file_content)
    try:
        workbook = openpyxl.load_workbook(file_io, read_only=True)
        sheet_names = workbook.sheetnames
        workbook.close()
    except Exception as e:
        raise IDException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f'Invalid XLSX file format: {str(e)}'
        )
    finally:
        file_io.seek(0)
    print('start002')

    try:
        file_rec = await create_file_metadata(
            db_session,
            filename=file.filename,
            file_size=len(file_content),
            status='uploaded',
            message=description or 'Uploaded',
            sheet_names=sheet_names,
            is_active=True,
            deactivate_previous=True,
        )
    except (FileCreateError, FileDeactivateError) as exc:
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    try:
        print('start0')
        await process_xlsx_file(
            db_session=db_session,
            file_io=file_io,
            file_id=str(file_rec.file_id),
        )
        await update_file_status(
            db_session,
            file_id=str(file_rec.file_id),
            status='processed',
            message='File processed successfully',
        )
    except (UavFlightCreateError, SQLAlchemyError, ServiceError) as exc:
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to process file: {str(exc)}',
        )
    finally:
        file_io.close()

    try:
        await deactivate_old_files(
            db_session,
            filename=file.filename,
            extra_filters=None,
        )
    except FileDeactivateError as exc:
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    return FileUploadResponseSchema(
        file_id=str(file_rec.file_id),
        filename=file_rec.filename,
        file_size=file_rec.file_size,
        status='processed',
        message='File uploaded and processed successfully',
        sheet_names=sheet_names,
    )


async def process_xlsx_file(
    db_session: AsyncSession,
    file_io: io.BytesIO,
    file_id: str,
) -> None:
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info('got without')
        with pd.ExcelFile(file_io) as excel_file:
            for sheet_name in excel_file.sheet_names:
                print('start')
                loader = ExcelLoader(source=excel_file, sheet_name=sheet_name)
                mapper = DefaultMapper(DefaultGeocoder())

                df = loader.load()
                if df.empty:
                    continue

                logger.info('got %s', df.shape)
                print('got', df.shape)

                for _, row in df.iterrows():
                    parsed: ParsedUavFlight = mapper.map_row(row)
                    logger.info('mapped %s', _)

                    await create_uav_flight(
                        db_session,
                        file_id=file_id,
                        uav_type=getattr(parsed, 'uav_type', None),
                        takeoff_point=getattr(parsed, 'takeoff_point', None),
                        landing_point=getattr(parsed, 'landing_point', None),
                        coordinates=getattr(parsed, 'coordinates', None),
                        takeoff_lat=getattr(parsed, 'takeoff_lat', None),
                        takeoff_lon=getattr(parsed, 'takeoff_lon', None),
                        landing_lat=getattr(parsed, 'landing_lat', None),
                        landing_lon=getattr(parsed, 'landing_lon', None),
                        latitude=getattr(parsed, 'latitude', None),
                        longitude=getattr(parsed, 'longitude', None),
                        takeoff_datetime=getattr(parsed, 'takeoff_datetime', None),
                        landing_datetime=getattr(parsed, 'landing_datetime', None),
                        date=getattr(parsed, 'date', None),
                        duration_minutes=getattr(parsed, 'duration_minutes', None),
                        city=getattr(parsed, 'city', None),
                        major_region_id=getattr(parsed, 'major_region_id', None),
                        takeoff_region_id=getattr(parsed, 'takeoff_region_id', None),
                        landing_region_id=getattr(parsed, 'landing_region_id', None),
                        distance_km=getattr(parsed, 'distance_km', None),
                        average_speed_kmh=getattr(parsed, 'average_speed_kmh', None),
                    )
    except ServiceError as exc:
        raise exc
    except Exception as exc:
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Unexpected parsing error: {str(exc)}',
        )
