"""
Logging configuration types - Port & Adapter pattern.

Contains:
- LoggingConfigType: Common/Port interface for all logging adapters
- StandardLoggerConfigType: Standard Python logger adapter config
"""

from typing import Literal, TypedDict

# =============================================================================
# Common/Port Type - Interface for all logging adapters
# =============================================================================


class LoggingConfigType(TypedDict):
    """
    Common logging configuration type (Port interface).

    All logging adapters must provide these base fields.
    """

    adapter: Literal["standard", "structlog"]
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    format: Literal["json", "text"]


# =============================================================================
# Adapter Types - Specific configuration for each adapter
# =============================================================================


class StandardLoggerConfigType(TypedDict):
    """
    Standard Python logger adapter configuration type.

    Contains all settings for Python's built-in logging.
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
