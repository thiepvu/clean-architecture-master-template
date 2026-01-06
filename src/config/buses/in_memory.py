"""
In-memory bus adapter configuration.

This is the ADAPTER-specific config for in-memory CQRS buses.
"""

from dataclasses import dataclass

from config.types import InMemoryBusConfigType


@dataclass
class InMemoryBusConfig:
    """
    In-memory bus adapter configuration.

    Simple configuration for in-memory command/query dispatch.
    """

    max_handlers_per_command: int
    max_handlers_per_query: int

    @classmethod
    def create(
        cls,
        max_handlers_per_command: int = 1,
        max_handlers_per_query: int = 1,
    ) -> "InMemoryBusConfig":
        """
        Create with defaults.

        Args:
            max_handlers_per_command: Max handlers per command (usually 1)
            max_handlers_per_query: Max handlers per query (usually 1)

        Returns:
            InMemoryBusConfig instance
        """
        return cls(
            max_handlers_per_command=max_handlers_per_command,
            max_handlers_per_query=max_handlers_per_query,
        )

    def to_dict(self) -> InMemoryBusConfigType:
        """Convert to typed dictionary format."""
        return InMemoryBusConfigType(
            max_handlers_per_command=self.max_handlers_per_command,
            max_handlers_per_query=self.max_handlers_per_query,
        )
