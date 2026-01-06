"""
Events Infrastructure Module.

Provides event bus capabilities with Port & Adapter + Factory pattern.

Adapters:
- In-Memory: Single-process event dispatch (development/testing)
- RabbitMQ: Distributed event bus (planned)
- Kafka: High-throughput event streaming (planned)

Usage:
──────
1. DI Container Registration (Recommended):
    from infrastructure.events import EventsModule

    event_bus = providers.Singleton(
        EventsModule.create_event_bus,
        config_service=config_service,
        logger=logger,
    )

2. Direct Factory Usage:
    from infrastructure.events import EventBusFactory
    from config.types import EventBusAdapterType

    event_bus = await EventBusFactory.create(
        adapter_type=EventBusAdapterType.IN_MEMORY,
        logger=logger,
    )

    event_bus.subscribe(UserCreatedEvent, UserCreatedHandler())
    await event_bus.publish(UserCreatedEvent(...))
"""

from .adapters import InMemoryEventBusAdapter
from .events_module import EventsModule
from .factory import EventBusFactory

# Backwards compatibility alias
InMemoryEventBus = InMemoryEventBusAdapter

__all__ = [
    # Module (primary interface for DI)
    "EventsModule",
    # Factory
    "EventBusFactory",
    # Adapters
    "InMemoryEventBusAdapter",
    "InMemoryEventBus",  # Backwards compatibility
]
