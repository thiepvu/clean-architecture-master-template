"""
In-Memory Cache Adapter.

Implements ICacheService using an in-memory dictionary.
Suitable for development, testing, and single-process applications.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from shared.application.ports import ILogger


@dataclass
class CacheEntry:
    """Cache entry with value and expiration."""

    value: Any
    expires_at: float  # Unix timestamp


class InMemoryCacheAdapter:
    """
    In-memory cache adapter implementing ICacheService.

    Uses a dictionary with TTL support.
    Not suitable for distributed systems (no shared state).

    Example:
        adapter = InMemoryCacheAdapter(logger)
        await adapter.initialize()

        await adapter.set("key", {"data": "value"}, ttl=3600)
        value = await adapter.get("key")
    """

    def __init__(self, logger: "ILogger"):
        """
        Initialize in-memory cache adapter.

        Args:
            logger: Logger instance
        """
        self._logger = logger
        self._cache: Dict[str, CacheEntry] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval: int = 60  # seconds

    async def initialize(self) -> None:
        """Initialize the cache and start cleanup task."""
        self._logger.info("🔧 Initializing in-memory cache adapter")
        self._cache.clear()

        # Start background cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())
        self._logger.info("✅ In-memory cache adapter initialized")

    async def close(self) -> None:
        """Close the cache and stop cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

        self._cache.clear()
        self._logger.info("✅ In-memory cache closed")

    async def health_check(self) -> bool:
        """Check if cache is healthy (always true for in-memory)."""
        return True

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self._cache.get(key)

        if entry is None:
            self._logger.debug(f"🔍 Cache: MISS {key}")
            return None

        # Check if expired
        if entry.expires_at < time.time():
            del self._cache[key]
            self._logger.debug(f"🔍 Cache: EXPIRED {key}")
            return None

        self._logger.debug(f"🔍 Cache: HIT {key}")
        return entry.value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache."""
        try:
            expires_at = time.time() + ttl
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
            self._logger.debug(f"💾 Cache: SET {key} (ttl={ttl}s)")
            return True
        except Exception as e:
            self._logger.error(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if key in self._cache:
                del self._cache[key]
                self._logger.debug(f"🗑️ Cache: DELETE {key}")
            return True
        except Exception as e:
            self._logger.error(f"Error deleting from cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        entry = self._cache.get(key)
        if entry is None:
            return False

        # Check if expired
        if entry.expires_at < time.time():
            del self._cache[key]
            return False

        return True

    async def clear(self) -> bool:
        """Clear all cached data."""
        try:
            self._cache.clear()
            self._logger.info("Cache cleared")
            return True
        except Exception as e:
            self._logger.error(f"Error clearing cache: {e}")
            return False

    async def _cleanup_expired(self) -> None:
        """Background task to cleanup expired entries."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)

                current_time = time.time()
                expired_keys = [
                    key for key, entry in self._cache.items() if entry.expires_at < current_time
                ]

                for key in expired_keys:
                    del self._cache[key]

                if expired_keys:
                    self._logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in cache cleanup: {e}")

    @property
    def size(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)
