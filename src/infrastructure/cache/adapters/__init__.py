"""
Cache Adapters.

Available adapters:
- RedisCacheAdapter: Redis-based caching
- InMemoryCacheAdapter: In-memory caching (for development/testing)
"""

from .in_memory import InMemoryCacheAdapter
from .redis import RedisCacheAdapter

__all__ = [
    "RedisCacheAdapter",
    "InMemoryCacheAdapter",
]
