"""
Cache Factory.

Creates cache adapters based on configuration.
Supports: Redis, In-Memory
"""

from config.cache import RedisCacheConfig, RedisCacheSettings
from config.types import CacheAdapterType
from shared.application.ports import ICacheService, IConfigService, ILogger


class CacheFactory:
    """
    Factory for creating cache adapters.

    Creates and initializes the appropriate cache adapter
    based on configuration. Performs health check before returning.

    Example:
        cache = await CacheFactory.create(
            adapter_type=CacheAdapterType.REDIS,
            config_service=config_service,
            logger=logger,
        )
    """

    @staticmethod
    async def create(
        adapter_type: CacheAdapterType,
        config_service: IConfigService,
        logger: ILogger,
    ) -> ICacheService:
        """
        Create and initialize cache adapter.

        Args:
            adapter_type: Type of cache adapter to create
            config_service: ConfigService instance
            logger: Logger instance

        Returns:
            Initialized cache adapter

        Raises:
            ValueError: If adapter type is unknown
            RuntimeError: If health check fails
        """
        logger.info(f"🔧 Creating cache adapter: {adapter_type.value}")

        if adapter_type == CacheAdapterType.REDIS:
            from .adapters.redis import RedisCacheAdapter

            # Factory loads adapter-specific config from config layer
            cache_config = config_service.cache
            redis_settings = RedisCacheSettings()
            adapter_config = RedisCacheConfig.from_settings(redis_settings, cache_config)

            # Adapter only receives config and implements
            adapter = RedisCacheAdapter(adapter_config, logger)

        elif adapter_type == CacheAdapterType.IN_MEMORY:
            from .adapters.in_memory import InMemoryCacheAdapter

            adapter = InMemoryCacheAdapter(logger)

        else:
            raise ValueError(f"Unknown cache adapter type: {adapter_type}")

        # Initialize adapter
        await adapter.initialize()

        # Verify health
        if not await adapter.health_check():
            raise RuntimeError(f"Cache adapter health check failed: {adapter_type.value}")

        logger.info(f"✅ Cache adapter ready: {adapter_type.value}")
        return adapter
