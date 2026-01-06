"""
Query pattern implementation for CQRS.

Queries represent requests to read data (Read operations).
Queries should NEVER modify state.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from shared.domain.result import Result

TResult = TypeVar("TResult")
TQuery = TypeVar("TQuery", bound="Query")


class Query(BaseModel, ABC):
    """
    Base query class.

    Queries are immutable requests for data. They should:
    - Be named as questions or data requests (GetUser, ListOrders, FindFilesByOwner)
    - Contain criteria for filtering/selecting data
    - Be immutable (frozen)
    - NEVER modify state
    - Have exactly one handler

    Example:
        class GetUserByIdQuery(Query):
            user_id: UUID

        class ListUsersQuery(Query):
            skip: int = 0
            limit: int = 100
            is_active: Optional[bool] = None

        class SearchUsersQuery(Query):
            search_term: str
            skip: int = 0
            limit: int = 50
    """

    class Config:
        frozen = True  # Make query immutable
        extra = "forbid"  # Don't allow extra fields


class QueryHandler(ABC, Generic[TQuery, TResult]):
    """
    Base query handler.

    Handles the execution of a specific query type and returns a Result.
    Query handlers:
    - Process exactly one query type
    - NEVER modify state (read-only)
    - Use read-optimized repositories or direct database queries
    - Return Read Models (DTOs optimized for display)
    - May use caching for performance

    Example:
        class GetUserByIdHandler(QueryHandler[GetUserByIdQuery, UserReadModel]):
            def __init__(self, read_repository: IUserReadRepository):
                self._read_repo = read_repository

            async def handle(self, query: GetUserByIdQuery) -> Result[UserReadModel]:
                user = await self._read_repo.get_by_id(query.user_id)
                if user is None:
                    return Result.fail("USER_NOT_FOUND", "User not found")
                return Result.ok(user)
    """

    @abstractmethod
    async def handle(self, query: TQuery) -> Result[TResult]:
        """
        Handle query execution.

        Args:
            query: Query to execute

        Returns:
            Result containing success value or error
        """
        pass
