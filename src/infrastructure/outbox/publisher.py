"""
Outbox Event Publisher for converting outbox events to domain events.

This module handles the conversion of stored outbox events back to domain events
for publishing to the event bus.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Type
from uuid import UUID

from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import OutboxEvent
from shared.application.ports.event_bus import IEventBus
from shared.domain.events import DomainEvent

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class DomainEventFactory:
    """
    Factory for reconstructing domain events from outbox data.

    Maintains a registry of event types and their constructors.
    """

    _registry: Dict[str, Type[DomainEvent]] = {}
    _logger: Optional["ILogger"] = None

    @classmethod
    def set_logger(cls, logger: "ILogger") -> None:
        """Set logger for the factory (called during DI initialization)."""
        cls._logger = logger

    @classmethod
    def register(cls, event_type: str, event_class: Type[DomainEvent]) -> None:
        """
        Register an event type for reconstruction.

        Args:
            event_type: String name of the event type
            event_class: The event class to instantiate
        """
        cls._registry[event_type] = event_class
        if cls._logger:
            cls._logger.debug(f"Registered event type: {event_type}")

    @classmethod
    def register_many(cls, event_classes: list[Type[DomainEvent]]) -> None:
        """
        Register multiple event classes.

        Uses class name as the event type.

        Args:
            event_classes: List of event classes to register
        """
        for event_class in event_classes:
            cls.register(event_class.__name__, event_class)

    @classmethod
    def create(cls, event_type: str, payload: Dict[str, Any]) -> Optional[DomainEvent]:
        """
        Reconstruct a domain event from its type and payload.

        Args:
            event_type: String name of the event type
            payload: Dictionary of event data

        Returns:
            Reconstructed domain event, or None if type not registered
        """
        event_class = cls._registry.get(event_type)

        if not event_class:
            if cls._logger:
                cls._logger.warning(f"Unknown event type: {event_type}")
            return None

        try:
            # Try to create event using from_dict if available
            if hasattr(event_class, "from_dict"):
                return event_class.from_dict(payload)

            # Otherwise, try direct instantiation with payload as kwargs
            # Filter out base event fields that are set in __init__
            filtered_payload = {
                k: v
                for k, v in payload.items()
                if k not in ("event_id", "event_type", "occurred_at")
            }

            # Convert string UUIDs back to UUID objects
            for key, value in filtered_payload.items():
                if isinstance(value, str) and key.endswith("_id"):
                    try:
                        filtered_payload[key] = UUID(value)
                    except ValueError:
                        pass

            event = event_class.__new__(event_class)
            DomainEvent.__init__(event)

            # Restore event_id and occurred_at from payload if present
            if "event_id" in payload:
                event.event_id = UUID(payload["event_id"])
            if "occurred_at" in payload:
                event.occurred_at = datetime.fromisoformat(payload["occurred_at"])

            # Set other attributes
            for key, value in filtered_payload.items():
                setattr(event, key, value)

            return event

        except Exception as e:
            if cls._logger:
                cls._logger.error(f"Failed to reconstruct event {event_type}: {e}")
            return None

    @classmethod
    def get_registered_types(cls) -> list[str]:
        """Get list of all registered event types."""
        return list(cls._registry.keys())


class OutboxEventPublisher:
    """
    Publishes outbox events to the event bus.

    Handles event reconstruction and publishing with error handling.
    """

    def __init__(self, event_bus: IEventBus, logger: "ILogger"):
        """
        Initialize publisher.

        Args:
            event_bus: Event bus for publishing events
            logger: Logger instance (injected via DI)
        """
        self._event_bus = event_bus
        self._logger = logger

        # Set logger for DomainEventFactory (class-level)
        DomainEventFactory.set_logger(logger)

    async def publish(self, outbox_event: OutboxEvent) -> bool:
        """
        Publish a single outbox event.

        Args:
            outbox_event: The outbox event to publish

        Returns:
            True if successfully published

        Raises:
            Exception: If publishing fails
        """
        # Reconstruct domain event
        domain_event = DomainEventFactory.create(
            outbox_event.event_type,
            outbox_event.event_payload,
        )

        if domain_event is None:
            # Event type not registered - log and mark as failed
            raise ValueError(
                f"Cannot reconstruct event type: {outbox_event.event_type}. "
                f"Ensure the event class is registered with DomainEventFactory."
            )

        # Publish to event bus
        await self._event_bus.publish(domain_event)

        self._logger.debug(
            f"Published outbox event: {outbox_event.id} "
            f"({outbox_event.event_type}) for aggregate {outbox_event.aggregate_id}"
        )

        return True

    async def publish_many(self, outbox_events: list[OutboxEvent]) -> Dict[UUID, bool]:
        """
        Publish multiple outbox events.

        Args:
            outbox_events: List of outbox events to publish

        Returns:
            Dictionary mapping event ID to success status
        """
        results = {}

        for event in outbox_events:
            try:
                success = await self.publish(event)
                results[event.id] = success
            except Exception as e:
                self._logger.error(f"Failed to publish outbox event {event.id}: {e}")
                results[event.id] = False

        return results
