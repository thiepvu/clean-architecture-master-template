"""File-specific domain exceptions"""

from typing import Any
from uuid import UUID

from shared.errors.exceptions import DomainException


class InvalidFilePathException(DomainException):
    """Invalid file path exception"""

    def __init__(self, path: Any, reason: str = "Invalid path format"):
        super().__init__(
            message=f"Invalid file path: {path} - {reason}",
            details={"path": str(path), "reason": reason},
        )


class InvalidFileSizeException(DomainException):
    """Invalid file size exception"""

    def __init__(self, size: Any):
        super().__init__(message=f"Invalid file size: {size}", details={"size": str(size)})


class InvalidMimeTypeException(DomainException):
    """Invalid MIME type exception"""

    def __init__(self, mime_type: str):
        super().__init__(
            message=f"Invalid MIME type: {mime_type}", details={"mime_type": mime_type}
        )


class FileSizeLimitExceededException(DomainException):
    """File size limit exceeded exception"""

    def __init__(self, size: int, max_size: int):
        super().__init__(
            message=f"File size {size} bytes exceeds maximum {max_size} bytes",
            details={"size": size, "max_size": max_size},
        )


class InvalidFileTypeException(DomainException):
    """Invalid file type exception"""

    def __init__(self, mime_type: str):
        super().__init__(
            message=f"File type not allowed: {mime_type}", details={"mime_type": mime_type}
        )


class FileAccessDeniedException(DomainException):
    """File access denied exception"""

    def __init__(self, file_id: UUID, user_id: UUID):
        super().__init__(
            message=f"User {user_id} does not have access to file {file_id}",
            details={"file_id": str(file_id), "user_id": str(user_id)},
        )


class FileNotFoundException(DomainException):
    """File not found exception"""

    def __init__(self, file_id: UUID):
        super().__init__(message=f"File {file_id} not found", details={"file_id": str(file_id)})
