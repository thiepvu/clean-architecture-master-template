"""
File Management Read Models.

Read Models are DTOs optimized for queries (read operations).
They are separate from Write Models (domain entities) and are
designed for efficient data display and API responses.
"""

from .file_read_models import (
    FileDownloadReadModel,
    FileListItemReadModel,
    FileReadModel,
    PaginatedFilesReadModel,
)

__all__ = [
    "FileReadModel",
    "FileListItemReadModel",
    "FileDownloadReadModel",
    "PaginatedFilesReadModel",
]
