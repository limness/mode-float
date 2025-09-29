from src.database.models import FileMetadataModel

from .base_repository import BaseRepository


class FileMetadataRepository(BaseRepository[FileMetadataModel]):
    """Repository for FileMetadata model."""

    ...


file_metadata_repo = FileMetadataRepository()
