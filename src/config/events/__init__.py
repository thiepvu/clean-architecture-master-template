"""
Events configuration - Port & Adapter pattern.

Contains:
- EventsConfig: Common/Port config for all event bus adapters
- InMemoryEventBusConfig: In-memory event bus adapter config
"""

from .events import EventsConfig
from .in_memory import InMemoryEventBusConfig

__all__ = [
    "EventsConfig",
    "InMemoryEventBusConfig",
]
