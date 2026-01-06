"""
Redis Cache Adapter.

Implements ICacheService using Redis as the backend.
Adapter only receives config from Factory and implements ICacheService interface.
"""

import json
from typing import TYPE_CHECKING, Any, Optional

from redis import asyncio as aioredis

from config.cache import RedisCacheConfig

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class RedisCacheAdapter:
    """
    Redis cache adapter implementing ICacheService.

    Uses aioredis for async Redis operations.
    Supports JSON serialization for complex values.

    Note: This adapter only receives RedisCacheConfig from Factory.
    It does NOT load config itself - that's the Factory's job.

    Example:
        # Factory creates config and passes to adapter
        adapter = RedisCacheAdapter(config, logger)
        await adapter.initialize()

        await adapter.set("key", {"data": "value"}, ttl=3600)
        value = await adapter.get("key")
    """

    def __init__(self, config: RedisCacheConfig, logger: "ILogger"):
        """
        Initialize Redis cache adapter.

        Args:
            config: Redis configuration
            logger: Logger instance
        """
        self._config = config
        self._logger = logger
        self._client: Optional[aioredis.Redis] = None

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        self._logger.info(
            f"🔧 Initializing Redis cache adapter: {self._config.host}:{self._config.port}"
        )

        try:
            self._client = await aioredis.from_url(
                self._config.url,
                password=self._config.password,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self._client.ping()
            self._logger.info("✅ Redis cache adapter initialized")
        except Exception as e:
            self._logger.error(f"❌ Failed to initialize Redis: {e}")
            raise

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            self._logger.info("✅ Redis cache connection closed")

    async def health_check(self) -> bool:
        """Check if Redis is healthy."""
        if not self._client:
            return False

        try:
            await self._client.ping()
            return True
        except Exception as e:
            self._logger.error(f"Redis health check failed: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._client:
            return None

        try:
            value = await self._client.get(key)
            if value:
                self._logger.debug(f"🔍 Redis: HIT {key}")
                return json.loads(value)
            self._logger.debug(f"🔍 Redis: MISS {key}")
            return None
        except json.JSONDecodeError:
            # Return raw value if not JSON
            self._logger.debug(f"🔍 Redis: HIT {key} (raw)")
            return value
        except Exception as e:
            self._logger.error(f"Error getting from cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache."""
        if not self._client:
            return False

        try:
            serialized = json.dumps(value)
            await self._client.setex(key, ttl, serialized)
            self._logger.debug(f"💾 Redis: SET {key} (ttl={ttl}s)")
            return True
        except Exception as e:
            self._logger.error(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._client:
            return False

        try:
            await self._client.delete(key)
            self._logger.debug(f"🗑️ Redis: DELETE {key}")
            return True
        except Exception as e:
            self._logger.error(f"Error deleting from cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._client:
            return False

        try:
            return await self._client.exists(key) > 0
        except Exception as e:
            self._logger.error(f"Error checking cache existence: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cached data."""
        if not self._client:
            return False

        try:
            await self._client.flushdb()
            self._logger.info("Cache cleared")
            return True
        except Exception as e:
            self._logger.error(f"Error clearing cache: {e}")
            return False
