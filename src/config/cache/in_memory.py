"""
In-memory cache adapter configuration.

This is the ADAPTER-specific config for in-memory cache.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from config.types import InMemoryCacheConfigType

if TYPE_CHECKING:
    from config.cache import CacheConfig


@dataclass
class InMemoryCacheConfig:
    """
    In-memory cache adapter configuration.

    Simple configuration for in-memory caching.
    Created from CacheConfig with in-memory specific defaults.
    """

    # Cache settings (from CacheConfig)
    default_ttl: int
    key_prefix: str

    # In-memory specific
    max_size: int
    cleanup_interval: int

    @classmethod
    def from_config(
        cls,
        cache_config: "CacheConfig",
        max_size: int = 10000,
        cleanup_interval: int = 60,
    ) -> "InMemoryCacheConfig":
        """
        Create from CacheConfig.

        Args:
            cache_config: Cache common configuration
            max_size: Maximum number of items to cache
            cleanup_interval: Seconds between cleanup cycles

        Returns:
            InMemoryCacheConfig instance
        """
        return cls(
            default_ttl=cache_config.CACHE_DEFAULT_TTL,
            key_prefix=cache_config.CACHE_KEY_PREFIX,
            max_size=max_size,
            cleanup_interval=cleanup_interval,
        )

    def to_dict(self) -> InMemoryCacheConfigType:
        """Convert to typed dictionary format."""
        return InMemoryCacheConfigType(
            default_ttl=self.default_ttl,
            key_prefix=self.key_prefix,
            max_size=self.max_size,
            cleanup_interval=self.cleanup_interval,
        )
