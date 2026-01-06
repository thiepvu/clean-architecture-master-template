"""
Buses (CQRS) configuration - Port & Adapter pattern.

Contains:
- BusesConfig: Common/Port configuration for bus adapters
- InMemoryBusConfig: In-memory bus adapter configuration
"""

from .buses import BusesConfig
from .in_memory import InMemoryBusConfig

__all__ = [
    # Port Config
    "BusesConfig",
    # Adapter Configs
    "InMemoryBusConfig",
]
