"""File Data Transfer Objects"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from shared.application.dto import DTO


class FileUploadDTO(DTO):
    """File upload DTO"""

    original_name: str = Field(..., description="Original filename")
    size: int = Field(..., gt=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    description: Optional[str] = Field(None, max_length=500, description="File description")
    is_public: bool = Field(default=False, description="Public access flag")

    # These will be set by the service after upload
    name: Optional[str] = Field(None, description="Internal filename")
    path: Optional[str] = Field(None, description="Storage path")


class FileUpdateDTO(DTO):
    """File update DTO"""

    original_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    is_public: Optional[bool] = None


class FileShareDTO(DTO):
    """File share DTO"""

    user_id: UUID = Field(..., description="User ID to share with")


class FileResponseDTO(DTO):
    """File response DTO"""

    id: UUID
    name: str
    original_name: str
    path: str
    size: int
    size_human: str  # Human-readable size
    mime_type: str
    owner_id: UUID
    description: Optional[str]
    is_public: bool
    download_count: int
    shared_with: List[UUID]
    file_extension: str
    is_image: bool
    is_document: bool
    created_at: datetime
    updated_at: datetime


class FileListResponseDTO(DTO):
    """File list item DTO"""

    id: UUID
    original_name: str
    size_human: str
    mime_type: str
    is_public: bool
    download_count: int
    created_at: datetime


class FileDownloadResponseDTO(DTO):
    """File download response DTO"""

    id: UUID
    name: str
    original_name: str
    path: str
    mime_type: str
    size: int
