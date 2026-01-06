"""
AWS S3 Storage Adapter.

Stores files on AWS S3 or S3-compatible services (MinIO, etc.).
Suitable for production and distributed deployments.
"""

from .adapter import S3StorageAdapter

__all__ = ["S3StorageAdapter"]
