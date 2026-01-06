"""
Redis Celery Jobs Adapter.

Implements IJobService using Celery with Redis as broker/backend.
Suitable for production distributed task processing.
"""

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Optional

from celery import Celery
from celery.result import AsyncResult

from shared.application.ports import JobInfo, JobResult, JobStatus

if TYPE_CHECKING:
    from config.jobs import RedisCeleryJobsConfig
    from shared.application.ports import ILogger


class RedisCeleryJobAdapter:
    """
    Redis Celery jobs adapter implementing IJobService.

    Uses Celery with Redis for distributed task processing.
    Supports task scheduling, retries, and result tracking.

    Note: This adapter only receives RedisCeleryJobsConfig from Factory.
    It does NOT load config itself - that's the Factory's job.

    Example:
        # Factory creates config and passes to adapter
        adapter = RedisCeleryJobAdapter(config, logger)
        await adapter.initialize()

        adapter.register_task("send_email", send_email_func)
        job_id = await adapter.enqueue("send_email", to="user@example.com")
    """

    def __init__(self, config: "RedisCeleryJobsConfig", logger: "ILogger"):
        """
        Initialize Redis Celery jobs adapter.

        Args:
            config: Redis Celery configuration
            logger: Logger instance
        """
        self._config = config
        self._logger = logger
        self._celery: Optional[Celery] = None
        self._registered_tasks: dict[str, JobInfo] = {}

    async def initialize(self) -> None:
        """Initialize Celery application."""
        self._logger.info(
            f"🔧 Initializing Redis Celery jobs adapter: {self._config.broker_host}:{self._config.broker_port}"
        )

        try:
            self._celery = Celery(
                "jobs",
                broker=self._config.broker_url,
                backend=self._config.backend_url,
            )

            # Configure Celery
            self._celery.conf.update(
                task_serializer=self._config.task_serializer,
                result_serializer=self._config.result_serializer,
                accept_content=self._config.accept_content,
                timezone=self._config.timezone,
                task_track_started=self._config.task_track_started,
                task_time_limit=self._config.task_time_limit,
                task_soft_time_limit=self._config.task_soft_time_limit,
                worker_prefetch_multiplier=self._config.worker_prefetch_multiplier,
                worker_concurrency=self._config.worker_concurrency,
                result_expires=self._config.result_expires,
                task_default_queue=self._config.default_queue,
                task_default_retry_delay=60,
                task_acks_late=True,
                task_reject_on_worker_lost=True,
            )

            self._logger.info("✅ Redis Celery jobs adapter initialized")

        except Exception as e:
            self._logger.error(f"❌ Failed to initialize Celery: {e}")
            raise

    async def close(self) -> None:
        """Close Celery connection."""
        if self._celery:
            self._celery.close()
            self._celery = None
            self._logger.info("✅ Redis Celery jobs connection closed")

    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown Celery gracefully (alias for close)."""
        await self.close()

    async def health_check(self) -> bool:
        """Check if Celery is healthy."""
        if not self._celery:
            return False

        try:
            # Try to ping the broker
            conn = self._celery.connection()
            conn.ensure_connection(max_retries=1)
            conn.release()
            return True
        except Exception as e:
            self._logger.error(f"Celery health check failed: {e}")
            return False

    async def enqueue(
        self,
        task_name: str,
        *args: Any,
        queue: Optional[str] = None,
        delay: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Enqueue a job for background execution."""
        if not self._celery:
            raise RuntimeError("Celery not initialized")

        if task_name not in self._registered_tasks:
            raise ValueError(f"Task not registered: {task_name}")

        task_info = self._registered_tasks[task_name]
        queue_name = queue or task_info.queue

        options: dict[str, Any] = {
            "queue": queue_name,
            "retry": True,
            "max_retries": task_info.max_retries,
        }

        if delay:
            options["countdown"] = delay

        if task_info.timeout:
            options["time_limit"] = task_info.timeout

        result: AsyncResult = self._celery.send_task(
            task_name,
            args=args,
            kwargs=kwargs,
            **options,
        )

        self._logger.debug(f"Job {result.id} enqueued to {queue_name}")
        return result.id

    async def enqueue_at(
        self,
        task_name: str,
        eta: datetime,
        *args: Any,
        queue: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Schedule a job for execution at a specific time."""
        if not self._celery:
            raise RuntimeError("Celery not initialized")

        if task_name not in self._registered_tasks:
            raise ValueError(f"Task not registered: {task_name}")

        task_info = self._registered_tasks[task_name]
        queue_name = queue or task_info.queue

        options: dict[str, Any] = {
            "queue": queue_name,
            "eta": eta,
            "retry": True,
            "max_retries": task_info.max_retries,
        }

        if task_info.timeout:
            options["time_limit"] = task_info.timeout

        result: AsyncResult = self._celery.send_task(
            task_name,
            args=args,
            kwargs=kwargs,
            **options,
        )

        self._logger.debug(f"Job {result.id} scheduled for {eta}")
        return result.id

    async def get_result(self, job_id: str, timeout: Optional[int] = None) -> JobResult:
        """Get the result of a job."""
        if not self._celery:
            return JobResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                error="Celery not initialized",
            )

        result = AsyncResult(job_id, app=self._celery)

        if timeout:
            try:
                # Wait for result with timeout
                value = await asyncio.to_thread(result.get, timeout=timeout)
                return JobResult(
                    job_id=job_id,
                    status=JobStatus.SUCCESS,
                    result=value,
                    completed_at=result.date_done,
                )
            except Exception as e:
                if result.failed():
                    return JobResult(
                        job_id=job_id,
                        status=JobStatus.FAILED,
                        error=str(result.result),
                        completed_at=result.date_done,
                    )
                return JobResult(
                    job_id=job_id,
                    status=self._map_celery_status(result.status),
                    error=str(e),
                )

        return JobResult(
            job_id=job_id,
            status=self._map_celery_status(result.status),
            result=result.result if result.successful() else None,
            error=str(result.result) if result.failed() else None,
            completed_at=result.date_done,
        )

    async def get_status(self, job_id: str) -> JobStatus:
        """Get the current status of a job."""
        if not self._celery:
            return JobStatus.FAILED

        result = AsyncResult(job_id, app=self._celery)
        return self._map_celery_status(result.status)

    async def revoke(self, job_id: str, terminate: bool = False) -> bool:
        """Revoke/cancel a pending or running job."""
        if not self._celery:
            return False

        try:
            self._celery.control.revoke(job_id, terminate=terminate)
            self._logger.debug(f"Job {job_id} revoked (terminate={terminate})")
            return True
        except Exception as e:
            self._logger.error(f"Failed to revoke job {job_id}: {e}")
            return False

    def register_task(
        self,
        name: str,
        func: Callable[..., Any],
        queue: Optional[str] = None,
        max_retries: int = 3,
        timeout: Optional[int] = None,
    ) -> None:
        """Register a task function."""
        if not self._celery:
            raise RuntimeError("Celery not initialized")

        queue_name = queue or self._config.default_queue
        task_timeout = timeout or self._config.default_timeout

        # Register task with Celery
        task_options = {
            "name": name,
            "bind": False,
            "max_retries": max_retries,
            "default_retry_delay": 60,
            "autoretry_for": (Exception,),
            "retry_backoff": True,
            "retry_backoff_max": 600,
            "retry_jitter": True,
        }

        if task_timeout:
            task_options["time_limit"] = task_timeout
            task_options["soft_time_limit"] = int(task_timeout * 0.9)

        self._celery.task(**task_options)(func)

        # Store task info
        self._registered_tasks[name] = JobInfo(
            name=name,
            queue=queue_name,
            max_retries=max_retries,
            timeout=task_timeout,
        )

        self._logger.debug(f"Task registered: {name}")

    async def get_registered_tasks(self) -> list[JobInfo]:
        """Get list of all registered tasks."""
        return list(self._registered_tasks.values())

    async def get_queue_length(self, queue: Optional[str] = None) -> int:
        """Get number of pending jobs in a queue."""
        if not self._celery:
            return 0

        queue_name = queue or self._config.default_queue

        try:
            with self._celery.pool.acquire(block=True) as conn:
                return conn.default_channel.client.llen(queue_name)
        except Exception as e:
            self._logger.error(f"Failed to get queue length: {e}")
            return 0

    async def purge_queue(self, queue: Optional[str] = None) -> int:
        """Remove all pending jobs from a queue."""
        if not self._celery:
            return 0

        queue_name = queue or self._config.default_queue

        try:
            count = self._celery.control.purge()
            self._logger.info(f"Purged {count} jobs from queue {queue_name}")
            return count or 0
        except Exception as e:
            self._logger.error(f"Failed to purge queue: {e}")
            return 0

    @property
    def celery_app(self) -> Optional[Celery]:
        """Get the underlying Celery app for advanced usage."""
        return self._celery

    def _map_celery_status(self, celery_status: str) -> JobStatus:
        """Map Celery status to JobStatus."""
        status_map = {
            "PENDING": JobStatus.PENDING,
            "STARTED": JobStatus.RUNNING,
            "SUCCESS": JobStatus.SUCCESS,
            "FAILURE": JobStatus.FAILED,
            "REVOKED": JobStatus.REVOKED,
            "RETRY": JobStatus.RETRY,
            "RECEIVED": JobStatus.PENDING,
        }
        return status_map.get(celery_status, JobStatus.PENDING)
