"""
AWS S3 Storage Adapter.

Implements IStorageService for AWS S3 and S3-compatible storage.

Requirements:
    pip install aiobotocore

Optional (for type hints):
    pip install types-aiobotocore[s3]
"""

from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import TYPE_CHECKING, Any, BinaryIO, Optional

from shared.application.ports.storage import (
    IStorageService,
    PresignedUrl,
    StorageDownloadError,
    StorageError,
    StorageFile,
    StorageUploadError,
)

if TYPE_CHECKING:
    try:
        from types_aiobotocore_s3 import S3Client
    except ImportError:
        S3Client = Any  # type: ignore

    from config.storage import S3StorageConfig
    from shared.application.ports import ILogger


class S3StorageAdapter(IStorageService):
    """
    AWS S3 storage adapter.

    Implements IStorageService for storing files on S3 or S3-compatible services.
    Suitable for production and distributed deployments.

    Features:
    - Async operations using aiobotocore
    - Presigned URL generation for uploads/downloads
    - Support for S3-compatible services (MinIO, DigitalOcean Spaces, etc.)
    - Configurable ACL and storage class
    """

    def __init__(
        self,
        config: "S3StorageConfig",
        logger: Optional["ILogger"] = None,
    ):
        """
        Initialize S3 storage adapter.

        Args:
            config: S3 storage configuration
            logger: Logger instance (optional)
        """
        self._config = config
        self._logger = logger
        self._client: Optional["S3Client"] = None
        self._session = None
        self._initialized = False

    @property
    def bucket(self) -> str:
        """Get S3 bucket name."""
        return self._config.bucket

    def _get_s3_key(self, path: str) -> str:
        """Convert path to S3 key with prefix."""
        prefix = self._config.upload_prefix.rstrip("/")
        return f"{prefix}/{path}" if prefix else path

    async def initialize(self) -> None:
        """
        Initialize the S3 client.

        Creates aiobotocore session and S3 client.
        """
        if self._initialized:
            return

        try:
            from aiobotocore.session import get_session

            self._session = get_session()

            # Build client configuration
            client_kwargs: dict[str, Any] = {
                "region_name": self._config.region,
            }

            if self._config.access_key_id and self._config.secret_access_key:
                client_kwargs["aws_access_key_id"] = self._config.access_key_id
                client_kwargs["aws_secret_access_key"] = self._config.secret_access_key

            if self._config.endpoint_url:
                client_kwargs["endpoint_url"] = self._config.endpoint_url

            # Create client context manager
            self._client_cm = self._session.create_client("s3", **client_kwargs)
            self._client = await self._client_cm.__aenter__()

            self._initialized = True
            if self._logger:
                self._logger.info(
                    f"S3 storage initialized: {self._config.bucket}",
                    extra={
                        "bucket": self._config.bucket,
                        "region": self._config.region,
                    },
                )
        except ImportError as e:
            raise StorageError(
                "aiobotocore is required for S3 storage. " "Install with: pip install aiobotocore"
            ) from e
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to initialize S3 storage: {e}")
            raise StorageError(f"Failed to initialize S3 storage: {e}") from e

    async def close(self) -> None:
        """Close the S3 client."""
        if self._client and hasattr(self, "_client_cm"):
            await self._client_cm.__aexit__(None, None, None)
            self._client = None
            self._initialized = False
            if self._logger:
                self._logger.info("S3 storage closed")

    async def health_check(self) -> bool:
        """
        Check if S3 storage is healthy.

        Attempts to list objects (with max 1) to verify connectivity.
        """
        if not self._client:
            return False

        try:
            await self._client.list_objects_v2(
                Bucket=self._config.bucket,
                MaxKeys=1,
            )
            return True
        except Exception as e:
            if self._logger:
                self._logger.warning(f"S3 health check failed: {e}")
            return False

    async def save(
        self,
        file_content: BinaryIO,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StorageFile:
        """
        Save file to S3.

        Args:
            file_content: File binary content
            path: Target path in storage
            content_type: MIME type (optional)
            metadata: Additional metadata (optional)

        Returns:
            StorageFile with metadata

        Raises:
            StorageUploadError: If upload fails
        """
        if not self._client:
            raise StorageError("S3 client not initialized")

        s3_key = self._get_s3_key(path)
        content = file_content.read()

        try:
            put_kwargs: dict[str, Any] = {
                "Bucket": self._config.bucket,
                "Key": s3_key,
                "Body": content,
                "ACL": self._config.acl,
                "StorageClass": self._config.storage_class,
            }

            if content_type:
                put_kwargs["ContentType"] = content_type

            if metadata:
                # S3 metadata values must be strings
                put_kwargs["Metadata"] = {k: str(v) for k, v in metadata.items()}

            await self._client.put_object(**put_kwargs)

            now = datetime.now(timezone.utc)

            if self._logger:
                self._logger.debug(
                    f"File uploaded to S3: {path}",
                    extra={"s3_key": s3_key, "size": len(content)},
                )

            return StorageFile(
                path=path,
                filename=path.split("/")[-1],
                size=len(content),
                content_type=content_type,
                created_at=now,
                updated_at=now,
                metadata=metadata,
            )
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to upload to S3 {path}: {e}")
            raise StorageUploadError(f"Failed to upload to S3: {e}") from e

    async def save_bytes(
        self,
        content: bytes,
        path: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> StorageFile:
        """
        Save bytes content to S3.

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
        Read file from S3.

        Args:
            path: File path in storage

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            StorageDownloadError: If download fails
        """
        if not self._client:
            raise StorageError("S3 client not initialized")

        s3_key = self._get_s3_key(path)

        try:
            response = await self._client.get_object(
                Bucket=self._config.bucket,
                Key=s3_key,
            )
            async with response["Body"] as stream:
                content = await stream.read()

            if self._logger:
                self._logger.debug(
                    f"File downloaded from S3: {path}",
                    extra={"size": len(content)},
                )

            return content
        except self._client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found in S3: {path}")
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to download from S3 {path}: {e}")
            raise StorageDownloadError(f"Failed to download from S3: {e}") from e

    async def delete(self, path: str) -> bool:
        """
        Delete file from S3.

        Args:
            path: File path in storage

        Returns:
            True (S3 delete is idempotent)
        """
        if not self._client:
            raise StorageError("S3 client not initialized")

        s3_key = self._get_s3_key(path)

        try:
            await self._client.delete_object(
                Bucket=self._config.bucket,
                Key=s3_key,
            )
            if self._logger:
                self._logger.debug(f"File deleted from S3: {path}")
            return True
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to delete from S3 {path}: {e}")
            return False

    async def exists(self, path: str) -> bool:
        """
        Check if file exists in S3.

        Args:
            path: File path in storage

        Returns:
            True if exists
        """
        if not self._client:
            return False

        s3_key = self._get_s3_key(path)

        try:
            await self._client.head_object(
                Bucket=self._config.bucket,
                Key=s3_key,
            )
            return True
        except Exception:
            return False

    async def get_metadata(self, path: str) -> Optional[StorageFile]:
        """
        Get file metadata from S3.

        Args:
            path: File path in storage

        Returns:
            StorageFile or None if not found
        """
        if not self._client:
            return None

        s3_key = self._get_s3_key(path)

        try:
            response = await self._client.head_object(
                Bucket=self._config.bucket,
                Key=s3_key,
            )

            # Parse S3 metadata
            s3_metadata = response.get("Metadata", {})
            last_modified = response.get("LastModified")

            return StorageFile(
                path=path,
                filename=path.split("/")[-1],
                size=response.get("ContentLength", 0),
                content_type=response.get("ContentType"),
                created_at=last_modified,
                updated_at=last_modified,
                metadata=s3_metadata if s3_metadata else None,
            )
        except Exception:
            return None

    async def list_files(
        self,
        prefix: str = "",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[StorageFile]:
        """
        List files in S3 with optional prefix filter.

        Args:
            prefix: Path prefix to filter
            limit: Max files to return
            offset: Files to skip (simulated, S3 uses continuation tokens)

        Returns:
            List of StorageFile objects
        """
        if not self._client:
            return []

        s3_prefix = self._get_s3_key(prefix)
        files: list[StorageFile] = []

        try:
            paginator = self._client.get_paginator("list_objects_v2")

            count = 0
            skipped = 0
            target_offset = offset or 0

            async for page in paginator.paginate(
                Bucket=self._config.bucket,
                Prefix=s3_prefix,
            ):
                for obj in page.get("Contents", []):
                    # Handle offset
                    if skipped < target_offset:
                        skipped += 1
                        continue

                    # Extract path without prefix
                    s3_key = obj["Key"]
                    upload_prefix = self._config.upload_prefix.rstrip("/")
                    if upload_prefix and s3_key.startswith(upload_prefix + "/"):
                        path = s3_key[len(upload_prefix) + 1 :]
                    else:
                        path = s3_key

                    files.append(
                        StorageFile(
                            path=path,
                            filename=path.split("/")[-1],
                            size=obj.get("Size", 0),
                            content_type=None,
                            created_at=obj.get("LastModified"),
                            updated_at=obj.get("LastModified"),
                            metadata=None,
                        )
                    )
                    count += 1

                    if limit and count >= limit:
                        return files

            return files
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to list S3 objects: {e}")
            return []

    async def copy(self, source_path: str, dest_path: str) -> StorageFile:
        """
        Copy file within S3.

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            StorageFile with metadata of copied file

        Raises:
            FileNotFoundError: If source doesn't exist
        """
        if not self._client:
            raise StorageError("S3 client not initialized")

        source_key = self._get_s3_key(source_path)
        dest_key = self._get_s3_key(dest_path)

        # Check if source exists
        if not await self.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        try:
            await self._client.copy_object(
                Bucket=self._config.bucket,
                CopySource={"Bucket": self._config.bucket, "Key": source_key},
                Key=dest_key,
                ACL=self._config.acl,
                StorageClass=self._config.storage_class,
            )

            if self._logger:
                self._logger.debug(f"File copied in S3: {source_path} -> {dest_path}")

            meta = await self.get_metadata(dest_path)
            if not meta:
                raise StorageError(f"Failed to get metadata after copy: {dest_path}")
            return meta
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to copy in S3: {e}")
            raise StorageError(f"Failed to copy file in S3: {e}") from e

    async def move(self, source_path: str, dest_path: str) -> StorageFile:
        """
        Move/rename file within S3 (copy + delete).

        Args:
            source_path: Source file path
            dest_path: Destination file path

        Returns:
            StorageFile with metadata of moved file

        Raises:
            FileNotFoundError: If source doesn't exist
        """
        # Copy first
        result = await self.copy(source_path, dest_path)

        # Then delete source
        await self.delete(source_path)

        if self._logger:
            self._logger.debug(f"File moved in S3: {source_path} -> {dest_path}")

        return result

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """
        Get presigned URL for file access.

        Args:
            path: File path in storage
            expires_in: URL expiration in seconds

        Returns:
            Presigned URL string
        """
        presigned = await self.get_presigned_url(path, expires_in, method="GET")
        return presigned.url

    async def get_presigned_url(
        self,
        path: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> PresignedUrl:
        """
        Get presigned URL for file operations.

        Args:
            path: File path in storage
            expires_in: URL expiration in seconds
            method: HTTP method (GET/PUT)

        Returns:
            PresignedUrl with URL and expiration info
        """
        if not self._client:
            raise StorageError("S3 client not initialized")

        s3_key = self._get_s3_key(path)
        client_method = "get_object" if method.upper() == "GET" else "put_object"

        url = await self._client.generate_presigned_url(
            ClientMethod=client_method,
            Params={
                "Bucket": self._config.bucket,
                "Key": s3_key,
            },
            ExpiresIn=expires_in,
        )

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        return PresignedUrl(
            url=url,
            expires_at=expires_at,
            method=method.upper(),
        )

    async def get_upload_url(self, path: str, expires_in: int = 3600) -> PresignedUrl:
        """
        Get presigned URL for direct upload.

        Args:
            path: Target file path
            expires_in: URL expiration in seconds

        Returns:
            PresignedUrl with upload URL and expiration info
        """
        return await self.get_presigned_url(path, expires_in, method="PUT")
