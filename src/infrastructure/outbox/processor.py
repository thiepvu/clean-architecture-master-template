"""
Outbox Processor for reliable event publishing.

This processor uses the JobsModule to schedule background tasks
for polling and publishing outbox events.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import (
    OutboxEvent,
    OutboxRepository,
)
from infrastructure.outbox.publisher import OutboxEventPublisher
from shared.application.ports import IEventBus, IJobService, IOutboxProcessor

if TYPE_CHECKING:
    from shared.application.ports import ILogger


@dataclass
class OutboxProcessorConfig:
    """Configuration for the outbox processor."""

    batch_size: int = 100
    poll_interval_seconds: float = 5.0
    retry_backoff_seconds: int = 60
    max_retries: int = 5
    cleanup_interval_seconds: float = 3600.0  # 1 hour
    cleanup_older_than_days: int = 7


class OutboxProcessor(IOutboxProcessor):
    """
    Outbox processor that uses JobsModule for background task scheduling.

    Features:
    - Uses IJobService for task scheduling instead of raw asyncio
    - Polls outbox table for unpublished events
    - Publishes events to event bus
    - Handles failures with exponential backoff
    - Cleans up old published events
    """

    # Task names for registration with JobService
    TASK_PROCESS_BATCH = "outbox.process_batch"
    TASK_CLEANUP = "outbox.cleanup"

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: IEventBus,
        job_service: IJobService,
        logger: "ILogger",
        config: Optional[OutboxProcessorConfig] = None,
    ):
        """
        Initialize the outbox processor.

        Args:
            session_factory: Factory for creating database sessions
            event_bus: Event bus for publishing events
            job_service: Job service for background task scheduling
            logger: Logger instance (injected via DI)
            config: Processor configuration
        """
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._job_service = job_service
        self._logger = logger
        self._config = config or OutboxProcessorConfig()
        self._publisher = OutboxEventPublisher(event_bus, logger)
        self._running = False

        # Metrics
        self._events_processed = 0
        self._events_failed = 0
        self._last_poll_at: Optional[datetime] = None

        # Register tasks with job service
        self._register_tasks()

    def _register_tasks(self) -> None:
        """Register outbox processing tasks with job service."""
        # Register batch processing task
        self._job_service.register_task(
            name=self.TASK_PROCESS_BATCH,
            func=self._process_batch_task,
            queue="outbox",
            max_retries=1,  # Don't retry the task itself, we handle retries per event
            timeout=int(self._config.poll_interval_seconds * 10),
        )

        # Register cleanup task
        self._job_service.register_task(
            name=self.TASK_CLEANUP,
            func=self._cleanup_task,
            queue="outbox",
            max_retries=3,
            timeout=300,
        )

        self._logger.info("Outbox processor tasks registered with job service")

    async def start(self) -> None:
        """Start the background processor by scheduling recurring jobs."""
        if self._running:
            self._logger.warning("Outbox processor already running")
            return

        self._running = True
        self._logger.info(
            f"Starting outbox processor (batch_size={self._config.batch_size}, "
            f"poll_interval={self._config.poll_interval_seconds}s)"
        )

        # Schedule first batch processing
        await self._schedule_next_batch()

        # Schedule first cleanup
        await self._schedule_cleanup()

    async def stop(self, timeout: float = 10.0) -> None:
        """
        Stop the background processor gracefully.

        Args:
            timeout: Maximum seconds to wait for shutdown (unused, kept for interface)
        """
        if not self._running:
            return

        self._logger.info("Stopping outbox processor...")
        self._running = False

        self._logger.info(
            f"Outbox processor stopped. "
            f"Processed: {self._events_processed}, Failed: {self._events_failed}"
        )

    async def _schedule_next_batch(self) -> None:
        """Schedule the next batch processing job."""
        if not self._running:
            return

        try:
            await self._job_service.enqueue(
                self.TASK_PROCESS_BATCH,
                delay=int(self._config.poll_interval_seconds),
            )
        except Exception as e:
            self._logger.error(f"Failed to schedule next batch: {e}")

    async def _schedule_cleanup(self) -> None:
        """Schedule the next cleanup job."""
        if not self._running:
            return

        try:
            await self._job_service.enqueue(
                self.TASK_CLEANUP,
                delay=int(self._config.cleanup_interval_seconds),
            )
        except Exception as e:
            self._logger.error(f"Failed to schedule cleanup: {e}")

    async def _process_batch_task(self) -> int:
        """
        Task function for processing a batch of outbox events.
        Called by the job service.

        Returns:
            Number of events processed
        """
        try:
            count = await self.process_batch()

            # Schedule next batch if still running
            await self._schedule_next_batch()

            return count
        except Exception as e:
            self._logger.error(f"Error in batch processing task: {e}")
            # Still schedule next batch even on error
            await self._schedule_next_batch()
            raise

    async def _cleanup_task(self) -> int:
        """
        Task function for cleaning up old published events.
        Called by the job service.

        Returns:
            Number of events cleaned up
        """
        try:
            count = await self._cleanup_old_events()

            # Schedule next cleanup if still running
            await self._schedule_cleanup()

            return count
        except Exception as e:
            self._logger.error(f"Error in cleanup task: {e}")
            # Still schedule next cleanup even on error
            await self._schedule_cleanup()
            raise

    async def process_batch(self) -> int:
        """
        Process a batch of unpublished events.

        Returns:
            Number of events processed
        """
        self._last_poll_at = datetime.utcnow()

        # Create a new session for this batch
        async with self._session_factory() as session:
            repository = OutboxRepository(session)

            # Fetch unpublished events
            events = await repository.get_unpublished(
                limit=self._config.batch_size,
                before=datetime.utcnow(),
            )

            if not events:
                return 0

            self._logger.info(f"📦 Outbox: Processing {len(events)} pending events")

            processed = 0
            for event in events:
                success = await self._process_event(event, repository)
                if success:
                    processed += 1

            return processed

    async def _process_event(
        self,
        event: OutboxEvent,
        repository: OutboxRepository,
    ) -> bool:
        """
        Process a single outbox event.

        Args:
            event: The event to process
            repository: Repository for updating event status

        Returns:
            True if event was successfully published
        """
        try:
            # Publish the event
            await self._publisher.publish(event)

            # Mark as published
            await repository.mark_as_published(event.id)

            self._events_processed += 1
            self._logger.info(
                f"✅ Outbox: Published {event.event_type} "
                f"[{str(event.id)[:8]}] for {event.aggregate_type}"
            )
            return True

        except Exception as e:
            error_msg = str(e)
            self._logger.warning(
                f"❌ Outbox: Failed {event.event_type} [{str(event.id)[:8]}]: {error_msg}"
            )

            # Calculate next retry time with exponential backoff
            next_retry = datetime.utcnow() + timedelta(
                seconds=self._config.retry_backoff_seconds * (2**event.retry_count)
            )

            # Increment retry or mark as failed
            await repository.increment_retry(event.id, error_msg, next_retry)

            self._events_failed += 1
            return False

    async def _cleanup_old_events(self) -> int:
        """
        Delete old published events.

        Returns:
            Number of events cleaned up
        """
        async with self._session_factory() as session:
            repository = OutboxRepository(session)

            older_than = timedelta(days=self._config.cleanup_older_than_days)
            count = await repository.cleanup_published(older_than)

            if count > 0:
                self._logger.info(f"Cleaned up {count} old published outbox events")

            return count

    def get_stats(self) -> dict:
        """Get processor statistics."""
        return {
            "running": self._running,
            "events_processed": self._events_processed,
            "events_failed": self._events_failed,
            "last_poll_at": self._last_poll_at.isoformat() if self._last_poll_at else None,
            "config": {
                "batch_size": self._config.batch_size,
                "poll_interval_seconds": self._config.poll_interval_seconds,
                "retry_backoff_seconds": self._config.retry_backoff_seconds,
                "max_retries": self._config.max_retries,
            },
        }


class OutboxProcessorFactory:
    """Factory for creating outbox processors."""

    @staticmethod
    def create(
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: IEventBus,
        job_service: IJobService,
        logger: "ILogger",
        config: Optional[OutboxProcessorConfig] = None,
    ) -> OutboxProcessor:
        """
        Create an outbox processor.

        Args:
            session_factory: Factory for creating database sessions
            event_bus: Event bus for publishing events
            job_service: Job service for background task scheduling
            logger: Logger instance (injected via DI)
            config: Optional processor configuration

        Returns:
            Configured outbox processor
        """
        return OutboxProcessor(
            session_factory=session_factory,
            event_bus=event_bus,
            job_service=job_service,
            logger=logger,
            config=config,
        )
