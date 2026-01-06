"""
Storage configuration - Port & Adapter pattern.

Contains:
- StorageConfig: Common/Port config for all storage adapters
- LocalStorageSettings: Local filesystem settings from environment
- LocalStorageConfig: Local filesystem adapter specific config
- S3StorageSettings: S3 settings from environment
- S3StorageConfig: AWS S3 adapter specific config
"""

from .local import LocalStorageConfig, LocalStorageSettings
from .s3 import S3StorageConfig, S3StorageSettings
from .storage import StorageConfig

__all__ = [
    "StorageConfig",
    "LocalStorageSettings",
    "LocalStorageConfig",
    "S3StorageSettings",
    "S3StorageConfig",
]
