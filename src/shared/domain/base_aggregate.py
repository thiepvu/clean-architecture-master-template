"""
Base aggregate root class.
Aggregates are clusters of domain objects that can be treated as a single unit.
"""

from typing import List, Optional
from uuid import UUID

from .base_entity import BaseEntity
from .events import DomainEvent


class AggregateRoot(BaseEntity):
    """
    Base aggregate root with domain events.
    Aggregate roots are the only entities that can be directly accessed from outside.
    """

    def __init__(self, id: Optional[UUID] = None):
        """
        Initialize aggregate root.

        Args:
            id: Entity UUID (generated if not provided)
        """
        super().__init__(id)
        self._domain_events: List[DomainEvent] = []
        self._version: int = 0

    def add_domain_event(self, event: DomainEvent) -> None:
        """
        Add a domain event.
        Domain events represent something important that happened in the domain.

        Args:
            event: Domain event to add
        """
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all domain events after they've been processed"""
        self._domain_events.clear()

    @property
    def domain_events(self) -> List[DomainEvent]:
        """
        Get all domain events.
        Returns a copy to prevent external modification.
        """
        return self._domain_events.copy()

    @property
    def version(self) -> int:
        """
        Get aggregate version.
        Useful for optimistic concurrency control.
        """
        return self._version

    def increment_version(self) -> None:
        """Increment aggregate version"""
        self._version += 1
        self.update_timestamp()
