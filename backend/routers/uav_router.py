import io
import logging

import openpyxl
import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.settings import application_settings
from backend.database.base import get_database
from backend.dto import UavFlightCreateDTO
from backend.exc import IDException
from backend.schemas.file_schema import FileUploadResponseSchema
from backend.schemas.uav_schema import DateBoundsQuery, DateBoundsResponse, UavFlightsResponse
from backend.services.exceptions import (
    FileCreateError,
    FileDeactivateError,
    ServiceError,
    UavFlightCreateError,
)
from backend.services.file_service import (
    create_file_metadata,
    deactivate_old_files,
    update_file_status,
)
from backend.services.parse_service.geocoder import DefaultGeocoder
from backend.services.parse_service.loader import ExcelLoader
from backend.services.parse_service.mapper import DefaultMapper
from backend.services.parse_service.party_classifier import PartyClassifier
from backend.services.uav_service import (
    create_uav_flights,
    get_uav_date_bounds,
    get_uav_flights_between_dates,
)

router = APIRouter(tags=['Files'])

MAX_FILE_SIZE = 50 * 1024 * 1024

logger = logging.getLogger(__name__)


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
    """Загрузка и обработка Excel-файла с данными полётов БВС.

    Проверяется расширение и размер файла, читаются имена листов, создаётся
    запись о файле. Далее данные с каждого листа построчно парсятся и
    сохраняются как полёты, после чего статус файла обновляется. При
    необходимости предыдущие активные версии деактивируются.

    - 201: файл успешно загружен и обработан
    - 400: неверный формат файла
    - 413: превышен допустимый размер файла
    - 500: ошибка обработки или записи данных
    """
    logger.info('File creation')
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
        file_id = str(file_rec.file_id)
        await process_xlsx_file(db_session=db_session, file_io=file_io, file_id=file_id)
        await update_file_status(
            db_session,
            file_id=file_id,
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
    """Парсинг Excel-файла и сохранение полётов в БД.

    Итерируется по листам и строкам, выполняется маппинг полёта и создание
    записи, связанной с `file_id`. Исключения пробрасываются наверх для
    корректной обработки в вызывающем хэндлере.
    """
    try:
        with pd.ExcelFile(file_io) as excel_file:
            for sheet_name in excel_file.sheet_names:
                loader = ExcelLoader(source=excel_file, sheet_name=sheet_name)
                mapper = DefaultMapper(DefaultGeocoder(), PartyClassifier())

                df = loader.load()
                if df.empty:
                    continue

                uav_flights_batch: list[dict] = []
                for _, row in df.iterrows():
                    uav_flight: UavFlightCreateDTO = mapper.map_row(row)
                    uav_flight.file_id = file_id
                    uav_flights_batch.append(uav_flight.model_dump())

                    if len(uav_flights_batch) >= application_settings.APP_BATCH_PROCESSING:
                        logger.info('Created uav model %s / %s', _, df.shape)
                        await create_uav_flights(db_session, data=uav_flights_batch)
                        uav_flights_batch = []

                if uav_flights_batch:
                    await create_uav_flights(db_session, data=uav_flights_batch)

    except ServiceError as exc:
        raise exc
    except Exception as exc:
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Unexpected parsing error: {str(exc)}',
        )


@router.post('/date-bounds', status_code=status.HTTP_200_OK)
async def get_date_bounds(db_session: AsyncSession = Depends(get_database)) -> DateBoundsResponse:
    """Вернуть минимальную и максимальную дату полётов в базе.

    Возвращает ISO-строки дат (или `null`, если данных нет).

    - 200: границы дат получены
    - 500: ошибка вычисления границ
    """
    try:
        min_date, max_date = await get_uav_date_bounds(db_session)
        return DateBoundsResponse(
            min_date=min_date.isoformat() if min_date else None,
            max_date=max_date.isoformat() if max_date else None,
        )
    except Exception as exc:
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get('/journal-json', status_code=status.HTTP_200_OK)
async def get_flights_between_dates(
    min_date: str = Query(..., description='Начальная дата диапазона в ISO 8601'),
    max_date: str = Query(..., description='Конечная дата диапазона в ISO 8601'),
    limit: int | None = Query(None, ge=1, le=1000, description='Максимальное количество записей'),
    db_session: AsyncSession = Depends(get_database),
) -> UavFlightsResponse:
    """Получить полёты БВС в заданном диапазоне дат."""
    try:
        query = DateBoundsQuery(min_date=min_date, max_date=max_date, limit=limit)
        flights = await get_uav_flights_between_dates(db_session, query=query)
        return UavFlightsResponse(flights=flights)
    except ValueError as exc:
        raise IDException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise IDException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
