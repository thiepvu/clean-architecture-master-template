"""
Jobs configuration - Common/Port interface.

This is the PORT that defines what all jobs adapters need.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import JobsConfigType


class JobsConfig(BaseSettings):
    """
    Common jobs configuration (Port interface).

    This config is used to select which adapter to use and common settings.
    Adapter-specific configs (RedisCeleryJobsConfig, InMemoryJobsConfig) extend this.

    Environment Variables:
        JOBS_ADAPTER: Jobs adapter type (redis_celery | in_memory)
        JOBS_DEFAULT_QUEUE: Default queue name for jobs
        JOBS_DEFAULT_MAX_RETRIES: Default max retry attempts
        JOBS_DEFAULT_TIMEOUT: Default job timeout in seconds
    """

    JOBS_ADAPTER: Literal["redis_celery", "in_memory"] = Field(
        default="in_memory",
        description="Jobs adapter: redis_celery | in_memory",
    )
    JOBS_DEFAULT_QUEUE: str = Field(
        default="default",
        description="Default queue name for jobs",
    )
    JOBS_DEFAULT_MAX_RETRIES: int = Field(
        default=3,
        ge=0,
        description="Default max retry attempts",
    )
    JOBS_DEFAULT_TIMEOUT: int = Field(
        default=300,
        ge=1,
        description="Default job timeout in seconds",
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def is_redis_celery(self) -> bool:
        """Check if using Redis Celery adapter."""
        return self.JOBS_ADAPTER == "redis_celery"

    @property
    def is_in_memory(self) -> bool:
        """Check if using in-memory adapter."""
        return self.JOBS_ADAPTER == "in_memory"

    def to_dict(self) -> JobsConfigType:
        """Convert to typed dictionary format."""
        return JobsConfigType(
            adapter=self.JOBS_ADAPTER,
            default_queue=self.JOBS_DEFAULT_QUEUE,
            default_max_retries=self.JOBS_DEFAULT_MAX_RETRIES,
            default_timeout=self.JOBS_DEFAULT_TIMEOUT,
        )
