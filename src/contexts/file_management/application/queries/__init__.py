"""
File Management Queries and Query Handlers.

Queries represent read operations that don't change state.
Each query has exactly one handler.
"""

from .get_file_by_id import GetFileByIdHandler, GetFileByIdQuery
from .get_file_download import GetFileDownloadHandler, GetFileDownloadQuery
from .list_files import ListFilesHandler, ListFilesQuery

__all__ = [
    # Queries
    "GetFileByIdQuery",
    "ListFilesQuery",
    "GetFileDownloadQuery",
    # Handlers
    "GetFileByIdHandler",
    "ListFilesHandler",
    "GetFileDownloadHandler",
]
