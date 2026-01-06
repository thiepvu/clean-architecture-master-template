"""
Get User By Email Query and Handler.

This query retrieves a single user by their email address.
"""

from shared.application.base_query import Query, QueryHandler
from shared.domain.result import Result

from ...domain.errors.user_error_codes import UserErrorCode
from ..ports.user_read_repository import IUserReadRepository
from ..read_models import UserReadModel


class GetUserByEmailQuery(Query):
    """
    Query to get a user by email.

    Attributes:
        email: Email address of the user to retrieve
    """

    email: str


class GetUserByEmailHandler(QueryHandler[GetUserByEmailQuery, UserReadModel]):
    """
    Handler for GetUserByEmailQuery.

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

    async def handle(self, query: GetUserByEmailQuery) -> Result[UserReadModel]:
        """
        Handle the get user by email query.

        Args:
            query: GetUserByEmailQuery with email

        Returns:
            Result containing UserReadModel on success, or error if not found
        """
        user = await self._read_repository.get_by_email(query.email)

        if user is None:
            return Result.fail(
                code=UserErrorCode.USER_NOT_FOUND.value,
                message=f"User with email {query.email} not found",
            )

        return Result.ok(user)
