"""
Cache configuration - Common/Port interface.

This is the PORT that defines what all cache adapters need.
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import CacheConfigType


class CacheConfig(BaseSettings):
    """
    Common cache configuration (Port interface).

    This config is used to select which adapter to use and common settings.
    Adapter-specific configs (RedisCacheConfig, InMemoryCacheConfig) extend this.

    Environment Variables:
        CACHE_ADAPTER: Cache adapter type (redis | in_memory)
        CACHE_DEFAULT_TTL: Default TTL in seconds
        CACHE_KEY_PREFIX: Prefix for all cache keys
    """

    CACHE_ADAPTER: Literal["redis", "in_memory"] = Field(
        default="in_memory",
        description="Cache adapter: redis | in_memory",
    )
    CACHE_DEFAULT_TTL: int = Field(
        default=3600,
        ge=1,
        description="Default TTL in seconds",
    )
    CACHE_KEY_PREFIX: str = Field(
        default="cache:",
        description="Prefix for all cache keys",
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def is_redis(self) -> bool:
        """Check if using Redis adapter."""
        return self.CACHE_ADAPTER == "redis"

    @property
    def is_in_memory(self) -> bool:
        """Check if using in-memory adapter."""
        return self.CACHE_ADAPTER == "in_memory"

    def to_dict(self) -> CacheConfigType:
        """Convert to typed dictionary format."""
        return CacheConfigType(
            adapter=self.CACHE_ADAPTER,
            default_ttl=self.CACHE_DEFAULT_TTL,
            key_prefix=self.CACHE_KEY_PREFIX,
        )
