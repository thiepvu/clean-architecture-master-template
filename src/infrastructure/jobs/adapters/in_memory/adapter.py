"""
In-Memory Jobs Adapter.

Implements IJobService using an in-memory queue.
Suitable for development, testing, and single-process applications.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Optional

from shared.application.ports import JobInfo, JobResult, JobStatus

if TYPE_CHECKING:
    from config.jobs import InMemoryJobsConfig
    from shared.application.ports import ILogger


@dataclass
class RegisteredTask:
    """Registered task information."""

    name: str
    func: Callable[..., Any]
    queue: str
    max_retries: int
    timeout: Optional[int]


@dataclass
class QueuedJob:
    """Job in the queue."""

    job_id: str
    task_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    queue: str
    eta: Optional[datetime] = None
    retries: int = 0
    max_retries: int = 3


@dataclass
class JobState:
    """Internal job state."""

    job_id: str
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0


class InMemoryJobAdapter:
    """
    In-memory jobs adapter implementing IJobService.

    Uses asyncio queues with worker tasks.
    Not suitable for distributed systems (no shared state).

    Example:
        adapter = InMemoryJobAdapter(config, logger)
        await adapter.initialize()

        adapter.register_task("send_email", send_email_func)
        job_id = await adapter.enqueue("send_email", to="user@example.com")
    """

    def __init__(self, config: "InMemoryJobsConfig", logger: "ILogger"):
        """
        Initialize in-memory jobs adapter.

        Args:
            config: In-memory jobs configuration
            logger: Logger instance
        """
        self._config = config
        self._logger = logger
        self._tasks: dict[str, RegisteredTask] = {}
        self._queues: dict[str, asyncio.Queue[QueuedJob]] = {}
        self._job_states: dict[str, JobState] = {}
        self._workers: list[asyncio.Task[None]] = []
        self._running = False
        self._scheduler_task: Optional[asyncio.Task[None]] = None
        self._scheduled_jobs: list[QueuedJob] = []

    async def initialize(self) -> None:
        """Initialize the job service and start workers."""
        self._logger.info("🔧 Initializing in-memory jobs adapter")

        # Create default queue
        self._queues[self._config.default_queue] = asyncio.Queue(
            maxsize=self._config.max_queue_size
        )

        # Start workers
        self._running = True
        for i in range(self._config.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)

        # Start scheduler for delayed jobs
        self._scheduler_task = asyncio.create_task(self._scheduler())

        self._logger.info(
            f"✅ In-memory jobs adapter initialized with {self._config.max_workers} workers"
        )

    async def close(self) -> None:
        """Close the job service and stop workers."""
        self._running = False

        # Cancel scheduler
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass

        # Cancel all workers
        for worker in self._workers:
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass

        self._workers.clear()
        self._queues.clear()
        self._job_states.clear()
        self._scheduled_jobs.clear()

        self._logger.info("✅ In-memory jobs adapter closed")

    async def shutdown(self, wait: bool = True) -> None:
        """Shutdown the job service gracefully (alias for close)."""
        await self.close()

    async def health_check(self) -> bool:
        """Check if job service is healthy."""
        return self._running and len(self._workers) > 0

    async def enqueue(
        self,
        task_name: str,
        *args: Any,
        queue: Optional[str] = None,
        delay: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """Enqueue a job for background execution."""
        if task_name not in self._tasks:
            raise ValueError(f"Task not registered: {task_name}")

        task = self._tasks[task_name]
        queue_name = queue or task.queue or self._config.default_queue
        job_id = str(uuid.uuid4())

        # Ensure queue exists
        if queue_name not in self._queues:
            self._queues[queue_name] = asyncio.Queue(maxsize=self._config.max_queue_size)

        job = QueuedJob(
            job_id=job_id,
            task_name=task_name,
            args=args,
            kwargs=kwargs,
            queue=queue_name,
            max_retries=task.max_retries,
        )

        self._job_states[job_id] = JobState(job_id=job_id)

        if delay:
            from datetime import timedelta

            job.eta = datetime.now() + timedelta(seconds=delay)
            self._scheduled_jobs.append(job)
            self._logger.info(f"📋 Jobs: Scheduled '{task_name}' [{job_id[:8]}] (delay={delay}s)")
        else:
            await self._queues[queue_name].put(job)
            self._logger.info(f"📋 Jobs: Enqueued '{task_name}' [{job_id[:8]}] → {queue_name}")

        return job_id

    async def enqueue_at(
        self,
        task_name: str,
        eta: datetime,
        *args: Any,
        queue: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Schedule a job for execution at a specific time."""
        if task_name not in self._tasks:
            raise ValueError(f"Task not registered: {task_name}")

        task = self._tasks[task_name]
        queue_name = queue or task.queue or self._config.default_queue
        job_id = str(uuid.uuid4())

        job = QueuedJob(
            job_id=job_id,
            task_name=task_name,
            args=args,
            kwargs=kwargs,
            queue=queue_name,
            eta=eta,
            max_retries=task.max_retries,
        )

        self._job_states[job_id] = JobState(job_id=job_id)
        self._scheduled_jobs.append(job)
        self._logger.debug(f"Job {job_id} scheduled for {eta}")

        return job_id

    async def get_result(self, job_id: str, timeout: Optional[int] = None) -> JobResult:
        """Get the result of a job."""
        if job_id not in self._job_states:
            return JobResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                error="Job not found",
            )

        state = self._job_states[job_id]

        if timeout and state.status == JobStatus.PENDING:
            # Wait for job to complete
            start = datetime.now()
            while (datetime.now() - start).seconds < timeout:
                await asyncio.sleep(0.1)
                state = self._job_states.get(job_id)
                if state and state.status not in (JobStatus.PENDING, JobStatus.RUNNING):
                    break

        return JobResult(
            job_id=job_id,
            status=state.status,
            result=state.result,
            error=state.error,
            started_at=state.started_at,
            completed_at=state.completed_at,
            retries=state.retries,
        )

    async def get_status(self, job_id: str) -> JobStatus:
        """Get the current status of a job."""
        if job_id not in self._job_states:
            return JobStatus.FAILED

        return self._job_states[job_id].status

    async def revoke(self, job_id: str, terminate: bool = False) -> bool:
        """Revoke/cancel a pending job."""
        if job_id not in self._job_states:
            return False

        state = self._job_states[job_id]

        if state.status == JobStatus.PENDING:
            state.status = JobStatus.REVOKED
            # Remove from scheduled jobs if present
            self._scheduled_jobs = [j for j in self._scheduled_jobs if j.job_id != job_id]
            return True

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
        self._tasks[name] = RegisteredTask(
            name=name,
            func=func,
            queue=queue or self._config.default_queue,
            max_retries=max_retries,
            timeout=timeout or self._config.default_timeout,
        )
        self._logger.info(f"⚙️ Jobs: Registered task '{name}' → queue={queue or 'default'}")

    async def get_registered_tasks(self) -> list[JobInfo]:
        """Get list of all registered tasks."""
        return [
            JobInfo(
                name=task.name,
                queue=task.queue,
                max_retries=task.max_retries,
                timeout=task.timeout,
            )
            for task in self._tasks.values()
        ]

    async def get_queue_length(self, queue: Optional[str] = None) -> int:
        """Get number of pending jobs in a queue."""
        queue_name = queue or self._config.default_queue

        if queue_name not in self._queues:
            return 0

        return self._queues[queue_name].qsize()

    async def purge_queue(self, queue: Optional[str] = None) -> int:
        """Remove all pending jobs from a queue."""
        queue_name = queue or self._config.default_queue

        if queue_name not in self._queues:
            return 0

        count = 0
        q = self._queues[queue_name]

        while not q.empty():
            try:
                job = q.get_nowait()
                if job.job_id in self._job_states:
                    self._job_states[job.job_id].status = JobStatus.REVOKED
                count += 1
            except asyncio.QueueEmpty:
                break

        return count

    async def _worker(self, worker_id: int) -> None:
        """Worker task that processes jobs from queues."""
        self._logger.debug(f"Worker {worker_id} started")

        while self._running:
            try:
                # Round-robin through all queues
                for queue_name, queue in self._queues.items():
                    try:
                        job = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        continue

                    await self._process_job(job, worker_id)

                # Small sleep to prevent busy loop
                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        self._logger.debug(f"Worker {worker_id} stopped")

    async def _process_job(self, job: QueuedJob, worker_id: int) -> None:
        """Process a single job."""
        state = self._job_states.get(job.job_id)
        if not state:
            return

        if state.status == JobStatus.REVOKED:
            return

        state.status = JobStatus.RUNNING
        state.started_at = datetime.now()

        task = self._tasks.get(job.task_name)
        if not task:
            state.status = JobStatus.FAILED
            state.error = f"Task not found: {job.task_name}"
            state.completed_at = datetime.now()
            return

        try:
            # Execute task with timeout
            timeout = task.timeout or self._config.default_timeout

            if asyncio.iscoroutinefunction(task.func):
                result = await asyncio.wait_for(
                    task.func(*job.args, **job.kwargs),
                    timeout=timeout,
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(task.func, *job.args, **job.kwargs),
                    timeout=timeout,
                )

            state.status = JobStatus.SUCCESS
            state.result = result
            state.completed_at = datetime.now()

            self._logger.info(
                f"✅ Jobs: Completed '{job.task_name}' [{job.job_id[:8]}] (worker={worker_id})"
            )

        except asyncio.TimeoutError:
            state.error = f"Task timed out after {timeout}s"
            await self._handle_failure(job, state, "timeout")

        except Exception as e:
            state.error = str(e)
            await self._handle_failure(job, state, str(e))

    async def _handle_failure(self, job: QueuedJob, state: JobState, error: str) -> None:
        """Handle job failure with retry logic."""
        job.retries += 1
        state.retries = job.retries

        if job.retries < job.max_retries:
            state.status = JobStatus.RETRY
            # Re-queue the job
            queue = self._queues.get(job.queue)
            if queue:
                await queue.put(job)
                self._logger.warning(
                    f"⚠️ Jobs: Retry '{job.task_name}' [{job.job_id[:8]}] "
                    f"({job.retries}/{job.max_retries}) - {error}"
                )
        else:
            state.status = JobStatus.FAILED
            state.completed_at = datetime.now()
            self._logger.error(
                f"❌ Jobs: Failed '{job.task_name}' [{job.job_id[:8]}] "
                f"after {job.retries} retries: {error}"
            )

    async def _scheduler(self) -> None:
        """Scheduler task that moves scheduled jobs to queues when due."""
        while self._running:
            try:
                now = datetime.now()
                ready_jobs = []
                remaining_jobs = []

                for job in self._scheduled_jobs:
                    if job.eta and job.eta <= now:
                        ready_jobs.append(job)
                    else:
                        remaining_jobs.append(job)

                self._scheduled_jobs = remaining_jobs

                for job in ready_jobs:
                    queue = self._queues.get(job.queue)
                    if queue:
                        await queue.put(job)
                        self._logger.debug(f"Scheduled job {job.job_id} moved to queue")

                await asyncio.sleep(1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(1)
