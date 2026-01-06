"""
CacheModule - Pure Cache Composer.

This module is responsible ONLY for composing cache instances.
It does NOT manage singleton instances - that's the DI container's job.

Architecture:
─────────────
┌─────────────────┐
│   CacheModule   │  ← Pure Composer
│  - load config  │     Load CacheConfig from ConfigService
│  - call factory │     Pass config to CacheFactory
└────────┬────────┘
         │ create_cache()
         ▼
┌─────────────────┐
│  CacheFactory   │  ← Adapter Switcher
│  - read adapter │     Read adapter type from config
│  - create adapt │     Create adapter
│  - init + check │     Init + health check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ICacheService  │  ← Cache instance
└────────┬────────┘
         │ registered as Singleton
         ▼
┌─────────────────┐
│  DI Container   │  ← Manages lifecycle
└─────────────────┘

Usage:
──────
1. DI Container Registration:
   cache_service = providers.Singleton(
       CacheModule.create_cache,
       config_service=config_service,
       logger=logger,
   )

2. Application Layer (via DI injection):
   class MyService:
       def __init__(self, cache: ICacheService):
           self._cache = cache
"""

from config.types import CacheAdapterType
from shared.application.ports import ICacheService, IConfigService, ILogger

from .factory import CacheFactory


class CacheModule:
    """
    Pure Cache Composer.

    Responsibilities:
    - Load CacheConfig from ConfigService
    - Read adapter type from config
    - Pass to CacheFactory
    - Return cache instance to DI

    NOT responsible for:
    - Creating adapter (factory does this)
    - Init/health check (factory does this)
    - Singleton management (DI container does this)
    """

    @staticmethod
    async def create_cache(
        config_service: IConfigService,
        logger: ILogger,
    ) -> ICacheService:
        """
        Create and return cache instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Args:
            config_service: ConfigService instance (from DI)
            logger: Logger instance (from DI)

        Returns:
            ICacheService instance
        """
        # Load cache config from ConfigService
        cache_config = config_service.cache

        # Read adapter type from config
        adapter_type = CacheAdapterType(cache_config.CACHE_ADAPTER)

        # Delegate to factory
        return await CacheFactory.create(
            adapter_type=adapter_type,
            config_service=config_service,
            logger=logger,
        )
