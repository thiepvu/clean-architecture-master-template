"""
Jobs Infrastructure Module.

Provides background job/task processing capabilities with Port & Adapter + Factory pattern.

Adapters:
- Redis Celery: Production-ready distributed task processing
- In-Memory: Development/testing with async workers

Usage:
──────
1. DI Container Registration (Recommended):
    from infrastructure.jobs import JobsModule

    job_service = providers.Singleton(
        JobsModule.create_jobs,
        config_service=config_service,
        logger=logger,
    )

2. Direct Factory Usage:
    from infrastructure.jobs import JobsFactory
    from config.types import JobsAdapterType

    jobs = await JobsFactory.create(
        adapter_type=JobsAdapterType.REDIS_CELERY,
        config_service=config_service,
        logger=logger,
    )

3. Register and Enqueue Tasks:
    # Register a task
    jobs.register_task("send_email", send_email_func, max_retries=3)

    # Enqueue for immediate execution
    job_id = await jobs.enqueue("send_email", to="user@example.com")

    # Schedule for later
    job_id = await jobs.enqueue("send_email", to="user@example.com", delay=60)

    # Get result
    result = await jobs.get_result(job_id, timeout=30)
"""

from .adapters import InMemoryJobAdapter, RedisCeleryJobAdapter
from .factory import JobsFactory
from .jobs_module import JobsModule

__all__ = [
    # Module (primary interface for DI)
    "JobsModule",
    # Factory
    "JobsFactory",
    # Adapters
    "RedisCeleryJobAdapter",
    "InMemoryJobAdapter",
]
