"""
Dead Letter Processor Job.

This job handles events that have exceeded max retries.
It moves them to a dead letter queue for manual inspection or
attempts to reprocess them with different strategies.

Example 4: Jobs xử lý Outbox event
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from shared.application.ports import IEventBus, IJobService, ILogger


@dataclass
class DeadLetterConfig:
    """Configuration for dead letter processing."""

    # How often to check for dead letters (in seconds)
    check_interval_seconds: float = 3600.0  # 1 hour

    # Maximum retries before marking as permanently failed
    max_retries: int = 5

    # Batch size for processing
    batch_size: int = 50

    # How long to keep dead letters before archiving
    archive_after_days: int = 30


class DeadLetterProcessorJob:
    """
    Job for processing outbox events that have exceeded max retries.

    This demonstrates:
    - Scheduled job with JobService
    - Handling failed outbox events
    - Metrics collection
    - Alert triggering

    Usage:
        job = DeadLetterProcessorJob(
            session_factory=session_factory,
            event_bus=event_bus,
            job_service=job_service,
            logger=logger,
        )
        await job.start()
    """

    TASK_NAME = "outbox.dead_letter.process"

    def __init__(
        self,
        session_factory: "async_sessionmaker[AsyncSession]",
        event_bus: "IEventBus",
        job_service: "IJobService",
        logger: "ILogger",
        config: Optional[DeadLetterConfig] = None,
    ):
        """
        Initialize the job.

        Args:
            session_factory: Factory for creating database sessions
            event_bus: Event bus for publishing recovered events
            job_service: Job service for scheduling
            logger: Logger instance
            config: Job configuration
        """
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._job_service = job_service
        self._logger = logger
        self._config = config or DeadLetterConfig()
        self._running = False

        # Metrics
        self._total_processed = 0
        self._total_recovered = 0
        self._total_archived = 0

    async def start(self) -> None:
        """Start the dead letter processor job."""
        if self._running:
            self._logger.warning("Dead letter processor already running")
            return

        self._running = True

        # Register task with job service
        self._job_service.register_task(
            name=self.TASK_NAME,
            func=self._process_dead_letters,
            queue="outbox",
            max_retries=1,
            timeout=300,
        )

        # Schedule first run
        await self._schedule_next()

        self._logger.info(
            f"Dead letter processor started " f"(interval={self._config.check_interval_seconds}s)"
        )

    async def stop(self) -> None:
        """Stop the job."""
        self._running = False
        self._logger.info(
            f"Dead letter processor stopped. "
            f"Processed={self._total_processed}, "
            f"Recovered={self._total_recovered}, "
            f"Archived={self._total_archived}"
        )

    async def _schedule_next(self) -> None:
        """Schedule the next run."""
        if not self._running:
            return

        try:
            await self._job_service.enqueue(
                self.TASK_NAME,
                delay=int(self._config.check_interval_seconds),
            )
        except Exception as e:
            self._logger.error(f"Failed to schedule dead letter job: {e}")

    async def _process_dead_letters(self) -> dict:
        """
        Process dead letter events.

        Returns:
            Dictionary with processing results
        """
        from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import OutboxRepository

        results = {
            "processed": 0,
            "recovered": 0,
            "archived": 0,
            "errors": [],
        }

        try:
            async with self._session_factory() as session:
                repository = OutboxRepository(session)

                # Get events that have exceeded max retries
                dead_letters = await self._get_dead_letters(repository)

                if not dead_letters:
                    await self._schedule_next()
                    return results

                self._logger.info(f"Processing {len(dead_letters)} dead letter events")

                for event in dead_letters:
                    try:
                        result = await self._process_single(event, repository)
                        if result == "recovered":
                            results["recovered"] += 1
                        elif result == "archived":
                            results["archived"] += 1
                        results["processed"] += 1
                    except Exception as e:
                        results["errors"].append(str(e))
                        self._logger.error(f"Error processing dead letter {event.id}: {e}")

                # Update metrics
                self._total_processed += results["processed"]
                self._total_recovered += results["recovered"]
                self._total_archived += results["archived"]

                # Alert if there are many dead letters
                if len(dead_letters) > 10:
                    self._logger.warning(
                        f"High number of dead letter events: {len(dead_letters)}. "
                        "Consider investigating root cause."
                    )

        except Exception as e:
            self._logger.error(f"Error in dead letter processing: {e}")
            results["errors"].append(str(e))

        # Schedule next run
        await self._schedule_next()

        return results

    async def _get_dead_letters(self, repository) -> List:
        """
        Get events that have exceeded max retries.

        Args:
            repository: Outbox repository

        Returns:
            List of dead letter events
        """
        # This would be a custom query in the repository
        # For now, we simulate it
        return await repository.get_failed_events(
            max_retries=self._config.max_retries,
            limit=self._config.batch_size,
        )

    async def _process_single(self, event, repository) -> str:
        """
        Process a single dead letter event.

        Strategies:
        1. If transient error (timeout, connection), reset and retry
        2. If permanent error (validation, missing data), archive
        3. If old enough, archive regardless

        Args:
            event: The dead letter event
            repository: Outbox repository

        Returns:
            "recovered" if event was reset for retry
            "archived" if event was archived
        """
        # Check if event is old enough to archive
        archive_threshold = datetime.utcnow() - timedelta(days=self._config.archive_after_days)

        if event.created_at < archive_threshold:
            await repository.archive_event(event.id)
            self._logger.info(f"Archived old dead letter event: {event.id}")
            return "archived"

        # Check if error is transient (could be retried)
        if self._is_transient_error(event.last_error):
            # Reset retry count and schedule for retry
            await repository.reset_for_retry(event.id)
            self._logger.info(f"Reset dead letter event for retry: {event.id}")
            return "recovered"

        # Permanent error - archive
        await repository.archive_event(event.id)
        self._logger.info(f"Archived dead letter event (permanent error): {event.id}")
        return "archived"

    def _is_transient_error(self, error: Optional[str]) -> bool:
        """
        Determine if an error is transient and can be retried.

        Args:
            error: Error message

        Returns:
            True if error is transient
        """
        if not error:
            return False

        transient_patterns = [
            "timeout",
            "connection",
            "temporarily unavailable",
            "rate limit",
            "503",
            "502",
            "504",
        ]

        error_lower = error.lower()
        return any(pattern in error_lower for pattern in transient_patterns)

    def get_stats(self) -> dict:
        """Get job statistics."""
        return {
            "running": self._running,
            "total_processed": self._total_processed,
            "total_recovered": self._total_recovered,
            "total_archived": self._total_archived,
            "config": {
                "check_interval_seconds": self._config.check_interval_seconds,
                "max_retries": self._config.max_retries,
                "batch_size": self._config.batch_size,
            },
        }
