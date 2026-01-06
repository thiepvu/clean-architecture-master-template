"""
Local filesystem storage adapter configuration.

Used when storing files on local filesystem.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import LocalStorageConfigType

if TYPE_CHECKING:
    from config.storage import StorageConfig


class LocalStorageSettings(BaseSettings):
    """
    Local storage settings loaded from environment.

    Environment Variables:
        UPLOAD_DIR: Upload directory path
        TEMP_DIR: Temporary files directory
        STATIC_DIR: Static files directory
        FILE_PERMISSIONS: File permissions (octal)
        DIRECTORY_PERMISSIONS: Directory permissions (octal)
    """

    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory path")
    TEMP_DIR: str = Field(default="temp", description="Temporary files directory")
    STATIC_DIR: str = Field(default="static", description="Static files directory")
    FILE_PERMISSIONS: int = Field(default=0o644, description="File permissions (octal)")
    DIRECTORY_PERMISSIONS: int = Field(default=0o755, description="Directory permissions (octal)")

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )


@dataclass
class LocalStorageConfig:
    """
    Local filesystem storage adapter configuration.

    Contains all settings needed to store files on local filesystem.
    Created from LocalStorageSettings + StorageConfig.
    """

    # Paths
    upload_dir: str
    temp_dir: str
    static_dir: str

    # Permissions
    file_permissions: int
    directory_permissions: int

    # Common settings from StorageConfig
    max_upload_size: int
    allowed_extensions: list
    blocked_extensions: list
    image_max_width: int
    image_max_height: int
    image_quality: int
    thumbnail_enabled: bool
    thumbnail_width: int
    thumbnail_height: int
    temp_file_lifetime_hours: int
    auto_cleanup_enabled: bool

    @classmethod
    def from_settings(
        cls,
        local_settings: LocalStorageSettings,
        storage_config: "StorageConfig",
    ) -> "LocalStorageConfig":
        """
        Create from LocalStorageSettings and StorageConfig.

        Args:
            local_settings: Local storage settings
            storage_config: Common storage configuration

        Returns:
            LocalStorageConfig instance
        """
        return cls(
            upload_dir=local_settings.UPLOAD_DIR,
            temp_dir=local_settings.TEMP_DIR,
            static_dir=local_settings.STATIC_DIR,
            file_permissions=local_settings.FILE_PERMISSIONS,
            directory_permissions=local_settings.DIRECTORY_PERMISSIONS,
            max_upload_size=storage_config.MAX_UPLOAD_SIZE,
            allowed_extensions=storage_config.ALLOWED_EXTENSIONS,
            blocked_extensions=storage_config.BLOCKED_EXTENSIONS,
            image_max_width=storage_config.IMAGE_MAX_WIDTH,
            image_max_height=storage_config.IMAGE_MAX_HEIGHT,
            image_quality=storage_config.IMAGE_QUALITY,
            thumbnail_enabled=storage_config.THUMBNAIL_ENABLED,
            thumbnail_width=storage_config.THUMBNAIL_WIDTH,
            thumbnail_height=storage_config.THUMBNAIL_HEIGHT,
            temp_file_lifetime_hours=storage_config.TEMP_FILE_LIFETIME_HOURS,
            auto_cleanup_enabled=storage_config.AUTO_CLEANUP_ENABLED,
        )

    def to_dict(self) -> LocalStorageConfigType:
        """Convert to typed dictionary format."""
        return LocalStorageConfigType(
            upload_dir=self.upload_dir,
            temp_dir=self.temp_dir,
            static_dir=self.static_dir,
            file_permissions=self.file_permissions,
            directory_permissions=self.directory_permissions,
            max_upload_size=self.max_upload_size,
            allowed_extensions=self.allowed_extensions,
            blocked_extensions=self.blocked_extensions,
            image_max_width=self.image_max_width,
            image_max_height=self.image_max_height,
            image_quality=self.image_quality,
            thumbnail_enabled=self.thumbnail_enabled,
            thumbnail_width=self.thumbnail_width,
            thumbnail_height=self.thumbnail_height,
            temp_file_lifetime_hours=self.temp_file_lifetime_hours,
            auto_cleanup_enabled=self.auto_cleanup_enabled,
        )
