"""
Logging configuration - Common/Port interface.

This is the PORT that defines what all logging adapters need.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import LoggingConfigType


class LoggingConfig(BaseSettings):
    """
    Common logging configuration (Port interface).

    This config is used to select which adapter to use and common settings.
    Adapter-specific configs (StandardLoggerConfig, etc.) extend this.

    Environment Variables:
        LOG_ADAPTER: Logging adapter type (standard | structlog)
        LOG_LEVEL: Logging level
        LOG_FORMAT: Log format (json | text)
        LOG_DIR: Log directory path
        LOG_FILE_ENABLED: Enable file logging
        LOG_USE_DAILY_ROTATION: Use daily rotation
        LOG_MAX_BYTES: Max log file size
        LOG_BACKUP_COUNT: Number of backup files
        LOG_RETENTION_DAYS: Days to retain logs
        LOG_CONSOLE_ENABLED: Enable console logging
        LOG_CONSOLE_COLORED: Enable colored output
    """

    LOG_ADAPTER: Literal["standard", "structlog"] = Field(
        default="standard",
        description="Logging adapter: standard | structlog",
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    LOG_FORMAT: Literal["json", "text"] = Field(
        default="text",
        description="Log format: json | text",
    )
    LOG_DIR: str = Field(
        default="logs",
        description="Log directory path",
    )
    LOG_FILE_ENABLED: bool = Field(
        default=True,
        description="Enable file logging",
    )
    LOG_USE_DAILY_ROTATION: bool = Field(
        default=True,
        description="Use daily rotation (True) or size-based (False)",
    )
    LOG_MAX_BYTES: int = Field(
        default=10 * 1024 * 1024,
        ge=1024,
        description="Max log file size in bytes",
    )
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        ge=0,
        description="Number of backup files",
    )
    LOG_RETENTION_DAYS: int = Field(
        default=30,
        ge=1,
        description="Days to retain old logs",
    )
    LOG_CONSOLE_ENABLED: bool = Field(
        default=True,
        description="Enable console logging",
    )
    LOG_CONSOLE_COLORED: bool = Field(
        default=True,
        description="Enable colored console output",
    )
    LOG_JSON_INDENT: int = Field(
        default=2,
        ge=0,
        description="JSON log indentation",
    )
    LOG_INCLUDE_EXTRA_FIELDS: bool = Field(
        default=True,
        description="Include extra fields in logs",
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is uppercase."""
        return v.upper()

    @property
    def is_standard(self) -> bool:
        """Check if using standard adapter."""
        return self.LOG_ADAPTER == "standard"

    @property
    def is_json_format(self) -> bool:
        """Check if using JSON format."""
        return self.LOG_FORMAT == "json"

    @property
    def is_debug(self) -> bool:
        """Check if debug level."""
        return self.LOG_LEVEL == "DEBUG"

    def to_dict(self) -> LoggingConfigType:
        """Convert to typed dictionary format."""
        return LoggingConfigType(
            adapter=self.LOG_ADAPTER,
            level=self.LOG_LEVEL,
            format=self.LOG_FORMAT,
        )
