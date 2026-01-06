"""
Local Filesystem Storage Adapter.

Implements IStorageService for local filesystem storage.
"""

import os
import shutil
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Optional

import aiofiles
import aiofiles.os

from shared.application.ports.storage import (
    IStorageService,
    PresignedUrl,
    StorageError,
    StorageFile,
    StorageUploadError,
)

if TYPE_CHECKING:
    from config.storage import LocalStorageConfig
    from shared.application.ports import ILogger


class LocalStorageAdapter(IStorageService):
    """
    Local filesystem storage adapter.

    Implements IStorageService for storing files on local disk.
    Suitable for development and single-server deployments.

    Features:
    - Async file operations using aiofiles
    - Automatic directory creation
    - File metadata tracking
    - Support for copy/move operations
    """

    def __init__(
        self,
        config: "LocalStorageConfig",
        logger: Optional["ILogger"] = None,
    ):
        """
        Initialize local storage adapter.

        Args:
            config: Local storage configuration
            logger: Logger instance (optional)
        """
        self._config = config
        self._logger = logger
        self._base_path = Path(config.upload_dir)
        self._temp_path = Path(config.temp_dir)
        self._static_path = Path(config.static_dir)
        self._initialized = False

    @property
    def base_path(self) -> Path:
        """Get base storage path."""
        return self._base_path

    async def initialize(self) -> None:
        """
        Initialize the storage service.

        Creates required directories with proper permissions.
        """
        if self._initialized:
            return

        try:
            # Create directories
            for path in [self._base_path, self._temp_path, self._static_path]:
                path.mkdir(parents=True, exist_ok=True)
                os.chmod(path, self._config.directory_permissions)

            self._initialized = True
            if self._logger:
                self._logger.info(
                    f"Local storage initialized: {self._base_path}",
                    extra={"base_path": str(self._base_path)},
                )
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to initialize local storage: {e}")
            raise StorageError(f"Failed to initialize storage: {e}") from e

    async def close(self) -> None:
        """Close the storage service."""
        self._initialized = False
        if self._logger:
            self._logger.info("Local storage closed")

    async def health_check(self) -> bool:
        """
        Check if storage service is healthy.

        Verifies that the base directory exists and is writable.
        """
        try:
            if not self._base_path.exists():
                return False

            # Try to create and delete a test file
            test_file = self._base_path / ".health_check"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Storage health check failed: {e}")
            return False

    def _get_full_path(self, path: str) -> Path:
        """Get full filesystem path from relative path."""
        return self._base_path / path

    def _ensure_parent_dir(self, file_path: Path) -> None:
        """Ensure parent directory exists."""
        parent = file_path.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
            os.chmod(parent, self._config.directory_permissions)

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
            file_content: File binary content
            path: Target path in storage
            content_type: MIME type (optional)
            metadata: Additional metadata (optional)

        Returns:
            StorageFile with metadata

        Raises:
            StorageUploadError: If save fails
        """
        full_path = self._get_full_path(path)
        self._ensure_parent_dir(full_path)

        try:
            content = file_content.read()
            async with aiofiles.open(full_path, "wb") as f:
                await f.write(content)

            os.chmod(full_path, self._config.file_permissions)

            stat = full_path.stat()
            now = datetime.now(timezone.utc)

            if self._logger:
                self._logger.debug(f"File saved: {path}", extra={"size": len(content)})

            return StorageFile(
                path=path,
                filename=full_path.name,
                size=stat.st_size,
                content_type=content_type,
                created_at=now,
                updated_at=now,
                metadata=metadata,
            )
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to save file {path}: {e}")
            raise StorageUploadError(f"Failed to save file: {e}") from e

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
            content_type: MIME type (optional)
            metadata: Additional metadata (optional)

        Returns:
            StorageFile with metadata
        """
        return await self.save(
            file_content=BytesIO(content),
            path=path,
            content_type=content_type,
            metadata=metadata,
        )

    async def read(self, path: str) -> bytes:
        """
        Read file from storage.

        Args:
            path: File path in storage

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        full_path = self._get_full_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        async with aiofiles.open(full_path, "rb") as f:
            content = await f.read()

        if self._logger:
            self._logger.debug(f"File read: {path}", extra={"size": len(content)})

        return content

    async def delete(self, path: str) -> bool:
        """
        Delete file from storage.

        Args:
            path: File path in storage

        Returns:
            True if deleted, False if not found
        """
        full_path = self._get_full_path(path)

        if not full_path.exists():
            return False

        try:
            await aiofiles.os.remove(full_path)
            if self._logger:
                self._logger.debug(f"File deleted: {path}")
            return True
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to delete file {path}: {e}")
            return False

    async def exists(self, path: str) -> bool:
        """
        Check if file exists.

        Args:
            path: File path in storage

        Returns:
            True if exists
        """
        full_path = self._get_full_path(path)
        return full_path.exists()

    async def get_metadata(self, path: str) -> Optional[StorageFile]:
        """
        Get file metadata without reading content.

        Args:
            path: File path in storage

        Returns:
            StorageFile or None if not found
        """
        full_path = self._get_full_path(path)

        if not full_path.exists():
            return None

        stat = full_path.stat()
        return StorageFile(
            path=path,
            filename=full_path.name,
            size=stat.st_size,
            content_type=None,
            created_at=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc),
            updated_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            metadata=None,
        )

    async def list_files(
        self,
        prefix: str = "",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[StorageFile]:
        """
        List files in storage with optional prefix filter.

        Args:
            prefix: Path prefix to filter
            limit: Max files to return
            offset: Files to skip

        Returns:
            List of StorageFile objects
        """
        search_path = self._get_full_path(prefix)
        files: list[StorageFile] = []

        if not search_path.exists():
            return files

        # Handle both file and directory
        if search_path.is_file():
            meta = await self.get_metadata(prefix)
            if meta:
                files.append(meta)
        else:
            for item in search_path.rglob("*"):
                if item.is_file():
                    relative_path = str(item.relative_to(self._base_path))
                    meta = await self.get_metadata(relative_path)
                    if meta:
                        files.append(meta)

        # Apply offset and limit
        if offset:
            files = files[offset:]
        if limit:
            files = files[:limit]

        return files

    async def copy(self, source_path: str, dest_path: str) -> StorageFile:
        """
        Copy file within storage.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            StorageFile with metadata of copied file

        Raises:
            FileNotFoundError: If source doesn't exist
        """
        source_full = self._get_full_path(source_path)
        dest_full = self._get_full_path(dest_path)

        if not source_full.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        self._ensure_parent_dir(dest_full)
        shutil.copy2(source_full, dest_full)
        os.chmod(dest_full, self._config.file_permissions)

        if self._logger:
            self._logger.debug(f"File copied: {source_path} -> {dest_path}")

        meta = await self.get_metadata(dest_path)
        if not meta:
            raise StorageError(f"Failed to get metadata after copy: {dest_path}")
        return meta

    async def move(self, source_path: str, dest_path: str) -> StorageFile:
        """
        Move/rename file within storage.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            StorageFile with metadata of moved file

        Raises:
            FileNotFoundError: If source doesn't exist
        """
        source_full = self._get_full_path(source_path)
        dest_full = self._get_full_path(dest_path)

        if not source_full.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        self._ensure_parent_dir(dest_full)
        shutil.move(str(source_full), str(dest_full))

        if self._logger:
            self._logger.debug(f"File moved: {source_path} -> {dest_path}")

        meta = await self.get_metadata(dest_path)
        if not meta:
            raise StorageError(f"Failed to get metadata after move: {dest_path}")
        return meta

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Get URL for file access.

        For local storage, returns a relative path.

        Args:
            path: File path in storage
            expires_in: Ignored for local storage

        Returns:
            Relative path string
        """
        # For local storage, just return the relative path
        # The web framework should handle serving static files
        return f"/static/{path}"

    async def get_presigned_url(
        self,
        path: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> PresignedUrl:
        """
        Get presigned URL for file operations.

        Local storage doesn't support presigned URLs.
        Returns a simple URL that the web framework should handle.

        Args:
            path: File path in storage
            expires_in: URL expiration (used for expiry timestamp)
            method: HTTP method (GET/PUT)

        Returns:
            PresignedUrl with local path
        """
        url = await self.get_url(path, expires_in)
        expires_at = datetime.now(timezone.utc).replace(microsecond=0)  # Local URLs don't expire

        return PresignedUrl(
            url=url,
            expires_at=expires_at,
            method=method,
        )

    async def get_upload_url(self, path: str, expires_in: int = 3600) -> PresignedUrl:
        """
        Get presigned URL for direct upload.

        Local storage doesn't support direct uploads.
        Raises NotImplementedError.

        Args:
            path: Target file path
            expires_in: URL expiration

        Raises:
            NotImplementedError: Local storage doesn't support presigned uploads
        """
        raise NotImplementedError(
            "Local storage doesn't support presigned upload URLs. " "Use save() method instead."
        )
