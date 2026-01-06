"""
Get File Download Query and Handler.

This query retrieves file download information.
"""

from uuid import UUID

from shared.application.base_query import Query, QueryHandler
from shared.domain.result import Result

from ...domain.errors.file_error_codes import FileErrorCode
from ..ports.file_read_repository import IFileReadRepository
from ..read_models import FileDownloadReadModel


class GetFileDownloadQuery(Query):
    """
    Query to get file download information.

    Attributes:
        file_id: UUID of the file to download
        user_id: User requesting the download (for access control)
    """

    file_id: UUID
    user_id: UUID


class GetFileDownloadHandler(QueryHandler[GetFileDownloadQuery, FileDownloadReadModel]):
    """
    Handler for GetFileDownloadQuery.

    Returns download information for serving a file.
    Validates user access before returning data.

    Note: This handler is read-only and does NOT use UnitOfWork.
    The read repository manages its own sessions.
    """

    def __init__(self, read_repository: IFileReadRepository):
        """Initialize handler."""
        self._read_repository = read_repository

    async def handle(self, query: GetFileDownloadQuery) -> Result[FileDownloadReadModel]:
        """Handle the get file download query."""
        # 1. Check if file exists
        exists = await self._read_repository.exists(query.file_id)
        if not exists:
            return Result.fail(
                code=FileErrorCode.FILE_NOT_FOUND.value,
                message=f"File with ID {query.file_id} not found",
            )

        # 2. Check access permission
        can_access = await self._read_repository.can_access(query.file_id, query.user_id)
        if not can_access:
            return Result.fail(
                code=FileErrorCode.FILE_ACCESS_DENIED.value,
                message="You don't have permission to download this file",
            )

        # 3. Get download info
        download_info = await self._read_repository.get_download_info(query.file_id)
        if download_info is None:
            return Result.fail(
                code=FileErrorCode.FILE_NOT_FOUND.value,
                message=f"File with ID {query.file_id} not found",
            )

        return Result.ok(download_info)
