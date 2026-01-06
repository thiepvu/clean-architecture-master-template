"""
Event Bus Adapters.

Available adapters:
- InMemoryEventBusAdapter: In-memory event bus (for single-process apps)
"""

from .in_memory import InMemoryEventBusAdapter

__all__ = [
    "InMemoryEventBusAdapter",
]
