"""
Domain events represent something important that happened in the domain.

Event Types:
─────────────
1. DomainEvent (base): Published directly to in-memory Event Bus
   - For side effects within same process (send email, log activity)
   - Immediate execution, no persistence
   - Example: SendWelcomeEmailHandler listens to UserCreatedEvent

2. OutboxEvent (marker): Saved to Outbox table, then published by OutboxProcessor
   - For cross-context integration and reliability
   - Persisted in same transaction as aggregate changes
   - Eventually consistent, guaranteed delivery
   - Example: File context listens to UserCreatedEvent for storage allocation

Usage:
──────
# Direct publish only (in-memory)
class UserLoggedInEvent(DomainEvent):
    pass

# Save to Outbox for reliable cross-context delivery
class UserCreatedEvent(DomainEvent, OutboxEvent):
    pass

# The UoW will:
# - Direct events → publish immediately to Event Bus
# - Outbox events → save to outbox table (OutboxProcessor publishes later)
"""

from abc import ABC
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4


class DomainEvent(ABC):
    """
    Base domain event.
    Domain events are immutable records of something that happened.

    By default, events are published directly to the in-memory Event Bus.
    For reliable cross-context delivery, also inherit from OutboxEvent.
    """

    def __init__(self):
        """Initialize domain event with ID and timestamp"""
        self.event_id: UUID = uuid4()
        self.occurred_at: datetime = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        Useful for serialization and logging.

        Returns:
            Dictionary representation of event
        """
        return {
            "event_id": str(self.event_id),
            "event_type": self.__class__.__name__,
            "occurred_at": self.occurred_at.isoformat(),
        }

    def __repr__(self) -> str:
        """String representation"""
        return f"<{self.__class__.__name__}(id={self.event_id})>"


class OutboxEvent:
    """
    Marker interface for events that should be saved to Outbox table.

    Events implementing this interface will be:
    1. Saved to outbox table in the same transaction as aggregate changes
    2. Published by OutboxProcessor (polling mechanism)
    3. Guaranteed delivery even if system crashes after commit

    Use this for:
    - Cross-context integration events
    - Events that trigger external systems (email, notifications)
    - Any event where you need guaranteed delivery

    Example:
        class UserCreatedEvent(DomainEvent, OutboxEvent):
            '''This event will be saved to outbox and published reliably.'''
            pass
    """

    pass
