"""
Cache Service Port (Interface).

Defines the contract for cache operations.
Implementations: RedisCacheAdapter, InMemoryCacheAdapter
"""

from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class ICacheService(Protocol):
    """
    Cache service port (interface).

    All cache adapters must implement this protocol.
    Supports async operations with health checking.

    Example:
        class RedisCacheAdapter:
            async def get(self, key: str) -> Optional[Any]:
                return await self._client.get(key)
    """

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be serialized)
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        ...

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        ...

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        ...

    async def clear(self) -> bool:
        """
        Clear all cached data.

        Returns:
            True if successful, False otherwise
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if cache service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        ...

    async def initialize(self) -> None:
        """
        Initialize the cache service.

        Called during application startup.
        Should establish connections and verify readiness.
        """
        ...

    async def close(self) -> None:
        """
        Close the cache service.

        Called during application shutdown.
        Should cleanup connections and resources.
        """
        ...
