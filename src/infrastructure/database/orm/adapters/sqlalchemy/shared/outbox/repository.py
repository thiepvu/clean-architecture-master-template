"""
Outbox Repository for SQLAlchemy.

Provides CRUD operations for outbox events with support for:
- Fetching unpublished events in batches
- Marking events as published or failed
- Cleaning up old published events
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.application.ports import IOutboxRepository, OutboxEventStatus

from .models import OutboxEvent, OutboxEventModel

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class OutboxRepository(IOutboxRepository):
    """
    SQLAlchemy implementation of the outbox repository.

    Implements IOutboxRepository interface from shared.application.ports.
    """

    def __init__(self, session: AsyncSession, logger: Optional["ILogger"] = None):
        """
        Initialize repository with session.

        Args:
            session: SQLAlchemy async session
            logger: Optional logger instance (injected via DI)
        """
        self._session = session
        self._logger = logger

    def _to_model(self, event: OutboxEvent) -> OutboxEventModel:
        """Convert domain event to SQLAlchemy model."""
        return OutboxEventModel(
            id=event.id,
            aggregate_id=event.aggregate_id,
            aggregate_type=event.aggregate_type,
            event_type=event.event_type,
            event_payload=event.event_payload,
            status=(
                event.status.value if isinstance(event.status, OutboxEventStatus) else event.status
            ),
            retry_count=event.retry_count,
            max_retries=event.max_retries,
            created_at=event.created_at,
            published_at=event.published_at,
            scheduled_at=event.scheduled_at,
            last_error=event.last_error,
        )

    def _to_domain(self, model: OutboxEventModel) -> OutboxEvent:
        """Convert SQLAlchemy model to domain event."""
        status = model.status
        if isinstance(status, str):
            status = OutboxEventStatus(status)

        return OutboxEvent(
            id=model.id,
            aggregate_id=model.aggregate_id,
            aggregate_type=model.aggregate_type,
            event_type=model.event_type,
            event_payload=model.event_payload,
            status=status,
            retry_count=model.retry_count,
            max_retries=model.max_retries,
            created_at=model.created_at,
            published_at=model.published_at,
            scheduled_at=model.scheduled_at,
            last_error=model.last_error,
        )

    async def save(self, event: OutboxEvent) -> OutboxEvent:
        """Save an outbox event."""
        model = self._to_model(event)
        self._session.add(model)
        await self._session.flush()
        if self._logger:
            self._logger.debug(f"Saved outbox event: {event.id} ({event.event_type})")
        return event

    async def save_many(self, events: List[OutboxEvent]) -> List[OutboxEvent]:
        """Save multiple outbox events in a batch."""
        if not events:
            return []

        models = [self._to_model(e) for e in events]
        self._session.add_all(models)
        await self._session.flush()
        if self._logger:
            self._logger.debug(f"Saved {len(events)} outbox events")
        return events

    async def get_unpublished(
        self,
        limit: int = 100,
        before: Optional[datetime] = None,
    ) -> List[OutboxEvent]:
        """Get unpublished events ready for processing."""
        before = before or datetime.utcnow()

        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.status == OutboxEventStatus.PENDING.value)
            .where(OutboxEventModel.scheduled_at <= before)
            .order_by(OutboxEventModel.created_at.asc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        events = [self._to_domain(m) for m in models]
        if self._logger:
            self._logger.debug(f"Fetched {len(events)} unpublished outbox events")
        return events

    async def mark_as_published(self, event_id: UUID) -> bool:
        """Mark an event as successfully published."""
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .where(OutboxEventModel.status == OutboxEventStatus.PENDING.value)
            .values(
                status=OutboxEventStatus.PUBLISHED.value,
                published_at=datetime.utcnow(),
            )
        )

        result = await self._session.execute(stmt)
        await self._session.commit()

        if result.rowcount > 0:
            if self._logger:
                self._logger.debug(f"Marked outbox event as published: {event_id}")
            return True
        return False

    async def mark_as_failed(self, event_id: UUID, error: str) -> bool:
        """Mark an event as permanently failed."""
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                status=OutboxEventStatus.FAILED.value,
                last_error=error,
            )
        )

        result = await self._session.execute(stmt)
        await self._session.commit()

        if result.rowcount > 0:
            if self._logger:
                self._logger.warning(f"Marked outbox event as failed: {event_id} - {error}")
            return True
        return False

    async def increment_retry(
        self,
        event_id: UUID,
        error: str,
        next_scheduled_at: datetime,
    ) -> bool:
        """Increment retry count and schedule next attempt."""
        # First, get the current event to check retry count
        stmt = select(OutboxEventModel).where(OutboxEventModel.id == event_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        new_retry_count = model.retry_count + 1

        # Check if max retries exceeded
        if new_retry_count >= model.max_retries:
            return await self.mark_as_failed(
                event_id,
                f"Max retries ({model.max_retries}) exceeded. Last error: {error}",
            )

        # Update with new retry count and scheduled time
        update_stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(
                retry_count=new_retry_count,
                last_error=error,
                scheduled_at=next_scheduled_at,
            )
        )

        await self._session.execute(update_stmt)
        await self._session.commit()

        if self._logger:
            self._logger.info(
                f"Outbox event {event_id} retry {new_retry_count}/{model.max_retries}, "
                f"next attempt at {next_scheduled_at}"
            )
        return True

    async def cleanup_published(self, older_than: timedelta) -> int:
        """Delete published events older than specified duration."""
        cutoff = datetime.utcnow() - older_than

        stmt = (
            delete(OutboxEventModel)
            .where(OutboxEventModel.status == OutboxEventStatus.PUBLISHED.value)
            .where(OutboxEventModel.published_at < cutoff)
        )

        result = await self._session.execute(stmt)
        await self._session.commit()

        count = result.rowcount
        if count > 0 and self._logger:
            self._logger.info(f"Cleaned up {count} published outbox events older than {older_than}")
        return count

    async def get_failed_events(self, limit: int = 100) -> List[OutboxEvent]:
        """Get events that have permanently failed (dead letter queue)."""
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.status == OutboxEventStatus.FAILED.value)
            .order_by(OutboxEventModel.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def retry_failed_event(self, event_id: UUID) -> bool:
        """Reset a failed event to pending for retry."""
        stmt = (
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .where(OutboxEventModel.status == OutboxEventStatus.FAILED.value)
            .values(
                status=OutboxEventStatus.PENDING.value,
                retry_count=0,
                scheduled_at=datetime.utcnow(),
                last_error=None,
            )
        )

        result = await self._session.execute(stmt)
        await self._session.commit()

        if result.rowcount > 0:
            if self._logger:
                self._logger.info(f"Reset failed outbox event for retry: {event_id}")
            return True
        return False
