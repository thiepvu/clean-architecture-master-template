"""
Query Bus Port (Interface).

Defines the contract for query bus implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Type

from shared.application.base_query import Query
from shared.domain.result import Result


class IQueryBus(ABC):
    """
    Query Bus interface.

    Responsible for:
    - Registering query handlers
    - Dispatching queries to appropriate handlers
    - Ensuring one handler per query type

    Note: Unlike commands, queries should NEVER modify state.
    They only read data and return results.

    Example:
        class GetUserQuery(Query):
            user_id: UUID

        class GetUserHandler(QueryHandler[GetUserQuery, UserReadModel]):
            async def handle(self, query: GetUserQuery) -> Result[UserReadModel]:
                ...

        # Usage
        bus = QueryBusFactory.create(adapter_type)
        bus.register(GetUserQuery, GetUserHandler(read_repo))

        result = await bus.dispatch(GetUserQuery(user_id=uuid))
    """

    @abstractmethod
    def register(
        self,
        query_type: Type[Query],
        handler: Any,
    ) -> None:
        """
        Register a handler for a query type.

        Args:
            query_type: The query class
            handler: The handler instance

        Raises:
            ValueError: If handler already registered for this query
        """
        ...

    @abstractmethod
    async def dispatch(self, query: Query) -> Result[Any]:
        """
        Dispatch a query to its handler.

        Args:
            query: The query to dispatch

        Returns:
            Result from the handler

        Raises:
            ValueError: If no handler registered for this query
        """
        ...

    @abstractmethod
    def has_handler(self, query_type: Type[Query]) -> bool:
        """Check if a handler is registered for a query type."""
        ...

    @property
    @abstractmethod
    def registered_queries(self) -> List[Type[Query]]:
        """List all registered query types."""
        ...
