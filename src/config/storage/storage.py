"""
Storage configuration - Common/Port.

This is the common storage config that all adapters share.
"""

from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import StorageConfigType


class StorageConfig(BaseSettings):
    """
    Storage configuration - Common/Port.

    Contains settings shared across all storage adapters (local, s3, etc.).

    Environment Variables:
        STORAGE_ADAPTER: Storage adapter type ("local" or "s3")
        MAX_UPLOAD_SIZE: Maximum upload size in bytes
        ALLOWED_EXTENSIONS: Comma-separated list of allowed extensions
        BLOCKED_EXTENSIONS: Comma-separated list of blocked extensions
        IMAGE_MAX_WIDTH: Maximum image width in pixels
        IMAGE_MAX_HEIGHT: Maximum image height in pixels
        IMAGE_QUALITY: Image compression quality (1-100)
        THUMBNAIL_ENABLED: Enable thumbnail generation
        THUMBNAIL_WIDTH: Thumbnail width in pixels
        THUMBNAIL_HEIGHT: Thumbnail height in pixels
        TEMP_FILE_LIFETIME_HOURS: Temporary file lifetime in hours
        AUTO_CLEANUP_ENABLED: Enable automatic cleanup
    """

    STORAGE_ADAPTER: Literal["local", "s3"] = Field(
        default="local", description="Storage adapter type"
    )

    # Upload settings
    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        ge=1024,
        description="Maximum upload size in bytes",
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default_factory=lambda: [
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "png",
            "jpg",
            "jpeg",
            "gif",
            "webp",
            "txt",
            "csv",
            "json",
        ],
        description="Allowed file extensions",
    )
    BLOCKED_EXTENSIONS: List[str] = Field(
        default_factory=lambda: [
            "exe",
            "bat",
            "sh",
            "cmd",
            "com",
            "scr",
            "vbs",
            "js",
            "jar",
        ],
        description="Blocked file extensions",
    )

    # Image settings
    IMAGE_MAX_WIDTH: int = Field(default=4096, ge=100, description="Maximum image width in pixels")
    IMAGE_MAX_HEIGHT: int = Field(
        default=4096, ge=100, description="Maximum image height in pixels"
    )
    IMAGE_QUALITY: int = Field(
        default=85, ge=1, le=100, description="Image compression quality (1-100)"
    )

    # Thumbnail settings
    THUMBNAIL_ENABLED: bool = Field(default=True, description="Enable thumbnail generation")
    THUMBNAIL_WIDTH: int = Field(default=300, ge=50, description="Thumbnail width in pixels")
    THUMBNAIL_HEIGHT: int = Field(default=300, ge=50, description="Thumbnail height in pixels")

    # Cleanup settings
    TEMP_FILE_LIFETIME_HOURS: int = Field(
        default=24, ge=1, description="Temporary file lifetime in hours"
    )
    AUTO_CLEANUP_ENABLED: bool = Field(
        default=True, description="Enable automatic cleanup of temporary files"
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("ALLOWED_EXTENSIONS", "BLOCKED_EXTENSIONS", mode="before")
    @classmethod
    def validate_extensions(cls, v):
        """Normalize file extensions."""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        if isinstance(v, list):
            return [ext.strip().lower().replace(".", "") for ext in v]
        return v

    @property
    def max_upload_size_mb(self) -> float:
        """Get max upload size in MB."""
        return self.MAX_UPLOAD_SIZE / (1024 * 1024)

    def is_allowed_extension(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext in self.BLOCKED_EXTENSIONS:
            return False
        return ext in self.ALLOWED_EXTENSIONS

    def to_dict(self) -> StorageConfigType:
        """Convert to typed dictionary format."""
        return StorageConfigType(
            adapter=self.STORAGE_ADAPTER,
            max_upload_size=self.MAX_UPLOAD_SIZE,
            allowed_extensions=self.ALLOWED_EXTENSIONS,
            blocked_extensions=self.BLOCKED_EXTENSIONS,
            image_max_width=self.IMAGE_MAX_WIDTH,
            image_max_height=self.IMAGE_MAX_HEIGHT,
            image_quality=self.IMAGE_QUALITY,
            thumbnail_enabled=self.THUMBNAIL_ENABLED,
            thumbnail_width=self.THUMBNAIL_WIDTH,
            thumbnail_height=self.THUMBNAIL_HEIGHT,
            temp_file_lifetime_hours=self.TEMP_FILE_LIFETIME_HOURS,
            auto_cleanup_enabled=self.AUTO_CLEANUP_ENABLED,
        )
