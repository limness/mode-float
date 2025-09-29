from __future__ import annotations

from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import FileMetadataModel
from backend.repositories.file_repository import file_metadata_repo
from backend.services.exceptions import FileCreateError, FileDeactivateError, ServiceError


async def deactivate_old_files(
    db_session: AsyncSession,
    *,
    filename: str | None = None,
    exclude_file_id: str | None = None,
    extra_filters: dict[str, Any] | None = None,
) -> None:
    """Deactivate old active FileMetadata records.

    Deactivates by:
    - `filename` equality (common case for versions), and `is_active=True`
    - optional `extra_filters` (e.g., by status or custom flags)
    - can exclude a specific file id (e.g., the just-created one)

    Args:
        db_session: Active async DB session.
        filename: Target filename to deactivate previous versions for.
        exclude_file_id: Keep this file active (skip deactivation).
        extra_filters: Additional exact-match filters passed to repo.

    Returns:
        int: Number of deactivated records.

    Raises:
        FileDeactivateError: On DB errors.
    """
    try:
        filters: dict[str, Any] = {'is_active': True}
        if filename is not None:
            filters['filename'] = filename
        if extra_filters:
            filters.update(extra_filters)

        candidates = await file_metadata_repo.get_all(db_session, **filters)
        for fm in candidates:
            if exclude_file_id and str(fm.file_id) == str(exclude_file_id):
                continue
            await file_metadata_repo.update_one(
                {'file_id': fm.file_id},
                db_session,
                is_active=False,
            )
    except SQLAlchemyError as exc:
        raise FileDeactivateError(f'Failed to deactivate old files: {exc}') from exc


async def create_file_metadata(
    db_session: AsyncSession,
    *,
    filename: str,
    file_size: int,
    status: str,
    message: str,
    sheet_names: list[str] | None,
    is_active: bool = True,
    deactivate_previous: bool = True,
    deactivate_filters: dict[str, Any] | None = None,
) -> FileMetadataModel:
    """Create a new FileMetadata record and optionally deactivate older active versions.

    Typical usage is to keep only the latest file (by `filename`) active.

    Args:
        db_session: Active async DB session.
        filename: Stored file name.
        file_size: File size in bytes.
        status: Processing status.
        message: Status/message detail.
        sheet_names: List of sheet names found in the file.
        is_active: Whether the created record should be active.
        deactivate_previous: If True, deactivates older active records for the same filename.
        deactivate_filters: Extra filters for deactivation (merged with `{'filename': filename}`).

    Returns:
        FileMetadata: Created file metadata row.

    Raises:
        FileCreateError: On DB errors during creation.
        FileDeactivateError: On DB errors during deactivation.
    """
    try:
        new_file = await file_metadata_repo.create_one(
            db_session,
            filename=filename,
            file_size=file_size,
            status=status,
            message=message,
            sheet_names=sheet_names,
            is_active=is_active,
        )
    except SQLAlchemyError as exc:
        raise FileCreateError(f"Failed to create file metadata for '{filename}': {exc}") from exc

    if deactivate_previous:
        # Build deactivation filter set: same filename + optional extras
        extra = dict(deactivate_filters or {})
        extra['filename'] = filename
        await deactivate_old_files(
            db_session,
            filename=filename,
            exclude_file_id=str(new_file.file_id),
            extra_filters=deactivate_filters,
        )

    return new_file


async def update_file_status(
    db_session: AsyncSession,
    *,
    file_id: str,
    status: str,
    message: str | None = None,
) -> None:
    """Update status/message of a FileMetadata record.

    Args:
        db_session: Active async DB session.
        file_id: FileMetadata.file_id (UUID as str/UUID).
        status: New status value.
        message: Optional message.

    Raises:
        ServiceError: Wrapped SQLAlchemy errors.
    """
    try:
        values: dict[str, Any] = {'status': status}
        if message is not None:
            values['message'] = message
        await file_metadata_repo.update_one({'file_id': file_id}, db_session, **values)
    except SQLAlchemyError as exc:
        raise ServiceError(f'Failed to update file status: {exc}') from exc
