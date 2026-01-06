"""
Get File By ID Query and Handler.

This query retrieves a single file by its ID.
"""

from uuid import UUID

from shared.application.base_query import Query, QueryHandler
from shared.domain.result import Result

from ...domain.errors.file_error_codes import FileErrorCode
from ..ports.file_read_repository import IFileReadRepository
from ..read_models import FileReadModel


class GetFileByIdQuery(Query):
    """
    Query to get a file by ID.

    Attributes:
        file_id: UUID of the file to retrieve
        user_id: User requesting the file (for access control)
    """

    file_id: UUID
    user_id: UUID


class GetFileByIdHandler(QueryHandler[GetFileByIdQuery, FileReadModel]):
    """
    Handler for GetFileByIdQuery.

    Uses the read repository to fetch file data efficiently.
    Validates user access before returning data.

    Note: This handler is read-only and does NOT use UnitOfWork.
    The read repository manages its own sessions.
    """

    def __init__(self, read_repository: IFileReadRepository):
        """Initialize handler."""
        self._read_repository = read_repository

    async def handle(self, query: GetFileByIdQuery) -> Result[FileReadModel]:
        """Handle the get file query."""
        # 1. Fetch file from read repository
        file = await self._read_repository.get_by_id(query.file_id)

        if file is None:
            return Result.fail(
                code=FileErrorCode.FILE_NOT_FOUND.value,
                message=f"File with ID {query.file_id} not found",
            )

        # 2. Check access permission
        can_access = await self._read_repository.can_access(query.file_id, query.user_id)
        if not can_access:
            return Result.fail(
                code=FileErrorCode.FILE_ACCESS_DENIED.value,
                message="You don't have permission to access this file",
            )

        return Result.ok(file)
