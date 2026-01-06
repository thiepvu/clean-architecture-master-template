"""
Unit of Work with Outbox Pattern support.

This module provides UoW implementations that save domain events
to the outbox table in the same transaction as aggregate changes.

Note: This is a base UoW for Outbox pattern. For bounded context-specific
operations, use context-specific UoW implementations that expose repositories.
"""

from typing import TYPE_CHECKING, Any, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.ports import IEventBus, IUnitOfWork, IUnitOfWorkFactory
from shared.domain.base_aggregate import AggregateRoot

from .models import OutboxEvent
from .repository import OutboxRepository

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class OutboxUnitOfWork(IUnitOfWork):
    """
    Unit of Work with Outbox Pattern support.

    This UoW saves domain events to the outbox table in the SAME transaction
    as aggregate changes, ensuring atomic consistency.

    Flow:
    1. __aenter__: Create session
    2. Application code: Persist aggregates, track them
    3. commit():
       a. Collect events from tracked aggregates
       b. Save events to outbox table (same transaction)
       c. Commit transaction (aggregate changes + outbox events)
       d. Optionally publish to in-memory event bus for immediate handlers
    4. __aexit__: Close session

    Benefits:
    - Events are guaranteed to be persisted with aggregate changes
    - No orphan events (events without data) or orphan data (data without events)
    - Background processor handles reliable delivery
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: "ILogger",
        event_bus: Optional[IEventBus] = None,
        publish_immediately: bool = False,
    ):
        """
        Initialize Unit of Work with Outbox support.

        Args:
            session_factory: Factory to create new sessions
            logger: Logger instance (injected via DI)
            event_bus: Optional event bus for immediate publishing after commit
            publish_immediately: If True, also publish to event bus after commit
                                 (dual-write for immediate handlers)
        """
        self._session_factory = session_factory
        self._logger = logger
        self._session: Optional[AsyncSession] = None
        self._event_bus = event_bus
        self._publish_immediately = publish_immediately
        self._is_committed = False
        self._is_rolled_back = False
        self._tracked_aggregates: List[AggregateRoot] = []
        self._outbox_repository: Optional[OutboxRepository] = None

    def track(self, aggregate: AggregateRoot) -> None:
        """
        Track an aggregate for event collection.

        Args:
            aggregate: Aggregate root to track
        """
        if aggregate not in self._tracked_aggregates:
            self._tracked_aggregates.append(aggregate)

    async def __aenter__(self) -> "OutboxUnitOfWork":
        """
        Enter async context manager.
        Creates a NEW session for this UoW.

        Returns:
            Self
        """
        # Create NEW session for this UoW
        self._session = self._session_factory()

        # Create outbox repository with the same session
        self._outbox_repository = OutboxRepository(self._session, self._logger)

        self._logger.debug("OutboxUoW: Created new session and started transaction")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit async context manager.
        Commits on success, rolls back on exception.
        Always closes session.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        try:
            if exc_type is not None:
                self._logger.warning(
                    f"OutboxUoW: Exception occurred: {exc_type.__name__}: {exc_val}"
                )
                await self.rollback()
            else:
                if not self._is_committed and not self._is_rolled_back:
                    await self.commit()
        finally:
            # ALWAYS close session
            await self._close_session()
            self._logger.debug("OutboxUoW: Transaction ended, session closed")

    async def _close_session(self) -> None:
        """Close session."""
        if self._session is not None:
            await self._session.close()
            self._session = None
            self._outbox_repository = None

    async def commit(self) -> None:
        """
        Commit the transaction with outbox pattern.

        Flow:
        1. Collect events from tracked aggregates
        2. Save events to outbox table (same transaction)
        3. Commit transaction (atomic: data + events)
        4. Optionally publish to in-memory event bus
        """
        if self._is_rolled_back:
            self._logger.warning("OutboxUoW: Cannot commit - already rolled back")
            return

        if self._is_committed:
            self._logger.warning("OutboxUoW: Already committed")
            return

        if self._session is None:
            self._logger.error("OutboxUoW: No session to commit")
            return

        try:
            # 1. Collect events from tracked aggregates
            outbox_events = self._collect_outbox_events()

            # 2. Save events to outbox table (same transaction)
            if outbox_events and self._outbox_repository:
                await self._outbox_repository.save_many(outbox_events)
                self._logger.debug(f"OutboxUoW: Saved {len(outbox_events)} events to outbox")

            # 3. Commit transaction (atomic: aggregate changes + outbox events)
            await self._session.commit()
            self._is_committed = True
            self._logger.debug("OutboxUoW: Transaction committed successfully")

            # 4. Optionally publish to in-memory event bus for immediate handlers
            if self._publish_immediately and outbox_events:
                await self._publish_to_event_bus(outbox_events)

        except Exception as e:
            self._logger.error(f"OutboxUoW: Error committing: {e}")
            await self.rollback()
            raise

    def _collect_outbox_events(self) -> List[OutboxEvent]:
        """
        Collect domain events from tracked aggregates and convert to outbox events.

        Returns:
            List of OutboxEvent ready to be persisted
        """
        outbox_events = []

        for aggregate in self._tracked_aggregates:
            aggregate_id = self._get_aggregate_id(aggregate)
            aggregate_type = aggregate.__class__.__name__

            for domain_event in aggregate.domain_events:
                outbox_event = OutboxEvent.from_domain_event(
                    domain_event=domain_event,
                    aggregate_id=aggregate_id,
                    aggregate_type=aggregate_type,
                )
                outbox_events.append(outbox_event)

            # Clear events from aggregate
            aggregate.clear_domain_events()

        self._tracked_aggregates.clear()
        return outbox_events

    def _get_aggregate_id(self, aggregate: AggregateRoot) -> UUID:
        """
        Get the ID of an aggregate.

        Args:
            aggregate: The aggregate to get ID from

        Returns:
            UUID of the aggregate
        """
        # Try common ID attribute names
        if hasattr(aggregate, "id"):
            id_value = aggregate.id
            if isinstance(id_value, UUID):
                return id_value
            elif hasattr(id_value, "value"):  # Value object
                return id_value.value

        raise ValueError(
            f"Cannot determine ID for aggregate {aggregate.__class__.__name__}. "
            f"Ensure aggregate has 'id' attribute."
        )

    async def _publish_to_event_bus(self, outbox_events: List[OutboxEvent]) -> None:
        """
        Publish events to in-memory event bus for immediate handlers.

        This is optional dual-write for handlers that need immediate processing.
        The outbox processor handles reliable delivery separately.

        Args:
            outbox_events: Events to publish
        """
        if not self._event_bus:
            return

        from infrastructure.outbox.publisher import DomainEventFactory

        domain_events = []
        for outbox_event in outbox_events:
            domain_event = DomainEventFactory.create(
                outbox_event.event_type,
                outbox_event.event_payload,
            )
            if domain_event:
                domain_events.append(domain_event)

        if domain_events:
            self._logger.debug(f"OutboxUoW: Publishing {len(domain_events)} events to event bus")
            await self._event_bus.publish_many(domain_events)

    async def rollback(self) -> None:
        """
        Rollback the transaction.
        Discards all changes and clears tracked aggregates.
        """
        if self._is_rolled_back:
            self._logger.warning("OutboxUoW: Already rolled back")
            return

        if self._session is None:
            self._logger.warning("OutboxUoW: No session to rollback")
            self._is_rolled_back = True
            return

        try:
            await self._session.rollback()
            self._is_rolled_back = True
            self._tracked_aggregates.clear()
            self._logger.debug("OutboxUoW: Transaction rolled back")
        except Exception as e:
            self._logger.error(f"OutboxUoW: Error rolling back: {e}")
            raise

    async def refresh(self, entity: Any) -> None:
        """
        Refresh entity state from database.

        Args:
            entity: Entity to refresh
        """
        if self._session is None:
            raise RuntimeError("OutboxUoW: No active session")

        try:
            await self._session.refresh(entity)
            self._logger.debug(f"OutboxUoW: Refreshed entity: {entity.__class__.__name__}")
        except Exception as e:
            self._logger.error(f"OutboxUoW: Error refreshing entity: {e}")
            raise

    async def flush(self) -> None:
        """
        Flush pending changes to database without committing.
        Useful for getting auto-generated IDs.
        """
        if self._session is None:
            raise RuntimeError("OutboxUoW: No active session")

        try:
            await self._session.flush()
            self._logger.debug("OutboxUoW: Session flushed")
        except Exception as e:
            self._logger.error(f"OutboxUoW: Error flushing: {e}")
            raise

    @property
    def session(self) -> AsyncSession:
        """
        Get the underlying session.

        Returns:
            SQLAlchemy async session

        Raises:
            RuntimeError: If no active session
        """
        if self._session is None:
            raise RuntimeError("OutboxUoW: No active session. Use within 'async with' context.")
        return self._session


class OutboxUnitOfWorkFactory(IUnitOfWorkFactory):
    """
    Factory for creating Unit of Work instances with Outbox support.

    Each call to create() returns a NEW UoW with its OWN session.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: "ILogger",
        event_bus: Optional[IEventBus] = None,
        publish_immediately: bool = False,
    ):
        """
        Initialize factory.

        Args:
            session_factory: SQLAlchemy async session factory
            logger: Logger instance (injected via DI)
            event_bus: Optional event bus for immediate publishing
            publish_immediately: If True, also publish to event bus after commit
        """
        self._session_factory = session_factory
        self._logger = logger
        self._event_bus = event_bus
        self._publish_immediately = publish_immediately
        self._logger.debug("OutboxUnitOfWorkFactory initialized")

    def create(self) -> OutboxUnitOfWork:
        """
        Create a new Unit of Work with Outbox support.

        Returns:
            New OutboxUnitOfWork instance
        """
        return OutboxUnitOfWork(
            session_factory=self._session_factory,
            logger=self._logger,
            event_bus=self._event_bus,
            publish_immediately=self._publish_immediately,
        )
