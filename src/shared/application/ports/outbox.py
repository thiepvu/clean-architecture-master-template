"""
Outbox Pattern Ports (Interfaces).

These interfaces define the contract for outbox pattern implementations.
Outbox pattern ensures reliable event delivery by storing events in the same
transaction as aggregate changes, then publishing them asynchronously.

Components:
- IOutboxEvent: Interface for outbox event entity
- IOutboxRepository: Repository for outbox CRUD operations
- IOutboxProcessor: Background processor for publishing events
- IOutboxEventPublisher: Publishes outbox events to event bus
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from uuid import UUID


class OutboxEventStatus(str, Enum):
    """Status of an outbox event."""

    PENDING = "pending"  # Not yet published
    PUBLISHED = "published"  # Successfully published
    FAILED = "failed"  # Failed after max retries (dead letter)


@runtime_checkable
class IOutboxEvent(Protocol):
    """
    Interface for outbox events.

    Outbox events store domain events for reliable async publishing.
    """

    @property
    def id(self) -> UUID:
        """Get the event ID."""
        ...

    @property
    def aggregate_id(self) -> UUID:
        """Get the aggregate ID that generated this event."""
        ...

    @property
    def aggregate_type(self) -> str:
        """Get the aggregate type name."""
        ...

    @property
    def event_type(self) -> str:
        """Get the event type name."""
        ...

    @property
    def event_payload(self) -> Dict[str, Any]:
        """Get the serialized event data."""
        ...

    @property
    def status(self) -> OutboxEventStatus:
        """Get the current status."""
        ...

    @property
    def retry_count(self) -> int:
        """Get the number of retry attempts."""
        ...

    @property
    def max_retries(self) -> int:
        """Get the maximum retry attempts."""
        ...

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        ...

    @property
    def scheduled_at(self) -> datetime:
        """Get the next scheduled publish time."""
        ...

    def mark_as_published(self) -> None:
        """Mark the event as successfully published."""
        ...

    def mark_as_failed(self, error: str) -> None:
        """Mark the event as permanently failed."""
        ...

    def increment_retry(self, error: str, backoff_seconds: int = 60) -> None:
        """Increment retry count with exponential backoff."""
        ...


class IOutboxRepository(ABC):
    """
    Interface for outbox repository operations.

    Provides CRUD operations for outbox events.
    """

    @abstractmethod
    async def save(self, event: IOutboxEvent) -> IOutboxEvent:
        """
        Save an outbox event.

        Args:
            event: The outbox event to save

        Returns:
            The saved event
        """
        pass

    @abstractmethod
    async def save_many(self, events: List[IOutboxEvent]) -> List[IOutboxEvent]:
        """
        Save multiple outbox events in a batch.

        Args:
            events: List of outbox events to save

        Returns:
            List of saved events
        """
        pass

    @abstractmethod
    async def get_unpublished(
        self,
        limit: int = 100,
        before: Optional[datetime] = None,
    ) -> List[IOutboxEvent]:
        """
        Get unpublished events ready for processing.

        Args:
            limit: Maximum number of events to fetch
            before: Only fetch events scheduled before this time

        Returns:
            List of unpublished events
        """
        pass

    @abstractmethod
    async def mark_as_published(self, event_id: UUID) -> bool:
        """
        Mark an event as successfully published.

        Args:
            event_id: ID of the event to mark

        Returns:
            True if event was found and updated
        """
        pass

    @abstractmethod
    async def mark_as_failed(self, event_id: UUID, error: str) -> bool:
        """
        Mark an event as permanently failed.

        Args:
            event_id: ID of the event to mark
            error: Error message

        Returns:
            True if event was found and updated
        """
        pass

    @abstractmethod
    async def increment_retry(
        self,
        event_id: UUID,
        error: str,
        next_scheduled_at: datetime,
    ) -> bool:
        """
        Increment retry count and schedule next attempt.

        Args:
            event_id: ID of the event
            error: Error message from failed attempt
            next_scheduled_at: When to next attempt publishing

        Returns:
            True if event was found and updated
        """
        pass

    @abstractmethod
    async def cleanup_published(self, older_than: timedelta) -> int:
        """
        Delete published events older than specified duration.

        Args:
            older_than: Delete events older than this duration

        Returns:
            Number of events deleted
        """
        pass

    @abstractmethod
    async def get_failed_events(self, limit: int = 100) -> List[IOutboxEvent]:
        """
        Get events that have permanently failed (dead letter queue).

        Args:
            limit: Maximum number of events to fetch

        Returns:
            List of failed events
        """
        pass

    @abstractmethod
    async def retry_failed_event(self, event_id: UUID) -> bool:
        """
        Reset a failed event to pending for retry.

        Args:
            event_id: ID of the event to retry

        Returns:
            True if event was found and reset
        """
        pass


class IOutboxProcessor(ABC):
    """
    Interface for outbox event processing.

    Responsible for polling and publishing outbox events.
    """

    @abstractmethod
    async def start(self) -> None:
        """Start the background processor."""
        pass

    @abstractmethod
    async def stop(self, timeout: float = 10.0) -> None:
        """
        Stop the background processor gracefully.

        Args:
            timeout: Maximum seconds to wait for shutdown
        """
        pass

    @abstractmethod
    async def process_batch(self) -> int:
        """
        Process a batch of pending events.

        Returns:
            Number of events processed
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """Get processor statistics."""
        pass


class IOutboxEventPublisher(ABC):
    """Interface for publishing outbox events to the event bus."""

    @abstractmethod
    async def publish(self, event: IOutboxEvent) -> bool:
        """
        Publish a single outbox event.

        Args:
            event: The outbox event to publish

        Returns:
            True if successfully published
        """
        pass

    @abstractmethod
    async def publish_many(self, events: List[IOutboxEvent]) -> Dict[UUID, bool]:
        """
        Publish multiple outbox events.

        Args:
            events: List of outbox events to publish

        Returns:
            Dictionary mapping event ID to success status
        """
        pass
