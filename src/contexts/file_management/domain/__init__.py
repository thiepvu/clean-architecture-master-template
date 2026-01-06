"""
File Management Domain Layer.

Contains:
- entities/ - Domain entities (File)
- value_objects/ - Value objects (FilePath, FileSize, MimeType)
- events/ - Domain events
- errors/ - Error codes
- exceptions/ - Domain exceptions
"""

from .entities import File
from .errors import FileErrorCode, register_file_error_codes
from .events import (
    FileDeletedEvent,
    FileDownloadedEvent,
    FileSharedEvent,
    FileUpdatedEvent,
    FileUploadedEvent,
)
from .exceptions import (
    FileAccessDeniedException,
    FileNotFoundException,
    FileSizeLimitExceededException,
    InvalidFilePathException,
    InvalidFileSizeException,
    InvalidFileTypeException,
    InvalidMimeTypeException,
)
from .value_objects import FilePath, FileSize, MimeType

__all__ = [
    # Entities
    "File",
    # Value Objects
    "FilePath",
    "FileSize",
    "MimeType",
    # Events
    "FileUploadedEvent",
    "FileUpdatedEvent",
    "FileDeletedEvent",
    "FileSharedEvent",
    "FileDownloadedEvent",
    # Errors
    "FileErrorCode",
    "register_file_error_codes",
    # Exceptions
    "FileNotFoundException",
    "FileAccessDeniedException",
    "FileSizeLimitExceededException",
    "InvalidFilePathException",
    "InvalidFileSizeException",
    "InvalidFileTypeException",
    "InvalidMimeTypeException",
]
