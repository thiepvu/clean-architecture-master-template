"""
File Management API Schemas (v1).

Presentation layer schemas for API request/response validation.
"""

from .file_requests import FileUploadMetadata, ShareFileRequest, UpdateFileRequest

__all__ = [
    "UpdateFileRequest",
    "ShareFileRequest",
    "FileUploadMetadata",
]
