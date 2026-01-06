"""
Logging configuration - Port & Adapter pattern.

Contains:
- LoggingConfig: Common/Port config for all logging adapters
- StandardLoggerConfig: Standard Python logger adapter config
"""

from .logging import LoggingConfig
from .standard import StandardLoggerConfig

__all__ = [
    "LoggingConfig",
    "StandardLoggerConfig",
]
