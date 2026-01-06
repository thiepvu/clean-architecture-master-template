"""
Job Service Port (Interface).

Defines the contract for background job/task operations.
Implementations: InMemoryJobAdapter, RedisCeleryJobAdapter
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, Protocol, runtime_checkable


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    REVOKED = "revoked"
    RETRY = "retry"


@dataclass
class JobResult:
    """Result of a job execution."""

    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0


@dataclass
class JobInfo:
    """Information about a registered job."""

    name: str
    queue: str
    max_retries: int
    timeout: Optional[int] = None


@runtime_checkable
class IJobService(Protocol):
    """
    Job service port (interface).

    All job adapters must implement this protocol.
    Supports async operations with health checking.

    Example:
        class RedisCeleryJobAdapter:
            async def enqueue(
                self,
                task_name: str,
                *args,
                **kwargs
            ) -> str:
                result = celery_app.send_task(task_name, args=args, kwargs=kwargs)
                return result.id
    """

    async def enqueue(
        self,
        task_name: str,
        *args: Any,
        queue: Optional[str] = None,
        delay: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        Enqueue a job for background execution.

        Args:
            task_name: Name of the registered task
            *args: Positional arguments for the task
            queue: Target queue name (optional, uses default if not specified)
            delay: Delay in seconds before execution (optional)
            **kwargs: Keyword arguments for the task

        Returns:
            Job ID for tracking

        Raises:
            ValueError: If task_name is not registered
        """
        ...

    async def enqueue_at(
        self,
        task_name: str,
        eta: datetime,
        *args: Any,
        queue: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Schedule a job for execution at a specific time.

        Args:
            task_name: Name of the registered task
            eta: Estimated time of arrival (when to execute)
            *args: Positional arguments for the task
            queue: Target queue name (optional)
            **kwargs: Keyword arguments for the task

        Returns:
            Job ID for tracking
        """
        ...

    async def get_result(self, job_id: str, timeout: Optional[int] = None) -> JobResult:
        """
        Get the result of a job.

        Args:
            job_id: Job ID returned from enqueue
            timeout: Max seconds to wait for result (None = don't wait)

        Returns:
            JobResult with status and result/error
        """
        ...

    async def get_status(self, job_id: str) -> JobStatus:
        """
        Get the current status of a job.

        Args:
            job_id: Job ID returned from enqueue

        Returns:
            Current job status
        """
        ...

    async def revoke(self, job_id: str, terminate: bool = False) -> bool:
        """
        Revoke/cancel a pending or running job.

        Args:
            job_id: Job ID to revoke
            terminate: If True, terminate running job (SIGTERM)

        Returns:
            True if revoked successfully, False otherwise
        """
        ...

    def register_task(
        self,
        name: str,
        func: Callable[..., Any],
        queue: Optional[str] = None,
        max_retries: int = 3,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Register a task function.

        Args:
            name: Unique task name
            func: Task function to execute
            queue: Default queue for this task
            max_retries: Max retry attempts on failure
            timeout: Task timeout in seconds
        """
        ...

    async def get_registered_tasks(self) -> list[JobInfo]:
        """
        Get list of all registered tasks.

        Returns:
            List of JobInfo for registered tasks
        """
        ...

    async def get_queue_length(self, queue: Optional[str] = None) -> int:
        """
        Get number of pending jobs in a queue.

        Args:
            queue: Queue name (None for default queue)

        Returns:
            Number of pending jobs
        """
        ...

    async def purge_queue(self, queue: Optional[str] = None) -> int:
        """
        Remove all pending jobs from a queue.

        Args:
            queue: Queue name (None for default queue)

        Returns:
            Number of jobs purged
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if job service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        ...

    async def initialize(self) -> None:
        """
        Initialize the job service.

        Called during application startup.
        Should establish connections and verify readiness.
        """
        ...

    async def close(self) -> None:
        """
        Close the job service.

        Called during application shutdown.
        Should cleanup connections, cancel pending jobs if needed.
        """
        ...

    async def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the job service gracefully.

        Args:
            wait: If True, wait for pending jobs to complete

        Called during application shutdown.
        Alias for close() with optional wait behavior.
        """
        ...
