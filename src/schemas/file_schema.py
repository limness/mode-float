from typing import Any, Dict, List

from pydantic import BaseModel


class FileUploadResponseSchema(BaseModel):
    file_id: str
    filename: str
    file_size: int
    status: str
    message: str
    sheet_names: List[str]


class FileInfoSchema(BaseModel):
    file_id: str
    original_filename: str
    file_size: int
    content_type: str | None
    user_id: str
    description: str | None
    sheet_names: List[str]
    preview_rows: int
    preview_columns: int
    status: str
    created_at: str
    updated_at: str


class FileDataSchema(BaseModel):
    file_id: str
    sheet_name: str
    columns: List[str]
    data: List[Dict[str, Any]]
    total_rows: int
    current_page: int
    per_page: int
