"""
Event Bus Factory.

Creates event bus adapters based on configuration.
Supports: In-Memory (RabbitMQ, Kafka planned for future)
"""

from typing import TYPE_CHECKING

from config.types import EventBusAdapterType
from shared.application.ports import IEventBus

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class EventBusFactory:
    """
    Factory for creating event bus adapters.

    Creates and initializes the appropriate event bus adapter
    based on configuration. Performs health check before returning.

    Example:
        event_bus = await EventBusFactory.create(
            adapter_type=EventBusAdapterType.IN_MEMORY,
            logger=logger,
        )
    """

    @staticmethod
    async def create(
        adapter_type: EventBusAdapterType,
        logger: "ILogger",
    ) -> IEventBus:
        """
        Create and initialize event bus adapter.

        Args:
            adapter_type: Type of event bus adapter to create
            logger: Logger instance

        Returns:
            Initialized event bus adapter

        Raises:
            ValueError: If adapter type is unknown
            RuntimeError: If health check fails
        """
        logger.info(f"🔧 Creating event bus adapter: {adapter_type.value}")

        if adapter_type == EventBusAdapterType.IN_MEMORY:
            from .adapters.in_memory import InMemoryEventBusAdapter

            adapter = InMemoryEventBusAdapter(logger)

        # Future adapters:
        # elif adapter_type == EventBusAdapterType.RABBITMQ:
        #     from .adapters.rabbitmq import RabbitMQEventBusAdapter
        #     adapter = RabbitMQEventBusAdapter(config, logger)

        else:
            raise ValueError(f"Unknown event bus adapter type: {adapter_type}")

        # Initialize adapter
        await adapter.initialize()

        # Verify health
        if not await adapter.health_check():
            raise RuntimeError(f"Event bus adapter health check failed: {adapter_type.value}")

        logger.info(f"✅ Event bus adapter ready: {adapter_type.value}")
        return adapter
