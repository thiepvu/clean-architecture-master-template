"""
AWS S3 storage adapter configuration.

Used when storing files on AWS S3 or S3-compatible services (MinIO, etc.).
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import S3StorageConfigType

if TYPE_CHECKING:
    from config.storage import StorageConfig


class S3StorageSettings(BaseSettings):
    """
    S3 storage settings loaded from environment.

    Environment Variables:
        S3_BUCKET: S3 bucket name
        S3_REGION: AWS region
        AWS_ACCESS_KEY_ID: AWS access key ID
        AWS_SECRET_ACCESS_KEY: AWS secret access key
        S3_ENDPOINT_URL: Custom endpoint URL (for MinIO, etc.)
        S3_UPLOAD_PREFIX: Upload directory prefix
        S3_TEMP_PREFIX: Temporary files prefix
        S3_STATIC_PREFIX: Static files prefix
        S3_ACL: S3 ACL for uploaded files
        S3_STORAGE_CLASS: S3 storage class
        S3_PRESIGNED_URL_EXPIRY: Presigned URL expiry in seconds
    """

    S3_BUCKET: str = Field(default="", description="S3 bucket name")
    S3_REGION: str = Field(default="us-east-1", description="AWS region")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS secret access key")
    S3_ENDPOINT_URL: Optional[str] = Field(
        default=None, description="Custom endpoint URL (MinIO, etc.)"
    )
    S3_UPLOAD_PREFIX: str = Field(default="uploads/", description="Upload directory prefix")
    S3_TEMP_PREFIX: str = Field(default="temp/", description="Temporary files prefix")
    S3_STATIC_PREFIX: str = Field(default="static/", description="Static files prefix")
    S3_ACL: str = Field(default="private", description="S3 ACL for uploaded files")
    S3_STORAGE_CLASS: str = Field(default="STANDARD", description="S3 storage class")
    S3_PRESIGNED_URL_EXPIRY: int = Field(
        default=3600, ge=60, description="Presigned URL expiry in seconds"
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )


@dataclass
class S3StorageConfig:
    """
    AWS S3 storage adapter configuration.

    Contains all settings needed to store files on S3.
    Created from S3StorageSettings + StorageConfig.
    """

    # S3 connection
    bucket: str
    region: str
    access_key_id: Optional[str]
    secret_access_key: Optional[str]
    endpoint_url: Optional[str]

    # Paths
    upload_prefix: str
    temp_prefix: str
    static_prefix: str

    # S3 settings
    acl: str
    storage_class: str
    presigned_url_expiry: int

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
        s3_settings: S3StorageSettings,
        storage_config: "StorageConfig",
    ) -> "S3StorageConfig":
        """
        Create from S3StorageSettings and StorageConfig.

        Args:
            s3_settings: S3 storage settings
            storage_config: Common storage configuration

        Returns:
            S3StorageConfig instance
        """
        return cls(
            bucket=s3_settings.S3_BUCKET,
            region=s3_settings.S3_REGION,
            access_key_id=s3_settings.AWS_ACCESS_KEY_ID,
            secret_access_key=s3_settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=s3_settings.S3_ENDPOINT_URL,
            upload_prefix=s3_settings.S3_UPLOAD_PREFIX,
            temp_prefix=s3_settings.S3_TEMP_PREFIX,
            static_prefix=s3_settings.S3_STATIC_PREFIX,
            acl=s3_settings.S3_ACL,
            storage_class=s3_settings.S3_STORAGE_CLASS,
            presigned_url_expiry=s3_settings.S3_PRESIGNED_URL_EXPIRY,
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

    def to_dict(self) -> S3StorageConfigType:
        """Convert to typed dictionary format."""
        return S3StorageConfigType(
            bucket=self.bucket,
            region=self.region,
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            endpoint_url=self.endpoint_url,
            upload_prefix=self.upload_prefix,
            temp_prefix=self.temp_prefix,
            static_prefix=self.static_prefix,
            acl=self.acl,
            storage_class=self.storage_class,
            presigned_url_expiry=self.presigned_url_expiry,
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
