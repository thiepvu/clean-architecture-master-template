"""
Integration Events for cross-bounded-context communication.

Integration Events are different from Domain Events:
- Domain Events: Internal to a BC, part of domain language
- Integration Events: Published contract between BCs, part of "published language"

Integration Events MUST use Outbox Pattern for reliable delivery.
"""

from abc import ABC
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from shared.domain.events import DomainEvent


class IntegrationEvent(ABC):
    """
    Base class for Integration Events.

    Integration events are used for:
    - Cross-BC communication
    - External system integration
    - Any scenario requiring guaranteed delivery

    Key differences from DomainEvent:
    - Always uses Outbox Pattern
    - Has schema versioning for backward compatibility
    - Contains metadata for tracing
    - Designed for serialization across process boundaries
    """

    # Schema version for backward compatibility
    VERSION: str = "1.0"

    def __init__(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        correlation_id: Optional[UUID] = None,
        causation_id: Optional[UUID] = None,
    ):
        """
        Initialize integration event.

        Args:
            aggregate_id: ID of the aggregate that generated this event
            aggregate_type: Type name of the aggregate
            correlation_id: ID linking related events in a workflow
            causation_id: ID of the event that caused this event
        """
        self.event_id: UUID = uuid4()
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type
        self.occurred_at: datetime = datetime.utcnow()
        self.correlation_id = correlation_id or uuid4()
        self.causation_id = causation_id
        self.version = self.VERSION

    @property
    def event_type(self) -> str:
        """Get the event type name."""
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize event to dictionary for storage/transport.

        Returns:
            Dictionary representation with all metadata
        """
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "version": self.version,
            "aggregate_id": str(self.aggregate_id),
            "aggregate_type": self.aggregate_type,
            "occurred_at": self.occurred_at.isoformat(),
            "correlation_id": str(self.correlation_id),
            "causation_id": str(self.causation_id) if self.causation_id else None,
            "payload": self._get_payload(),
        }

    def _get_payload(self) -> Dict[str, Any]:
        """
        Get event-specific payload.

        Override in subclasses to include event data.
        """
        # Default: include all non-private, non-metadata attributes
        metadata_fields = {
            "event_id",
            "event_type",
            "version",
            "aggregate_id",
            "aggregate_type",
            "occurred_at",
            "correlation_id",
            "causation_id",
        }
        return {
            k: self._serialize_value(v)
            for k, v in vars(self).items()
            if not k.startswith("_") and k not in metadata_fields
        }

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value for JSON."""
        if isinstance(value, UUID):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif hasattr(value, "to_dict"):
            return value.to_dict()
        elif hasattr(value, "value"):  # Value objects
            return self._serialize_value(value.value)
        return value

    @classmethod
    def from_domain_event(
        cls,
        domain_event: DomainEvent,
        aggregate_id: UUID,
        aggregate_type: str,
        **extra_fields,
    ) -> "IntegrationEvent":
        """
        Create integration event from a domain event.

        This factory method helps translate domain events to integration events
        at the boundary of a bounded context.

        Args:
            domain_event: The source domain event
            aggregate_id: ID of the aggregate
            aggregate_type: Type of the aggregate
            **extra_fields: Additional fields for the integration event

        Returns:
            New integration event instance
        """
        instance = cls.__new__(cls)
        IntegrationEvent.__init__(
            instance,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            causation_id=domain_event.event_id,
        )

        # Copy relevant fields from domain event
        for key, value in vars(domain_event).items():
            if not key.startswith("_") and key not in ("event_id", "occurred_at"):
                setattr(instance, key, value)

        # Apply extra fields
        for key, value in extra_fields.items():
            setattr(instance, key, value)

        return instance

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.event_id}, "
            f"aggregate={self.aggregate_type}:{self.aggregate_id}"
            f")>"
        )


# =============================================================================
# Common Integration Event Patterns
# =============================================================================


class EntityCreatedIntegrationEvent(IntegrationEvent):
    """Base for entity creation events."""

    pass


class EntityUpdatedIntegrationEvent(IntegrationEvent):
    """Base for entity update events."""

    def __init__(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        changes: Dict[str, Any],
        **kwargs,
    ):
        super().__init__(aggregate_id, aggregate_type, **kwargs)
        self.changes = changes


class EntityDeletedIntegrationEvent(IntegrationEvent):
    """Base for entity deletion events."""

    pass


class StateChangedIntegrationEvent(IntegrationEvent):
    """Base for state transition events."""

    def __init__(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        from_state: str,
        to_state: str,
        **kwargs,
    ):
        super().__init__(aggregate_id, aggregate_type, **kwargs)
        self.from_state = from_state
        self.to_state = to_state
