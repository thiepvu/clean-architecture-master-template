"""
Storage Adapters.

Available adapters:
- LocalStorageAdapter: Local filesystem storage
- S3StorageAdapter: AWS S3 / S3-compatible storage
"""

from .local import LocalStorageAdapter
from .s3 import S3StorageAdapter

__all__ = [
    "LocalStorageAdapter",
    "S3StorageAdapter",
]
