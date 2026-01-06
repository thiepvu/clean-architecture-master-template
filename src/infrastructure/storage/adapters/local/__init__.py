"""
Local Filesystem Storage Adapter.

Stores files on the local filesystem.
Suitable for development and single-server deployments.
"""

from .adapter import LocalStorageAdapter

__all__ = ["LocalStorageAdapter"]
