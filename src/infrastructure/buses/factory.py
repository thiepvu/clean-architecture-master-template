"""
CQRS Bus Factory.

Creates CommandBus and QueryBus instances based on adapter type.
Currently supports in-memory implementation, extensible for distributed buses.
"""

from typing import TYPE_CHECKING, Optional

from config.types import BusAdapterType
from shared.application.ports.command_bus import ICommandBus
from shared.application.ports.query_bus import IQueryBus

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class CommandBusFactory:
    """Factory for creating CommandBus instances."""

    @staticmethod
    def create(
        adapter_type: BusAdapterType = BusAdapterType.IN_MEMORY,
        logger: Optional["ILogger"] = None,
    ) -> ICommandBus:
        """
        Create a CommandBus instance based on adapter type.

        Args:
            adapter_type: Type of bus adapter to use
            logger: Optional logger instance (injected via DI)

        Returns:
            ICommandBus implementation

        Raises:
            ValueError: If adapter type is not supported
        """
        if logger:
            logger.debug(f"Creating CommandBus with adapter: {adapter_type}")

        match adapter_type:
            case BusAdapterType.IN_MEMORY:
                from .adapters.in_memory import InMemoryCommandBus

                bus = InMemoryCommandBus(logger)
            case _:
                raise ValueError(f"Unsupported CommandBus adapter: {adapter_type}")

        if logger:
            logger.info(f"✓ CommandBus created: {adapter_type}")
        return bus


class QueryBusFactory:
    """Factory for creating QueryBus instances."""

    @staticmethod
    def create(
        adapter_type: BusAdapterType = BusAdapterType.IN_MEMORY,
        logger: Optional["ILogger"] = None,
    ) -> IQueryBus:
        """
        Create a QueryBus instance based on adapter type.

        Args:
            adapter_type: Type of bus adapter to use
            logger: Optional logger instance (injected via DI)

        Returns:
            IQueryBus implementation

        Raises:
            ValueError: If adapter type is not supported
        """
        if logger:
            logger.debug(f"Creating QueryBus with adapter: {adapter_type}")

        match adapter_type:
            case BusAdapterType.IN_MEMORY:
                from .adapters.in_memory import InMemoryQueryBus

                bus = InMemoryQueryBus(logger)
            case _:
                raise ValueError(f"Unsupported QueryBus adapter: {adapter_type}")

        if logger:
            logger.info(f"✓ QueryBus created: {adapter_type}")
        return bus
