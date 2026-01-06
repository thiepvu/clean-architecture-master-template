"""
Outbox Event Models for SQLAlchemy.

This module provides:
- OutboxEventModel: SQLAlchemy ORM model for database persistence
- OutboxEvent: Domain model for application layer
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import Base
from shared.application.ports import OutboxEventStatus

# Create SQLAlchemy ENUM type for PostgreSQL
outbox_status_enum = ENUM(
    "pending",
    "published",
    "failed",
    name="outboxeventstatus",
    create_type=False,  # Type is created via migration
)


class OutboxEventModel(Base):
    """
    SQLAlchemy model for outbox events.

    This table stores events that need to be published to the event bus.
    Events are written in the same transaction as aggregate changes.

    Columns:
        - id: Unique event ID
        - aggregate_id: ID of the aggregate that generated this event
        - aggregate_type: Type of aggregate (e.g., "User", "File")
        - event_type: Type of event (e.g., "UserCreatedEvent")
        - event_payload: JSON serialized event data
        - status: Current status (pending, published, failed)
        - retry_count: Number of publish attempts
        - max_retries: Maximum retry attempts before marking as failed
        - created_at: When the event was created
        - published_at: When the event was successfully published
        - last_error: Last error message if failed
        - scheduled_at: When to next attempt publishing (for retry backoff)
    """

    __tablename__ = "outbox_events"

    # Primary key
    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        comment="Unique event ID",
    )

    # Aggregate information
    aggregate_id = Column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID of the aggregate that generated this event",
    )
    aggregate_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of aggregate (e.g., User, File)",
    )

    # Event information
    event_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of event (e.g., UserCreatedEvent)",
    )
    event_payload = Column(
        JSONB,
        nullable=False,
        comment="JSON serialized event data",
    )

    # Processing status
    status = Column(
        outbox_status_enum,
        nullable=False,
        default=OutboxEventStatus.PENDING.value,
        index=True,
        comment="Current processing status",
    )
    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of publish attempts",
    )
    max_retries = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Maximum retry attempts",
    )

    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When the event was created",
    )
    published_at = Column(
        DateTime,
        nullable=True,
        comment="When the event was successfully published",
    )
    scheduled_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="When to next attempt publishing",
    )

    # Error tracking
    last_error = Column(
        Text,
        nullable=True,
        comment="Last error message if failed",
    )

    def __repr__(self) -> str:
        return f"<OutboxEventModel(id={self.id}, type={self.event_type}, status={self.status})>"


class OutboxEvent:
    """
    Domain model for outbox events.

    This is the domain representation used in application code.
    It's separate from the SQLAlchemy model for clean architecture.
    Implements IOutboxEvent protocol.
    """

    def __init__(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        event_type: str,
        event_payload: Dict[str, Any],
        id: Optional[UUID] = None,
        status: OutboxEventStatus = OutboxEventStatus.PENDING,
        retry_count: int = 0,
        max_retries: int = 5,
        created_at: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
        scheduled_at: Optional[datetime] = None,
        last_error: Optional[str] = None,
    ):
        self._id = id or uuid4()
        self._aggregate_id = aggregate_id
        self._aggregate_type = aggregate_type
        self._event_type = event_type
        self._event_payload = event_payload
        self._status = status
        self._retry_count = retry_count
        self._max_retries = max_retries
        self._created_at = created_at or datetime.utcnow()
        self._published_at = published_at
        self._scheduled_at = scheduled_at or datetime.utcnow()
        self._last_error = last_error

    # Properties for IOutboxEvent protocol
    @property
    def id(self) -> UUID:
        return self._id

    @property
    def aggregate_id(self) -> UUID:
        return self._aggregate_id

    @property
    def aggregate_type(self) -> str:
        return self._aggregate_type

    @property
    def event_type(self) -> str:
        return self._event_type

    @property
    def event_payload(self) -> Dict[str, Any]:
        return self._event_payload

    @property
    def status(self) -> OutboxEventStatus:
        return self._status

    @property
    def retry_count(self) -> int:
        return self._retry_count

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def published_at(self) -> Optional[datetime]:
        return self._published_at

    @property
    def scheduled_at(self) -> datetime:
        return self._scheduled_at

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    @classmethod
    def from_domain_event(
        cls,
        domain_event: Any,
        aggregate_id: UUID,
        aggregate_type: str,
    ) -> "OutboxEvent":
        """
        Create an OutboxEvent from a domain event.

        Args:
            domain_event: The domain event to wrap
            aggregate_id: ID of the aggregate that generated the event
            aggregate_type: Type name of the aggregate

        Returns:
            OutboxEvent ready to be persisted
        """
        # Get event payload from to_dict() method or convert manually
        if hasattr(domain_event, "to_dict"):
            payload = domain_event.to_dict()
        else:
            # Fallback: serialize public attributes
            payload = {
                k: str(v) if isinstance(v, (UUID, datetime)) else v
                for k, v in vars(domain_event).items()
                if not k.startswith("_")
            }

        return cls(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            event_type=domain_event.__class__.__name__,
            event_payload=payload,
        )

    def mark_as_published(self) -> None:
        """Mark the event as successfully published."""
        self._status = OutboxEventStatus.PUBLISHED
        self._published_at = datetime.utcnow()

    def mark_as_failed(self, error: str) -> None:
        """Mark the event as permanently failed."""
        self._status = OutboxEventStatus.FAILED
        self._last_error = error

    def increment_retry(self, error: str, backoff_seconds: int = 60) -> None:
        """
        Increment retry count and schedule next attempt.

        Uses exponential backoff: delay = backoff_seconds * 2^retry_count

        Args:
            error: The error message from the failed attempt
            backoff_seconds: Base delay in seconds (default 60)
        """
        self._retry_count += 1
        self._last_error = error

        if self._retry_count >= self._max_retries:
            self.mark_as_failed(f"Max retries exceeded. Last error: {error}")
        else:
            # Exponential backoff
            delay = backoff_seconds * (2**self._retry_count)
            self._scheduled_at = datetime.utcnow() + timedelta(seconds=delay)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self._id),
            "aggregate_id": str(self._aggregate_id),
            "aggregate_type": self._aggregate_type,
            "event_type": self._event_type,
            "event_payload": self._event_payload,
            "status": self._status.value,
            "retry_count": self._retry_count,
            "max_retries": self._max_retries,
            "created_at": self._created_at.isoformat() if self._created_at else None,
            "published_at": self._published_at.isoformat() if self._published_at else None,
            "scheduled_at": self._scheduled_at.isoformat() if self._scheduled_at else None,
            "last_error": self._last_error,
        }

    def __repr__(self) -> str:
        return f"<OutboxEvent(id={self._id}, type={self._event_type}, status={self._status})>"
