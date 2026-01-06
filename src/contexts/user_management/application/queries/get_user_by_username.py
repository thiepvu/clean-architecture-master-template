"""
Get User By Username Query and Handler.

This query retrieves a single user by their username.
"""

from shared.application.base_query import Query, QueryHandler
from shared.domain.result import Result

from ...domain.errors.user_error_codes import UserErrorCode
from ..ports.user_read_repository import IUserReadRepository
from ..read_models import UserReadModel


class GetUserByUsernameQuery(Query):
    """
    Query to get a user by username.

    Attributes:
        username: Username of the user to retrieve
    """

    username: str


class GetUserByUsernameHandler(QueryHandler[GetUserByUsernameQuery, UserReadModel]):
    """
    Handler for GetUserByUsernameQuery.

    Uses the read repository to fetch user data efficiently.
    Returns a read model (not domain entity).

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

    async def handle(self, query: GetUserByUsernameQuery) -> Result[UserReadModel]:
        """
        Handle the get user by username query.

        Args:
            query: GetUserByUsernameQuery with username

        Returns:
            Result containing UserReadModel on success, or error if not found
        """
        user = await self._read_repository.get_by_username(query.username)

        if user is None:
            return Result.fail(
                code=UserErrorCode.USER_NOT_FOUND.value,
                message=f"User with username {query.username} not found",
            )

        return Result.ok(user)
