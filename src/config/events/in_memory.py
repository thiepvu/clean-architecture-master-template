"""
In-memory event bus adapter configuration.

This is the ADAPTER-specific config for in-memory event bus.
"""

from dataclasses import dataclass

from config.types import InMemoryEventBusConfigType


@dataclass
class InMemoryEventBusConfig:
    """
    In-memory event bus adapter configuration.

    Simple configuration for in-memory event publishing.
    """

    max_queue_size: int
    worker_count: int

    @classmethod
    def create(
        cls,
        max_queue_size: int = 1000,
        worker_count: int = 4,
    ) -> "InMemoryEventBusConfig":
        """
        Create with defaults.

        Args:
            max_queue_size: Maximum events in queue
            worker_count: Number of worker tasks

        Returns:
            InMemoryEventBusConfig instance
        """
        return cls(
            max_queue_size=max_queue_size,
            worker_count=worker_count,
        )

    def to_dict(self) -> InMemoryEventBusConfigType:
        """Convert to typed dictionary format."""
        return InMemoryEventBusConfigType(
            max_queue_size=self.max_queue_size,
            worker_count=self.worker_count,
        )
