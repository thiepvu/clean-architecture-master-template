"""
Cache Infrastructure Module.

Provides caching capabilities with Port & Adapter + Factory pattern.

Adapters:
- Redis: Production-ready distributed caching
- In-Memory: Development/testing with TTL support

Usage:
──────
1. DI Container Registration (Recommended):
    from infrastructure.cache import CacheModule

    cache_service = providers.Singleton(
        CacheModule.create_cache,
        config_service=config_service,
        logger=logger,
    )

2. Direct Factory Usage:
    from infrastructure.cache import CacheFactory
    from config.types import CacheAdapterType

    cache = await CacheFactory.create(
        adapter_type=CacheAdapterType.REDIS,
        config_service=config_service,
        logger=logger,
    )
"""

from .adapters import InMemoryCacheAdapter, RedisCacheAdapter
from .cache_module import CacheModule
from .factory import CacheFactory

__all__ = [
    # Module (primary interface for DI)
    "CacheModule",
    # Factory
    "CacheFactory",
    # Adapters
    "RedisCacheAdapter",
    "InMemoryCacheAdapter",
]
