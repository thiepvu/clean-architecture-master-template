"""
In-memory jobs adapter configuration.

This is the ADAPTER-specific config for in-memory jobs.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from config.types import InMemoryJobsConfigType

if TYPE_CHECKING:
    from config.jobs import JobsConfig


@dataclass
class InMemoryJobsConfig:
    """
    In-memory jobs adapter configuration.

    Simple configuration for in-memory job processing.
    Created from JobsConfig with in-memory specific defaults.
    """

    # Jobs settings (from JobsConfig)
    default_queue: str
    default_max_retries: int
    default_timeout: int

    # In-memory specific
    max_workers: int
    max_queue_size: int

    @classmethod
    def from_config(
        cls,
        jobs_config: "JobsConfig",
        max_workers: int = 4,
        max_queue_size: int = 1000,
    ) -> "InMemoryJobsConfig":
        """
        Create from JobsConfig.

        Args:
            jobs_config: Jobs common configuration
            max_workers: Maximum concurrent workers
            max_queue_size: Maximum queue size

        Returns:
            InMemoryJobsConfig instance
        """
        return cls(
            default_queue=jobs_config.JOBS_DEFAULT_QUEUE,
            default_max_retries=jobs_config.JOBS_DEFAULT_MAX_RETRIES,
            default_timeout=jobs_config.JOBS_DEFAULT_TIMEOUT,
            max_workers=max_workers,
            max_queue_size=max_queue_size,
        )

    def to_dict(self) -> InMemoryJobsConfigType:
        """Convert to typed dictionary format."""
        return InMemoryJobsConfigType(
            default_queue=self.default_queue,
            default_max_retries=self.default_max_retries,
            default_timeout=self.default_timeout,
            max_workers=self.max_workers,
            max_queue_size=self.max_queue_size,
        )
