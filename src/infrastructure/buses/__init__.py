"""
CQRS Buses Infrastructure Module.

Provides Command Bus and Query Bus implementations with Port & Adapter + Factory pattern.

Adapters:
- In-Memory: Single-process, synchronous dispatch

Usage:
──────
1. DI Container Registration (Recommended):
    from infrastructure.buses import BusesModule

    command_bus = providers.Singleton(
        BusesModule.create_command_bus,
        config_service=config_service,
        logger=logger,
    )

2. Direct Factory Usage:
    from infrastructure.buses import CommandBusFactory
    from config.types import BusAdapterType

    command_bus = CommandBusFactory.create(BusAdapterType.IN_MEMORY, logger)
"""

from .adapters import InMemoryCommandBus, InMemoryQueryBus
from .buses_module import BusesModule
from .factory import CommandBusFactory, QueryBusFactory

__all__ = [
    # Module (primary interface for DI)
    "BusesModule",
    # Factory
    "CommandBusFactory",
    "QueryBusFactory",
    # Adapters
    "InMemoryCommandBus",
    "InMemoryQueryBus",
]
