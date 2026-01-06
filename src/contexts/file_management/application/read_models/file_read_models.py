"""
File Management Read Models.

These are query-optimized data structures for the CQRS read side.
They are designed for efficient reading and display, separate from
domain entities used for write operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, computed_field


class FileReadModel(BaseModel):
    """
    Full file read model for detailed views.

    Includes all file metadata and computed properties.
    """

    id: UUID
    name: str = Field(description="Internal unique filename")
    original_name: str = Field(description="Original uploaded filename")
    path: str = Field(description="Storage path")
    size: int = Field(description="File size in bytes")
    mime_type: str = Field(description="MIME type")
    owner_id: UUID = Field(description="Owner user ID")
    description: Optional[str] = Field(None, description="File description")
    is_public: bool = Field(description="Whether file is publicly accessible")
    download_count: int = Field(default=0, description="Number of downloads")
    shared_with: List[UUID] = Field(
        default_factory=list, description="User IDs file is shared with"
    )
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def size_human(self) -> str:
        """Human-readable file size."""
        size: float = self.size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def file_extension(self) -> str:
        """File extension extracted from original name."""
        if "." in self.original_name:
            return self.original_name.rsplit(".", 1)[-1].lower()
        return ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.mime_type.startswith("image/")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_document(self) -> bool:
        """Check if file is a document."""
        doc_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument",
            "text/plain",
        ]
        return any(self.mime_type.startswith(t) for t in doc_types)

    model_config = {"from_attributes": True}


class FileListItemReadModel(BaseModel):
    """
    Lightweight file read model for list views.

    Contains only essential information for file listings.
    """

    id: UUID
    original_name: str
    size: int
    mime_type: str
    is_public: bool
    download_count: int
    owner_id: UUID
    created_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def size_human(self) -> str:
        """Human-readable file size."""
        size: float = self.size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    model_config = {"from_attributes": True}


class FileDownloadReadModel(BaseModel):
    """
    Read model for file download operations.

    Contains information needed to serve a file download.
    """

    id: UUID
    name: str = Field(description="Internal filename")
    original_name: str = Field(description="Original filename for Content-Disposition")
    path: str = Field(description="Full storage path")
    mime_type: str = Field(description="Content-Type header value")
    size: int = Field(description="Content-Length header value")

    model_config = {"from_attributes": True}


class PaginatedFilesReadModel(BaseModel):
    """
    Paginated file list read model.

    Used for returning paginated file listings.
    """

    files: List[FileListItemReadModel]
    total: int
    skip: int
    limit: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.skip + len(self.files) < self.total
