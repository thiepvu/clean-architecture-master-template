"""
List Users Query and Handler.

This query retrieves a paginated list of users.
"""

from typing import Optional

from shared.application.base_query import Query, QueryHandler
from shared.domain.result import Result

from ..ports.user_read_repository import IUserReadRepository
from ..read_models import PaginatedUsersReadModel


class ListUsersQuery(Query):
    """
    Query to list users with pagination and filtering.

    Attributes:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
        is_active: Filter by active status (optional)
    """

    skip: int = 0
    limit: int = 100
    is_active: Optional[bool] = None


class ListUsersHandler(QueryHandler[ListUsersQuery, PaginatedUsersReadModel]):
    """
    Handler for ListUsersQuery.

    Uses the read repository to fetch users efficiently.
    Returns paginated read models with metadata.

    Note: This handler is read-only and does NOT use UnitOfWork.
    The read repository manages its own sessions.
    """

    def __init__(self, read_repository: IUserReadRepository):
        """
        Initialize handler.

        Args:
            read_repository: Read-optimized repository for user queries
        """
        self._read_repository = read_repository

    async def handle(self, query: ListUsersQuery) -> Result[PaginatedUsersReadModel]:
        """
        Handle the list users query.

        Args:
            query: ListUsersQuery with pagination and filter options

        Returns:
            Result containing PaginatedUsersReadModel with users and metadata
        """
        # Read repository manages its own session
        users = await self._read_repository.list_users(
            skip=query.skip,
            limit=query.limit,
            is_active=query.is_active,
        )

        total = await self._read_repository.count(is_active=query.is_active)

        result = PaginatedUsersReadModel.create(
            users=users,
            total=total,
            skip=query.skip,
            limit=query.limit,
        )

        return Result.ok(result)
