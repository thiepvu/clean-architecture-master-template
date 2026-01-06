"""Event Bus interface (Outbound Port)"""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Type

from shared.domain.events import DomainEvent


class IEventHandler(ABC):
    """
    Base event handler interface.
    Implement this to handle specific domain events.
    """

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """
        Handle the domain event.

        Args:
            event: Domain event to handle
        """
        pass


class IEventBus(ABC):
    """
    Event Bus interface for publishing and subscribing to domain events.

    Supports both:
    - In-memory event dispatch (within bounded context)
    - Integration events via message broker (cross bounded context)

    Example:
        # Publishing events after commit
        async with uow:
            order = Order.create(...)
            await uow.orders.add(order)
            await uow.commit()

        # Events are collected from aggregates and published
        for event in order.domain_events:
            await event_bus.publish(event)
        order.clear_domain_events()
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a single domain event.

        Args:
            event: Domain event to publish
        """
        pass

    @abstractmethod
    async def publish_many(self, events: List[DomainEvent]) -> None:
        """
        Publish multiple domain events.

        Args:
            events: List of domain events to publish
        """
        pass

    @abstractmethod
    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: IEventHandler,
    ) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Handler to invoke when event is published
        """
        pass

    @abstractmethod
    def unsubscribe(
        self,
        event_type: Type[DomainEvent],
        handler: IEventHandler,
    ) -> None:
        """
        Unsubscribe a handler from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if event bus is healthy.

        Returns:
            True if healthy, False otherwise
        """
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the event bus.

        Called during application startup.
        Should establish connections if needed.
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close the event bus.

        Called during application shutdown.
        Should cleanup connections and resources.
        """
        pass
