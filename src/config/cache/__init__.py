"""
Cache configuration - Port & Adapter pattern.

Contains:
- CacheConfig: Common/Port config for all cache adapters
- RedisCacheSettings: Redis connection settings from environment
- RedisCacheConfig: Redis adapter specific config
- InMemoryCacheConfig: In-memory adapter specific config
"""

from .cache import CacheConfig
from .in_memory import InMemoryCacheConfig
from .redis import RedisCacheConfig, RedisCacheSettings

__all__ = [
    "CacheConfig",
    "RedisCacheSettings",
    "RedisCacheConfig",
    "InMemoryCacheConfig",
]
