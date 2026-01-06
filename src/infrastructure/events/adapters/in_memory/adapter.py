"""
In-Memory Event Bus Adapter.

Implements IEventBus for synchronous in-process event publishing.
Suitable for development, testing, and single-process applications.
"""

import asyncio
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Type

from shared.application.ports.event_bus import IEventBus, IEventHandler
from shared.domain.events import DomainEvent

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class InMemoryEventBusAdapter(IEventBus):
    """
    In-memory implementation of the Event Bus.

    Features:
    - Synchronous event dispatch within the same process
    - Multiple handlers per event type
    - Error isolation (one handler failure doesn't affect others)
    - Concurrent handler execution with asyncio.gather()

    For production with distributed systems, consider:
    - RabbitMQ (aio-pika)
    - Redis Pub/Sub
    - Kafka

    Example:
        event_bus = InMemoryEventBusAdapter(logger)
        await event_bus.initialize()

        event_bus.subscribe(UserCreatedEvent, UserCreatedEmailHandler())
        await event_bus.publish(UserCreatedEvent(user_id=..., email=...))
    """

    def __init__(self, logger: "ILogger"):
        """
        Initialize the event bus.

        Args:
            logger: Logger instance
        """
        self._logger = logger
        self._handlers: Dict[Type[DomainEvent], List[IEventHandler]] = defaultdict(list)
        self._published_count: int = 0
        self._error_count: int = 0
        self._initialized: bool = False

    async def initialize(self) -> None:
        """Initialize the event bus."""
        self._logger.info("🔧 Initializing in-memory event bus adapter")
        self._handlers.clear()
        self._published_count = 0
        self._error_count = 0
        self._initialized = True
        self._logger.info("✅ In-memory event bus adapter initialized")

    async def close(self) -> None:
        """Close the event bus."""
        self._handlers.clear()
        self._initialized = False
        self._logger.info("✅ In-memory event bus closed")

    async def health_check(self) -> bool:
        """Check if event bus is healthy."""
        return self._initialized

    @property
    def handler_count(self) -> int:
        """Get total number of registered handlers."""
        return sum(len(handlers) for handlers in self._handlers.values())

    @property
    def published_count(self) -> int:
        """Get total number of published events."""
        return self._published_count

    @property
    def error_count(self) -> int:
        """Get total number of handler errors."""
        return self._error_count

    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: IEventHandler,
    ) -> None:
        """Subscribe a handler to an event type."""
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            self._logger.info(
                f"📬 EventBus: Subscribed {handler.__class__.__name__} → {event_type.__name__}"
            )

    def unsubscribe(
        self,
        event_type: Type[DomainEvent],
        handler: IEventHandler,
    ) -> None:
        """Unsubscribe a handler from an event type."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            self._logger.debug(
                f"Unsubscribed {handler.__class__.__name__} from {event_type.__name__}"
            )

    async def publish(self, event: DomainEvent) -> None:
        """Publish a single domain event."""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        self._published_count += 1

        if not handlers:
            self._logger.debug(
                f"Event published (no handlers): {event_type.__name__} " f"[{event.event_id}]"
            )
            return

        self._logger.info(
            f"📤 EventBus: Publishing {event_type.__name__} "
            f"[{str(event.event_id)[:8]}] → {len(handlers)} handler(s)"
        )

        # Execute handlers concurrently
        tasks = [self._execute_handler(handler, event) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def publish_many(self, events: List[DomainEvent]) -> None:
        """Publish multiple domain events."""
        if not events:
            return

        self._logger.info(f"Publishing {len(events)} event(s)")

        for event in events:
            await self.publish(event)

    async def _execute_handler(
        self,
        handler: IEventHandler,
        event: DomainEvent,
    ) -> None:
        """Execute a single handler with error isolation."""
        handler_name = handler.__class__.__name__
        event_name = type(event).__name__

        try:
            await handler.handle(event)
            self._logger.info(f"✅ EventBus: {handler_name} handled {event_name}")
        except Exception as e:
            self._error_count += 1
            self._logger.error(
                f"Handler {handler_name} failed processing {event_name}: {e}",
                exc_info=True,
            )

    def get_handlers(self, event_type: Type[DomainEvent]) -> List[IEventHandler]:
        """Get all handlers for an event type."""
        return self._handlers.get(event_type, []).copy()

    def clear_handlers(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()
        self._logger.debug("All event handlers cleared")

    def reset_stats(self) -> None:
        """Reset published and error counts."""
        self._published_count = 0
        self._error_count = 0
