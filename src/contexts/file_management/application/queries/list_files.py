"""
List Files Query and Handler.

This query retrieves a paginated list of files.
"""

from typing import Optional
from uuid import UUID

from shared.application.base_query import Query, QueryHandler
from shared.domain.result import Result

from ..ports.file_read_repository import IFileReadRepository
from ..read_models import PaginatedFilesReadModel


class ListFilesQuery(Query):
    """
    Query to list files with pagination and filtering.

    Attributes:
        user_id: User requesting the list (for access control)
        skip: Number of records to skip
        limit: Maximum number of records to return
        owner_only: If True, only return files owned by user
        public_only: If True, only return public files
    """

    user_id: UUID
    skip: int = 0
    limit: int = 100
    owner_only: bool = False
    public_only: bool = False


class ListFilesHandler(QueryHandler[ListFilesQuery, PaginatedFilesReadModel]):
    """
    Handler for ListFilesQuery.

    Returns paginated file listings based on filters and access control.

    Note: This handler is read-only and does NOT use UnitOfWork.
    The read repository manages its own sessions.
    """

    def __init__(self, read_repository: IFileReadRepository):
        """Initialize handler."""
        self._read_repository = read_repository

    async def handle(self, query: ListFilesQuery) -> Result[PaginatedFilesReadModel]:
        """Handle the list files query."""
        owner_id: Optional[UUID] = None
        is_public: Optional[bool] = None
        accessible_by: Optional[UUID] = None

        if query.owner_only:
            # Only files owned by user
            owner_id = query.user_id
        elif query.public_only:
            # Only public files
            is_public = True
        else:
            # Files accessible by user (owned, public, or shared)
            accessible_by = query.user_id

        # Read repository manages its own session
        files = await self._read_repository.list_files(
            skip=query.skip,
            limit=query.limit,
            owner_id=owner_id,
            is_public=is_public,
            accessible_by=accessible_by,
        )

        total = await self._read_repository.count(
            owner_id=owner_id,
            is_public=is_public,
            accessible_by=accessible_by,
        )

        return Result.ok(
            PaginatedFilesReadModel(
                files=files,
                total=total,
                skip=query.skip,
                limit=query.limit,
            )
        )
