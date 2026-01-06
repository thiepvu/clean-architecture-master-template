"""
Storage Service Port (Interface).

Defines the contract for file storage operations.
Implementations: LocalStorageAdapter, S3StorageAdapter
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, BinaryIO, Optional, Protocol, runtime_checkable


@dataclass
class StorageFile:
    """Metadata about a stored file."""

    path: str
    filename: str
    size: int
    content_type: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None


@dataclass
class PresignedUrl:
    """Presigned URL for file access."""

    url: str
    expires_at: datetime
    method: str = "GET"


@runtime_checkable
class IStorageService(Protocol):
    """
    Storage service port (interface).

    All storage adapters must implement this protocol.
    Supports async operations with health checking.

    Example:
        class LocalStorageAdapter:
            async def save(
                self,
                file_content: BinaryIO,
                path: str,
            ) -> StorageFile:
                ...
    """

    async def save(
        self,
        file_content: BinaryIO,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StorageFile:
        """
        Save file to storage.

        Args:
            file_content: File binary content (file-like object)
            path: Target path in storage (e.g., "users/123/avatar.png")
            content_type: MIME type of the file (optional)
            metadata: Additional metadata to store with the file (optional)

        Returns:
            StorageFile with metadata about the saved file

        Raises:
            StorageError: If save operation fails
        """
        ...

    async def save_bytes(
        self,
        content: bytes,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StorageFile:
        """
        Save bytes content to storage.

        Args:
            content: File content as bytes
            path: Target path in storage
            content_type: MIME type of the file (optional)
            metadata: Additional metadata to store with the file (optional)

        Returns:
            StorageFile with metadata about the saved file

        Raises:
            StorageError: If save operation fails
        """
        ...

    async def read(self, path: str) -> bytes:
        """
        Read file from storage.

        Args:
            path: File path in storage

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            StorageError: If read operation fails
        """
        ...

    async def delete(self, path: str) -> bool:
        """
        Delete file from storage.

        Args:
            path: File path in storage

        Returns:
            True if file was deleted, False if file didn't exist
        """
        ...

    async def exists(self, path: str) -> bool:
        """
        Check if file exists in storage.

        Args:
            path: File path in storage

        Returns:
            True if file exists, False otherwise
        """
        ...

    async def get_metadata(self, path: str) -> Optional[StorageFile]:
        """
        Get file metadata without reading content.

        Args:
            path: File path in storage

        Returns:
            StorageFile with metadata, or None if file doesn't exist
        """
        ...

    async def list_files(
        self,
        prefix: str = "",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[StorageFile]:
        """
        List files in storage with optional prefix filter.

        Args:
            prefix: Path prefix to filter files (e.g., "users/123/")
            limit: Maximum number of files to return (optional)
            offset: Number of files to skip (optional, for pagination)

        Returns:
            List of StorageFile objects
        """
        ...

    async def copy(self, source_path: str, dest_path: str) -> StorageFile:
        """
        Copy file within storage.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            StorageFile with metadata about the copied file

        Raises:
            FileNotFoundError: If source file doesn't exist
            StorageError: If copy operation fails
        """
        ...

    async def move(self, source_path: str, dest_path: str) -> StorageFile:
        """
        Move/rename file within storage.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            StorageFile with metadata about the moved file

        Raises:
            FileNotFoundError: If source file doesn't exist
            StorageError: If move operation fails
        """
        ...

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Get URL for file access.

        For local storage, returns a relative path.
        For S3, returns a presigned URL.

        Args:
            path: File path in storage
            expires_in: URL expiration time in seconds (for S3)

        Returns:
            URL string for accessing the file
        """
        ...

    async def get_presigned_url(
        self,
        path: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> PresignedUrl:
        """
        Get presigned URL for file operations.

        For local storage, this may not be applicable.
        For S3, returns a presigned URL for the specified method.

        Args:
            path: File path in storage
            expires_in: URL expiration time in seconds
            method: HTTP method (GET for download, PUT for upload)

        Returns:
            PresignedUrl with URL and expiration info

        Raises:
            NotImplementedError: If adapter doesn't support presigned URLs
        """
        ...

    async def get_upload_url(self, path: str, expires_in: int = 3600) -> PresignedUrl:
        """
        Get presigned URL for direct upload (S3 only).

        Args:
            path: Target file path in storage
            expires_in: URL expiration time in seconds

        Returns:
            PresignedUrl with upload URL and expiration info

        Raises:
            NotImplementedError: If adapter doesn't support presigned uploads
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if storage service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        ...

    async def initialize(self) -> None:
        """
        Initialize the storage service.

        Called during application startup.
        Should create directories, verify permissions, etc.
        """
        ...

    async def close(self) -> None:
        """
        Close the storage service.

        Called during application shutdown.
        Should cleanup connections and resources.
        """
        ...


class StorageError(Exception):
    """Base exception for storage operations."""

    pass


class StorageUploadError(StorageError):
    """Exception raised when file upload fails."""

    pass


class StorageDownloadError(StorageError):
    """Exception raised when file download fails."""

    pass


class StoragePermissionError(StorageError):
    """Exception raised when permission is denied."""

    pass
