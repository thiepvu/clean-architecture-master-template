"""
Jobs configuration types - Port & Adapter pattern.

Contains:
- JobsAdapterType: Enum for adapter selection
- JobsConfigType: Common/Port interface for all jobs adapters
- RedisCeleryJobsConfigType: Redis Celery adapter specific config
- InMemoryJobsConfigType: In-memory adapter specific config
"""

from enum import Enum
from typing import Literal, Optional, TypedDict

# =============================================================================
# Adapter Type Enum
# =============================================================================


class JobsAdapterType(str, Enum):
    """Available jobs adapter types."""

    REDIS_CELERY = "redis_celery"
    IN_MEMORY = "in_memory"


# =============================================================================
# Common/Port Type - Interface for all jobs adapters
# =============================================================================


class JobsConfigType(TypedDict):
    """
    Common jobs configuration type (Port interface).

    All jobs adapters must provide these base fields.
    """

    adapter: Literal["redis_celery", "in_memory"]
    default_queue: str
    default_max_retries: int
    default_timeout: int


# =============================================================================
# Adapter Types - Specific configuration for each adapter
# =============================================================================


class RedisCeleryJobsConfigType(TypedDict):
    """
    Redis Celery jobs adapter configuration type.

    Contains all settings needed to connect to Redis as Celery broker/backend.
    """

    # Redis Connection (broker)
    broker_host: str
    broker_port: int
    broker_db: int
    broker_password: Optional[str]
    broker_username: Optional[str]
    broker_ssl: bool

    # Redis Connection (result backend)
    backend_host: str
    backend_port: int
    backend_db: int
    backend_password: Optional[str]
    backend_username: Optional[str]
    backend_ssl: bool

    # Celery settings
    task_serializer: str
    result_serializer: str
    accept_content: list[str]
    timezone: str
    task_track_started: bool
    task_time_limit: int
    task_soft_time_limit: int
    worker_prefetch_multiplier: int
    worker_concurrency: int
    result_expires: int

    # Jobs settings
    default_queue: str
    default_max_retries: int
    default_timeout: int

    # Computed
    broker_url: str
    backend_url: str


class InMemoryJobsConfigType(TypedDict):
    """
    In-memory jobs adapter configuration type.

    Simple configuration for in-memory job processing.
    """

    # Jobs settings
    default_queue: str
    default_max_retries: int
    default_timeout: int

    # In-memory specific
    max_workers: int
    max_queue_size: int
