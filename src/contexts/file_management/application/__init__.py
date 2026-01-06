"""
File Management Application Layer.

Contains:
- commands/ - Command handlers (write operations)
- queries/ - Query handlers (read operations)
- dto/ - Data transfer objects
- read_models/ - Read models for queries
- ports/ - Port interfaces
"""

from .commands import (
    DeleteFileCommand,
    DeleteFileHandler,
    ShareFileCommand,
    ShareFileHandler,
    UpdateFileCommand,
    UpdateFileHandler,
    UploadFileCommand,
    UploadFileHandler,
)
from .dto import (
    FileDownloadResponseDTO,
    FileListResponseDTO,
    FileResponseDTO,
    FileShareDTO,
    FileUpdateDTO,
    FileUploadDTO,
)
from .ports import (
    IFileManagementUoW,
    IFileManagementUoWFactory,
    IFileReadRepository,
    IFileRepository,
)
from .queries import (
    GetFileByIdHandler,
    GetFileByIdQuery,
    GetFileDownloadHandler,
    GetFileDownloadQuery,
    ListFilesHandler,
    ListFilesQuery,
)
from .read_models import (
    FileDownloadReadModel,
    FileListItemReadModel,
    FileReadModel,
    PaginatedFilesReadModel,
)

__all__ = [
    # Commands
    "UploadFileCommand",
    "UpdateFileCommand",
    "DeleteFileCommand",
    "ShareFileCommand",
    # Command Handlers
    "UploadFileHandler",
    "UpdateFileHandler",
    "DeleteFileHandler",
    "ShareFileHandler",
    # Queries
    "GetFileByIdQuery",
    "ListFilesQuery",
    "GetFileDownloadQuery",
    # Query Handlers
    "GetFileByIdHandler",
    "ListFilesHandler",
    "GetFileDownloadHandler",
    # DTOs
    "FileUploadDTO",
    "FileUpdateDTO",
    "FileResponseDTO",
    "FileListResponseDTO",
    "FileShareDTO",
    "FileDownloadResponseDTO",
    # Read Models
    "FileReadModel",
    "FileListItemReadModel",
    "FileDownloadReadModel",
    "PaginatedFilesReadModel",
    # Ports
    "IFileRepository",
    "IFileReadRepository",
    "IFileManagementUoW",
    "IFileManagementUoWFactory",
]
