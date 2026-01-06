"""
Standard Python logger adapter configuration.

This is the ADAPTER-specific config for Python's built-in logging.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from config.types import StandardLoggerConfigType

if TYPE_CHECKING:
    from config.logging import LoggingConfig


@dataclass
class StandardLoggerConfig:
    """
    Standard Python logger adapter configuration.

    Contains all settings for Python's built-in logging.
    Created from LoggingConfig.
    """

    # Basic settings
    level: str
    format: str

    # File logging
    log_dir: str
    file_enabled: bool
    use_daily_rotation: bool
    max_bytes: int
    backup_count: int
    retention_days: int

    # Console settings
    console_enabled: bool
    console_colored: bool

    # Structured logging
    json_indent: int
    include_extra_fields: bool

    @classmethod
    def from_config(cls, logging_config: "LoggingConfig") -> "StandardLoggerConfig":
        """
        Create from LoggingConfig.

        Args:
            logging_config: Logging common configuration

        Returns:
            StandardLoggerConfig instance
        """
        return cls(
            level=logging_config.LOG_LEVEL,
            format=logging_config.LOG_FORMAT,
            log_dir=logging_config.LOG_DIR,
            file_enabled=logging_config.LOG_FILE_ENABLED,
            use_daily_rotation=logging_config.LOG_USE_DAILY_ROTATION,
            max_bytes=logging_config.LOG_MAX_BYTES,
            backup_count=logging_config.LOG_BACKUP_COUNT,
            retention_days=logging_config.LOG_RETENTION_DAYS,
            console_enabled=logging_config.LOG_CONSOLE_ENABLED,
            console_colored=logging_config.LOG_CONSOLE_COLORED,
            json_indent=logging_config.LOG_JSON_INDENT,
            include_extra_fields=logging_config.LOG_INCLUDE_EXTRA_FIELDS,
        )

    def to_dict(self) -> StandardLoggerConfigType:
        """Convert to typed dictionary format."""
        return StandardLoggerConfigType(
            level=self.level,
            format=self.format,
            log_dir=self.log_dir,
            file_enabled=self.file_enabled,
            use_daily_rotation=self.use_daily_rotation,
            max_bytes=self.max_bytes,
            backup_count=self.backup_count,
            retention_days=self.retention_days,
            console_enabled=self.console_enabled,
            console_colored=self.console_colored,
            json_indent=self.json_indent,
            include_extra_fields=self.include_extra_fields,
        )
