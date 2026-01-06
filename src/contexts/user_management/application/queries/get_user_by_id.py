"""
Get User By ID Query and Handler.

This query retrieves a single user by their ID.
Supports optional caching with cache-aside pattern.
"""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from shared.application.base_query import Query, QueryHandler
from shared.domain.result import Result

from ...domain.errors.user_error_codes import UserErrorCode
from ..ports.user_read_repository import IUserReadRepository
from ..read_models import UserReadModel

if TYPE_CHECKING:
    from shared.application.ports import ICacheService


class GetUserByIdQuery(Query):
    """
    Query to get a user by ID.

    Attributes:
        user_id: UUID of the user to retrieve
    """

    user_id: UUID


class GetUserByIdHandler(QueryHandler[GetUserByIdQuery, UserReadModel]):
    """
    Handler for GetUserByIdQuery.

    Uses the read repository to fetch user data efficiently.
    Returns a read model (not domain entity).

    Cache-Aside Pattern:
    1. Check cache first
    2. If cache miss, query from database
    3. Store result in cache for future requests

    Note: This handler is read-only and does NOT use UnitOfWork.
    The read repository manages its own sessions.
    """

    # Cache key prefix for user lookups
    CACHE_KEY_PREFIX = "user:by_id:"
    # Cache TTL in seconds (5 minutes)
    CACHE_TTL = 300

    def __init__(
        self,
        read_repository: IUserReadRepository,
        cache_service: Optional["ICacheService"] = None,
    ):
        """
        Initialize handler.

        Args:
            read_repository: Read-optimized repository for user queries
            cache_service: Optional cache service for caching results
        """
        self._read_repository = read_repository
        self._cache_service = cache_service

    def _get_cache_key(self, user_id: UUID) -> str:
        """Generate cache key for user ID."""
        return f"{self.CACHE_KEY_PREFIX}{user_id}"

    async def handle(self, query: GetUserByIdQuery) -> Result[UserReadModel]:
        """
        Handle the get user query.

        Uses cache-aside pattern when cache service is available:
        1. Try to get from cache
        2. On cache miss, query database
        3. Store result in cache

        Args:
            query: GetUserByIdQuery with user ID

        Returns:
            Result containing UserReadModel on success, or error if not found
        """
        cache_key = self._get_cache_key(query.user_id)

        # Step 1: Try cache first (if available)
        if self._cache_service:
            cached_data = await self._cache_service.get(cache_key)
            if cached_data is not None:
                # Cache hit - reconstruct UserReadModel from cached dict
                user = UserReadModel.model_validate(cached_data)
                return Result.ok(user)

        # Step 2: Cache miss - query from database
        user_result = await self._read_repository.get_by_id(query.user_id)

        if user_result is None:
            return Result.fail(
                code=UserErrorCode.USER_NOT_FOUND.value,
                message=f"User with ID {query.user_id} not found",
            )

        # Step 3: Store in cache for future requests (if cache available)
        if self._cache_service:
            # Convert Pydantic model to dict for serialization
            await self._cache_service.set(
                key=cache_key,
                value=user_result.model_dump(mode="json"),
                ttl=self.CACHE_TTL,
            )

        return Result.ok(user_result)
