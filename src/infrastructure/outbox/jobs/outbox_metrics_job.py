"""
Outbox Metrics Collection Job.

Collects and reports metrics about outbox processing:
- Queue depth (pending events)
- Processing rate
- Failure rate
- Average latency

This job demonstrates scheduled data collection with JobService.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from shared.application.ports import IJobService, ILogger


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""

    # Collection interval (in seconds)
    collection_interval_seconds: float = 60.0  # 1 minute

    # Time window for rate calculations
    rate_window_minutes: int = 5

    # Alert thresholds
    queue_depth_warning: int = 100
    queue_depth_critical: int = 500
    failure_rate_warning: float = 0.1  # 10%
    failure_rate_critical: float = 0.25  # 25%


@dataclass
class OutboxMetrics:
    """Snapshot of outbox metrics."""

    timestamp: datetime
    pending_count: int
    published_count_last_window: int
    failed_count_last_window: int
    average_latency_ms: float
    oldest_pending_age_seconds: Optional[float]

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        total = self.published_count_last_window + self.failed_count_last_window
        if total == 0:
            return 0.0
        return self.failed_count_last_window / total

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "pending_count": self.pending_count,
            "published_count_last_window": self.published_count_last_window,
            "failed_count_last_window": self.failed_count_last_window,
            "failure_rate": round(self.failure_rate, 4),
            "average_latency_ms": round(self.average_latency_ms, 2),
            "oldest_pending_age_seconds": self.oldest_pending_age_seconds,
        }


class OutboxMetricsJob:
    """
    Job for collecting outbox metrics.

    This demonstrates:
    - Periodic data collection with JobService
    - Metrics aggregation
    - Threshold-based alerting
    - Health monitoring

    Usage:
        job = OutboxMetricsJob(
            session_factory=session_factory,
            job_service=job_service,
            logger=logger,
        )
        await job.start()

        # Get current metrics
        metrics = job.get_latest_metrics()
    """

    TASK_NAME = "outbox.metrics.collect"

    def __init__(
        self,
        session_factory: "async_sessionmaker[AsyncSession]",
        job_service: "IJobService",
        logger: "ILogger",
        config: Optional[MetricsConfig] = None,
    ):
        """
        Initialize the job.

        Args:
            session_factory: Factory for creating database sessions
            job_service: Job service for scheduling
            logger: Logger instance
            config: Job configuration
        """
        self._session_factory = session_factory
        self._job_service = job_service
        self._logger = logger
        self._config = config or MetricsConfig()
        self._running = False

        # Store latest metrics
        self._latest_metrics: Optional[OutboxMetrics] = None
        self._metrics_history: list = []
        self._max_history_size = 60  # Keep last 60 snapshots

    async def start(self) -> None:
        """Start the metrics collection job."""
        if self._running:
            self._logger.warning("Outbox metrics job already running")
            return

        self._running = True

        # Register task with job service
        self._job_service.register_task(
            name=self.TASK_NAME,
            func=self._collect_metrics,
            queue="metrics",
            max_retries=1,
            timeout=30,
        )

        # Schedule first collection
        await self._schedule_next()

        self._logger.info(
            f"Outbox metrics job started " f"(interval={self._config.collection_interval_seconds}s)"
        )

    async def stop(self) -> None:
        """Stop the job."""
        self._running = False
        self._logger.info("Outbox metrics job stopped")

    async def _schedule_next(self) -> None:
        """Schedule the next collection."""
        if not self._running:
            return

        try:
            await self._job_service.enqueue(
                self.TASK_NAME,
                delay=int(self._config.collection_interval_seconds),
            )
        except Exception as e:
            self._logger.error(f"Failed to schedule metrics collection: {e}")

    async def _collect_metrics(self) -> dict:
        """
        Collect outbox metrics.

        Returns:
            Dictionary with collected metrics
        """
        from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import OutboxRepository

        try:
            async with self._session_factory() as session:
                repository = OutboxRepository(session)

                # Collect metrics
                metrics = await self._gather_metrics(repository)

                # Store in history
                self._latest_metrics = metrics
                self._metrics_history.append(metrics)
                if len(self._metrics_history) > self._max_history_size:
                    self._metrics_history.pop(0)

                # Check thresholds and alert
                await self._check_thresholds(metrics)

                # Log summary
                self._logger.debug(
                    f"Outbox metrics: pending={metrics.pending_count}, "
                    f"failure_rate={metrics.failure_rate:.2%}, "
                    f"latency={metrics.average_latency_ms:.1f}ms"
                )

        except Exception as e:
            self._logger.error(f"Error collecting outbox metrics: {e}")

        # Schedule next collection
        await self._schedule_next()

        return self._latest_metrics.to_dict() if self._latest_metrics else {}

    async def _gather_metrics(self, repository) -> OutboxMetrics:
        """
        Gather metrics from the database.

        Args:
            repository: Outbox repository

        Returns:
            OutboxMetrics snapshot
        """
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self._config.rate_window_minutes)

        # Get counts
        pending_count = await repository.count_pending()
        published_count = await repository.count_published_since(window_start)
        failed_count = await repository.count_failed_since(window_start)

        # Get latency (time from creation to publishing)
        avg_latency = await repository.get_average_latency_ms(window_start)

        # Get oldest pending event age
        oldest_pending = await repository.get_oldest_pending()
        oldest_age = None
        if oldest_pending:
            oldest_age = (now - oldest_pending.created_at).total_seconds()

        return OutboxMetrics(
            timestamp=now,
            pending_count=pending_count,
            published_count_last_window=published_count,
            failed_count_last_window=failed_count,
            average_latency_ms=avg_latency or 0.0,
            oldest_pending_age_seconds=oldest_age,
        )

    async def _check_thresholds(self, metrics: OutboxMetrics) -> None:
        """
        Check metrics against thresholds and alert if necessary.

        Args:
            metrics: Current metrics snapshot
        """
        # Check queue depth
        if metrics.pending_count >= self._config.queue_depth_critical:
            self._logger.error(
                f"CRITICAL: Outbox queue depth is {metrics.pending_count} "
                f"(threshold: {self._config.queue_depth_critical}). "
                "Events may be backing up!"
            )
        elif metrics.pending_count >= self._config.queue_depth_warning:
            self._logger.warning(
                f"WARNING: Outbox queue depth is {metrics.pending_count} "
                f"(threshold: {self._config.queue_depth_warning})"
            )

        # Check failure rate
        if metrics.failure_rate >= self._config.failure_rate_critical:
            self._logger.error(
                f"CRITICAL: Outbox failure rate is {metrics.failure_rate:.1%} "
                f"(threshold: {self._config.failure_rate_critical:.1%}). "
                "Check event handlers for issues!"
            )
        elif metrics.failure_rate >= self._config.failure_rate_warning:
            self._logger.warning(
                f"WARNING: Outbox failure rate is {metrics.failure_rate:.1%} "
                f"(threshold: {self._config.failure_rate_warning:.1%})"
            )

    def get_latest_metrics(self) -> Optional[OutboxMetrics]:
        """Get the most recent metrics snapshot."""
        return self._latest_metrics

    def get_metrics_history(self) -> list:
        """Get historical metrics snapshots."""
        return [m.to_dict() for m in self._metrics_history]

    def get_stats(self) -> dict:
        """Get job statistics."""
        return {
            "running": self._running,
            "latest_metrics": self._latest_metrics.to_dict() if self._latest_metrics else None,
            "history_size": len(self._metrics_history),
            "config": {
                "collection_interval_seconds": self._config.collection_interval_seconds,
                "rate_window_minutes": self._config.rate_window_minutes,
            },
        }
