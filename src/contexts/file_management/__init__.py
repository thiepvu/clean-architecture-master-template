"""
File Management Bounded Context.

Public API for the File Management context.
Other layers should import from here, not from internal modules.

This module provides a clean public API following the Barrel Export pattern:
- Commands & Queries (CQRS operations)
- Read Models (query results)
- DTOs (data transfer objects)
- Domain entities, value objects, events, exceptions
- Ports (interfaces for repositories/services)
- Facades (anti-corruption layer for cross-BC communication)
- Composition metadata (for DI wiring)

Usage:
──────
# Basic usage (commands, queries, read models)
from contexts.file_management import (
    UploadFileCommand,
    GetFileByIdQuery,
    FileReadModel,
)

# Domain layer access
from contexts.file_management.domain import File, FilePath, FileUploadedEvent

# Application layer access
from contexts.file_management.application import (
    IFileRepository,
    FileManagementFacade,
)

# Composition metadata (for bootstrapper)
from contexts.file_management.composition import FileManagementComposition
"""

# =============================================================================
# Commands (Public API)
# =============================================================================
from .application.commands import (
    DeleteFileCommand,
    DeleteFileHandler,
    ShareFileCommand,
    ShareFileHandler,
    UpdateFileCommand,
    UpdateFileHandler,
    UploadFileCommand,
    UploadFileHandler,
)

# =============================================================================
# DTOs (Public API)
# =============================================================================
from .application.dto import (
    FileDownloadResponseDTO,
    FileListResponseDTO,
    FileResponseDTO,
    FileShareDTO,
    FileUpdateDTO,
    FileUploadDTO,
)

# =============================================================================
# Ports (Interfaces)
# Note: IStorageService is now in shared.application.ports
# =============================================================================
from .application.ports import (
    IFileManagementUoW,
    IFileManagementUoWFactory,
    IFileReadRepository,
    IFileRepository,
)

# =============================================================================
# Queries (Public API)
# =============================================================================
from .application.queries import (
    GetFileByIdHandler,
    GetFileByIdQuery,
    GetFileDownloadHandler,
    GetFileDownloadQuery,
    ListFilesHandler,
    ListFilesQuery,
)

# =============================================================================
# Read Models (Public API)
# =============================================================================
from .application.read_models import (
    FileDownloadReadModel,
    FileListItemReadModel,
    FileReadModel,
    PaginatedFilesReadModel,
)

# =============================================================================
# Composition Metadata (for DI wiring)
# =============================================================================
from .composition import FileManagementComposition

# =============================================================================
# Domain Layer (Re-exports for convenience)
# =============================================================================
from .domain import File  # Entity; Value Objects; Events; Errors; Exceptions
from .domain import (
    FileAccessDeniedException,
    FileDeletedEvent,
    FileDownloadedEvent,
    FileErrorCode,
    FileNotFoundException,
    FilePath,
    FileSharedEvent,
    FileSize,
    FileSizeLimitExceededException,
    FileUpdatedEvent,
    FileUploadedEvent,
    InvalidFilePathException,
    InvalidFileSizeException,
    InvalidFileTypeException,
    InvalidMimeTypeException,
    MimeType,
    register_file_error_codes,
)

__all__ = [
    # =========================================================================
    # Commands
    # =========================================================================
    "UploadFileCommand",
    "UpdateFileCommand",
    "DeleteFileCommand",
    "ShareFileCommand",
    # =========================================================================
    # Command Handlers
    # =========================================================================
    "UploadFileHandler",
    "UpdateFileHandler",
    "DeleteFileHandler",
    "ShareFileHandler",
    # =========================================================================
    # Queries
    # =========================================================================
    "GetFileByIdQuery",
    "ListFilesQuery",
    "GetFileDownloadQuery",
    # =========================================================================
    # Query Handlers
    # =========================================================================
    "GetFileByIdHandler",
    "ListFilesHandler",
    "GetFileDownloadHandler",
    # =========================================================================
    # Read Models
    # =========================================================================
    "FileReadModel",
    "FileListItemReadModel",
    "FileDownloadReadModel",
    "PaginatedFilesReadModel",
    # =========================================================================
    # DTOs
    # =========================================================================
    "FileUploadDTO",
    "FileUpdateDTO",
    "FileResponseDTO",
    "FileListResponseDTO",
    "FileShareDTO",
    "FileDownloadResponseDTO",
    # =========================================================================
    # Ports
    # =========================================================================
    "IFileRepository",
    "IFileReadRepository",
    "IFileManagementUoW",
    "IFileManagementUoWFactory",
    # =========================================================================
    # Composition Metadata
    # =========================================================================
    "FileManagementComposition",
    # =========================================================================
    # Domain - Entity
    # =========================================================================
    "File",
    # =========================================================================
    # Domain - Value Objects
    # =========================================================================
    "FilePath",
    "FileSize",
    "MimeType",
    # =========================================================================
    # Domain - Events
    # =========================================================================
    "FileUploadedEvent",
    "FileUpdatedEvent",
    "FileDeletedEvent",
    "FileSharedEvent",
    "FileDownloadedEvent",
    # =========================================================================
    # Domain - Errors
    # =========================================================================
    "FileErrorCode",
    "register_file_error_codes",
    # =========================================================================
    # Domain - Exceptions
    # =========================================================================
    "FileNotFoundException",
    "FileAccessDeniedException",
    "FileSizeLimitExceededException",
    "InvalidFilePathException",
    "InvalidFileSizeException",
    "InvalidFileTypeException",
    "InvalidMimeTypeException",
]
