"""
Buses (CQRS) configuration types - Port & Adapter pattern.

Contains:
- BusAdapterType: Enum for adapter selection
- BusesConfigType: Common/Port interface for all bus adapters
- InMemoryBusConfigType: In-memory bus adapter config
"""

from enum import Enum
from typing import Literal, TypedDict

# =============================================================================
# Adapter Type Enum
# =============================================================================


class BusAdapterType(str, Enum):
    """Available bus adapter types."""

    IN_MEMORY = "in_memory"
    REDIS = "redis"
    RABBITMQ = "rabbitmq"


# =============================================================================
# Common/Port Type - Interface for all bus adapters
# =============================================================================


class BusesConfigType(TypedDict):
    """
    Common buses configuration type (Port interface).

    All bus adapters must provide these base fields.
    """

    adapter: Literal["in_memory", "redis", "rabbitmq"]


# =============================================================================
# Adapter Types - Specific configuration for each adapter
# =============================================================================


class InMemoryBusConfigType(TypedDict):
    """
    In-memory bus adapter configuration type.

    Simple configuration for in-memory command/query dispatch.
    """

    max_handlers_per_command: int
    max_handlers_per_query: int
