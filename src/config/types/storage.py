"""
Storage configuration types - Port & Adapter pattern.

Contains:
- StorageAdapterType: Enum for adapter selection
- StorageConfigType: Common/Port interface for all storage adapters
- LocalStorageConfigType: Local filesystem adapter specific
- S3StorageConfigType: AWS S3 adapter specific
"""

from enum import Enum
from typing import List, Literal, Optional, TypedDict


class StorageAdapterType(str, Enum):
    """Available storage adapter types."""

    LOCAL = "local"
    S3 = "s3"


class StorageConfigType(TypedDict):
    """
    Storage configuration type - Common/Port interface.

    This is the base storage config that all adapters share.
    """

    # Adapter selection
    adapter: Literal["local", "s3"]

    # Upload settings
    max_upload_size: int
    allowed_extensions: List[str]
    blocked_extensions: List[str]

    # Image settings
    image_max_width: int
    image_max_height: int
    image_quality: int

    # Thumbnail settings
    thumbnail_enabled: bool
    thumbnail_width: int
    thumbnail_height: int

    # Cleanup settings
    temp_file_lifetime_hours: int
    auto_cleanup_enabled: bool


class LocalStorageConfigType(TypedDict):
    """
    Local filesystem storage adapter configuration type.

    Used when storing files on local filesystem.
    """

    # Paths
    upload_dir: str
    temp_dir: str
    static_dir: str

    # Permissions
    file_permissions: int
    directory_permissions: int

    # Common settings inherited from StorageConfig
    max_upload_size: int
    allowed_extensions: List[str]
    blocked_extensions: List[str]
    image_max_width: int
    image_max_height: int
    image_quality: int
    thumbnail_enabled: bool
    thumbnail_width: int
    thumbnail_height: int
    temp_file_lifetime_hours: int
    auto_cleanup_enabled: bool


class S3StorageConfigType(TypedDict):
    """
    AWS S3 storage adapter configuration type.

    Used when storing files on AWS S3 or S3-compatible services.
    """

    # S3 connection
    bucket: str
    region: str
    access_key_id: Optional[str]
    secret_access_key: Optional[str]
    endpoint_url: Optional[str]  # For S3-compatible services (MinIO, etc.)

    # Paths
    upload_prefix: str
    temp_prefix: str
    static_prefix: str

    # S3 settings
    acl: str
    storage_class: str
    presigned_url_expiry: int

    # Common settings inherited from StorageConfig
    max_upload_size: int
    allowed_extensions: List[str]
    blocked_extensions: List[str]
    image_max_width: int
    image_max_height: int
    image_quality: int
    thumbnail_enabled: bool
    thumbnail_width: int
    thumbnail_height: int
    temp_file_lifetime_hours: int
    auto_cleanup_enabled: bool
