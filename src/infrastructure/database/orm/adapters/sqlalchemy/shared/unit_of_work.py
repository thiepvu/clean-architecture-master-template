"""
Base Unit of Work Implementation for SQLAlchemy.

Provides the core UoW functionality. Context-specific UoW classes
should extend this to add repository properties.

Pattern: UoW owns session and exposes repositories as properties.
- Session is created when entering context
- Repositories receive session in constructor (created lazily)
- Session is closed when exiting context
- No ContextVar needed - explicit dependency injection

Event Handling:
- Direct events (DomainEvent only) → Published immediately to Event Bus
- Outbox events (DomainEvent + OutboxEvent) → Saved to outbox table first
"""

from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.ports.event_bus import IEventBus
from shared.application.ports.unit_of_work import IUnitOfWork, IUnitOfWorkFactory
from shared.domain.base_aggregate import AggregateRoot
from shared.domain.events import DomainEvent, OutboxEvent

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class BaseUnitOfWork(IUnitOfWork):
    """
    Base Unit of Work implementation with SQLAlchemy.

    Provides core transaction management functionality.
    Context-specific UoW classes should extend this and add
    repository properties that create repositories with the session.

    Example:
        class UserManagementUoW(BaseUnitOfWork, IUserManagementUoW):
            @property
            def users(self) -> IUserRepository:
                if self._user_repo is None:
                    self._user_repo = UserRepository(self.session)
                return self._user_repo
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: Optional[IEventBus] = None,
        logger: Optional["ILogger"] = None,
    ):
        """
        Initialize Unit of Work.

        Args:
            session_factory: Factory to create new sessions
            event_bus: Optional event bus for publishing domain events
            logger: Optional logger instance (injected via DI)
        """
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self._event_bus = event_bus
        self._logger = logger
        self._is_committed = False
        self._is_rolled_back = False
        self._tracked_aggregates: List[AggregateRoot] = []

    @property
    def session(self) -> AsyncSession:
        """
        Get the current session.

        Returns:
            AsyncSession instance

        Raises:
            RuntimeError: If no active session
        """
        if self._session is None:
            raise RuntimeError("UoW: No active session. Use within 'async with' context.")
        return self._session

    def track(self, aggregate: AggregateRoot) -> None:
        """
        Track an aggregate for event collection.

        Args:
            aggregate: Aggregate root to track
        """
        if aggregate not in self._tracked_aggregates:
            self._tracked_aggregates.append(aggregate)

    async def __aenter__(self) -> "BaseUnitOfWork":
        """
        Enter async context manager.
        Creates a NEW session for this UoW.

        Returns:
            Self
        """
        self._session = self._session_factory()
        if self._logger:
            self._logger.debug("UoW: Created new session and started transaction")
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
                if self._logger:
                    self._logger.warning(f"UoW: Exception occurred: {exc_type.__name__}: {exc_val}")
                await self.rollback()
            else:
                if not self._is_committed and not self._is_rolled_back:
                    await self.commit()
        finally:
            await self._close_session()
            if self._logger:
                self._logger.debug("UoW: Transaction ended, session closed")

    async def _close_session(self) -> None:
        """Close session."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        """
        Commit the transaction.

        Flow:
        1. Collect events from tracked aggregates
        2. Save OutboxEvents to outbox table (SAME transaction)
        3. Commit transaction (aggregate + outbox atomically)
        4. Publish direct events to Event Bus (after commit)
        """
        if self._is_rolled_back:
            if self._logger:
                self._logger.warning("UoW: Cannot commit - already rolled back")
            return

        if self._is_committed:
            if self._logger:
                self._logger.warning("UoW: Already committed")
            return

        if self._session is None:
            if self._logger:
                self._logger.error("UoW: No session to commit")
            return

        try:
            # 1. Collect and separate events BEFORE commit
            direct_events, outbox_events = self._collect_and_separate_events()

            # 2. Save outbox events to DB (SAME transaction as aggregate)
            if outbox_events:
                await self._save_to_outbox_in_transaction(outbox_events)

            # 3. Commit transaction (aggregate changes + outbox events atomically)
            await self._session.commit()
            self._is_committed = True

            if self._logger:
                self._logger.info(
                    f"💾 UoW: Committed "
                    f"(direct={len(direct_events)}, outbox={len(outbox_events)})"
                )

            # 4. Publish direct events AFTER commit (fire-and-forget)
            if direct_events and self._event_bus:
                await self._event_bus.publish_many(direct_events)
                if self._logger:
                    self._logger.debug(f"UoW: Published {len(direct_events)} direct events")

        except Exception as e:
            if self._logger:
                self._logger.error(f"UoW: Error committing: {e}", exc_info=True)
            await self.rollback()
            raise

        finally:
            self._tracked_aggregates.clear()

    def _collect_and_separate_events(self) -> tuple:
        """
        Collect events from tracked aggregates and separate by type.

        Returns:
            Tuple of (direct_events, outbox_events)
        """
        from shared.domain.events import OutboxEvent

        direct_events = []
        outbox_events = []

        if self._logger:
            self._logger.debug(
                f"UoW: Collecting events from {len(self._tracked_aggregates)} tracked aggregates"
            )

        for aggregate in self._tracked_aggregates:
            events = aggregate.domain_events
            if self._logger:
                self._logger.debug(
                    f"UoW: Aggregate {aggregate.__class__.__name__} has {len(events)} events"
                )

            for event in events:
                event_type = event.__class__.__name__
                is_outbox = isinstance(event, OutboxEvent)
                if self._logger:
                    self._logger.debug(f"UoW: Event {event_type} is_outbox={is_outbox}")

                if is_outbox:
                    outbox_events.append((aggregate, event))
                else:
                    direct_events.append(event)
            aggregate.clear_domain_events()

        return direct_events, outbox_events

    async def _save_to_outbox_in_transaction(self, aggregate_events: list) -> None:
        """
        Save outbox events in the SAME transaction as aggregate changes.

        This ensures atomicity: either both aggregate AND events are saved, or neither.

        Args:
            aggregate_events: List of (aggregate, event) tuples
        """
        from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import (
            OutboxEvent as OutboxEventModel,
        )
        from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import OutboxRepository

        # Use the SAME session (same transaction)
        repository = OutboxRepository(self._session, self._logger)

        outbox_entries = []
        for aggregate, event in aggregate_events:
            aggregate_id = self._get_aggregate_id(aggregate)
            aggregate_type = aggregate.__class__.__name__

            outbox_entry = OutboxEventModel.from_domain_event(
                domain_event=event,
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
            )
            outbox_entries.append(outbox_entry)

        if outbox_entries:
            await repository.save_many(outbox_entries)
            if self._logger:
                self._logger.info(
                    f"📦 UoW: Saved {len(outbox_entries)} to outbox "
                    f"({', '.join(e.event_type for e in outbox_entries)})"
                )

    def _get_aggregate_id(self, aggregate) -> "UUID":
        """Get aggregate ID."""
        from uuid import UUID

        if hasattr(aggregate, "id"):
            id_val = aggregate.id
            if isinstance(id_val, UUID):
                return id_val
            if hasattr(id_val, "value"):
                return id_val.value
        raise ValueError(f"Cannot get ID from aggregate {aggregate.__class__.__name__}")

    def _infer_aggregate_type(self, event) -> str:
        """Infer aggregate type from event class name."""
        event_name = event.__class__.__name__

        # Common patterns: UserCreatedEvent -> User, FileUploadedEvent -> File
        if "User" in event_name:
            if "Profile" in event_name:
                return "UserProfile"
            return "User"
        elif "File" in event_name:
            return "File"
        else:
            # Fallback: remove "Event" suffix
            return event_name.replace("Event", "")

    async def rollback(self) -> None:
        """
        Rollback the transaction.
        Discards all changes and clears tracked aggregates.
        """
        if self._is_rolled_back:
            if self._logger:
                self._logger.warning("UoW: Already rolled back")
            return

        if self._session is None:
            if self._logger:
                self._logger.warning("UoW: No session to rollback")
            self._is_rolled_back = True
            return

        try:
            await self._session.rollback()
            self._is_rolled_back = True
            self._tracked_aggregates.clear()
            if self._logger:
                self._logger.debug("UoW: Transaction rolled back")
        except Exception as e:
            if self._logger:
                self._logger.error(f"UoW: Error rolling back: {e}", exc_info=True)
            raise


class BaseUnitOfWorkFactory(IUnitOfWorkFactory):
    """
    Base factory for creating Unit of Work instances.

    Context-specific factories should extend this and override
    create() to return the appropriate UoW type.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: Optional[IEventBus] = None,
        logger: Optional["ILogger"] = None,
    ):
        """
        Initialize factory.

        Args:
            session_factory: SQLAlchemy async session factory
            event_bus: Optional event bus for domain events
            logger: Optional logger instance (injected via DI)
        """
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._logger = logger
        if self._logger:
            self._logger.debug("BaseUnitOfWorkFactory initialized")

    def create(self) -> BaseUnitOfWork:
        """
        Create a new Unit of Work.

        Returns:
            New BaseUnitOfWork instance
        """
        return BaseUnitOfWork(
            session_factory=self._session_factory,
            event_bus=self._event_bus,
            logger=self._logger,
        )
