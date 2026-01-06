"""
Events configuration types - Port & Adapter pattern.

Contains:
- EventBusAdapterType: Enum for adapter selection
- EventsConfigType: Common/Port interface for all event bus adapters
- InMemoryEventBusConfigType: In-memory event bus adapter config
"""

from enum import Enum
from typing import Literal, TypedDict

# =============================================================================
# Adapter Type Enum
# =============================================================================


class EventBusAdapterType(str, Enum):
    """Available event bus adapter types."""

    IN_MEMORY = "in_memory"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"


# =============================================================================
# Common/Port Type - Interface for all event bus adapters
# =============================================================================


class EventsConfigType(TypedDict):
    """
    Common events configuration type (Port interface).

    All event bus adapters must provide these base fields.
    """

    adapter: Literal["in_memory", "rabbitmq", "kafka"]


# =============================================================================
# Adapter Types - Specific configuration for each adapter
# =============================================================================


class InMemoryEventBusConfigType(TypedDict):
    """
    In-memory event bus adapter configuration type.

    Simple configuration for in-memory event publishing.
    """

    max_queue_size: int
    worker_count: int
