"""
In-Memory CQRS Bus Adapters.

Simple in-memory implementations of CommandBus and QueryBus.
Suitable for single-process applications.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from shared.application.base_command import Command
from shared.application.base_query import Query
from shared.application.ports.command_bus import ICommandBus
from shared.application.ports.query_bus import IQueryBus
from shared.domain.result import Result

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class InMemoryCommandBus(ICommandBus):
    """
    In-memory Command Bus implementation.

    Routes commands to their registered handlers.
    Ensures exactly one handler per command type (command → handler).
    """

    def __init__(self, logger: Optional["ILogger"] = None):
        """
        Initialize the command bus.

        Args:
            logger: Optional logger instance (injected via DI)
        """
        self._handlers: Dict[Type[Command], Any] = {}
        self._logger = logger

    def register(
        self,
        command_type: Type[Command],
        handler: Any,
    ) -> None:
        """
        Register a handler for a command type.

        Args:
            command_type: The command class
            handler: The handler instance

        Raises:
            ValueError: If handler already registered for this command
        """
        if command_type in self._handlers:
            raise ValueError(
                f"Handler already registered for {command_type.__name__}. "
                "Each command can only have one handler."
            )

        self._handlers[command_type] = handler
        if self._logger:
            self._logger.info(
                f"📝 CommandBus: Registered {handler.__class__.__name__} → {command_type.__name__}"
            )

    async def dispatch(self, command: Command) -> Result[Any]:
        """
        Dispatch a command to its handler.

        Args:
            command: The command to dispatch

        Returns:
            Result from the handler

        Raises:
            ValueError: If no handler registered for this command
        """
        command_type = type(command)
        handler = self._handlers.get(command_type)

        if handler is None:
            error_msg = f"No handler registered for {command_type.__name__}"
            if self._logger:
                self._logger.error(error_msg)
            raise ValueError(error_msg)

        handler_name = handler.__class__.__name__
        if self._logger:
            self._logger.info(f"🚀 CommandBus: {command_type.__name__} → {handler_name}")

        try:
            result = await handler.handle(command)
            if self._logger:
                status = "✅ success" if result.is_success else "❌ failure"
                self._logger.info(f"🏁 CommandBus: {command_type.__name__} {status}")
            return result
        except Exception as e:
            if self._logger:
                self._logger.error(
                    f"💥 CommandBus: {command_type.__name__} raised {e.__class__.__name__}: {e}"
                )
            raise

    def has_handler(self, command_type: Type[Command]) -> bool:
        """Check if a handler is registered for a command type."""
        return command_type in self._handlers

    @property
    def registered_commands(self) -> List[Type[Command]]:
        """List all registered command types."""
        return list(self._handlers.keys())


class InMemoryQueryBus(IQueryBus):
    """
    In-memory Query Bus implementation.

    Routes queries to their registered handlers.
    Ensures exactly one handler per query type (query → handler).

    Note: Query handlers should use read-optimized repositories
    or direct database queries for better performance.
    """

    def __init__(self, logger: Optional["ILogger"] = None):
        """
        Initialize the query bus.

        Args:
            logger: Optional logger instance (injected via DI)
        """
        self._handlers: Dict[Type[Query], Any] = {}
        self._logger = logger

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
        if query_type in self._handlers:
            raise ValueError(
                f"Handler already registered for {query_type.__name__}. "
                "Each query can only have one handler."
            )

        self._handlers[query_type] = handler
        if self._logger:
            self._logger.info(
                f"📖 QueryBus: Registered {handler.__class__.__name__} → {query_type.__name__}"
            )

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
        query_type = type(query)
        handler = self._handlers.get(query_type)

        if handler is None:
            error_msg = f"No handler registered for {query_type.__name__}"
            if self._logger:
                self._logger.error(error_msg)
            raise ValueError(error_msg)

        handler_name = handler.__class__.__name__
        if self._logger:
            self._logger.debug(f"🔍 QueryBus: {query_type.__name__} → {handler_name}")

        try:
            result = await handler.handle(query)
            if self._logger:
                status = "✅ found" if result.is_success else "❌ not found"
                self._logger.debug(f"🔍 QueryBus: {query_type.__name__} {status}")
            return result
        except Exception as e:
            if self._logger:
                self._logger.error(
                    f"💥 QueryBus: {query_type.__name__} raised {e.__class__.__name__}: {e}"
                )
            raise

    def has_handler(self, query_type: Type[Query]) -> bool:
        """Check if a handler is registered for a query type."""
        return query_type in self._handlers

    @property
    def registered_queries(self) -> List[Type[Query]]:
        """List all registered query types."""
        return list(self._handlers.keys())
