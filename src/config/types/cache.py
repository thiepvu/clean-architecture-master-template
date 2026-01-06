"""
Cache configuration types - Port & Adapter pattern.

Contains:
- CacheAdapterType: Enum for adapter selection
- CacheConfigType: Common/Port interface for all cache adapters
- RedisCacheConfigType: Redis adapter specific config
- InMemoryCacheConfigType: In-memory adapter specific config
"""

from enum import Enum
from typing import Literal, Optional, TypedDict

# =============================================================================
# Adapter Type Enum
# =============================================================================


class CacheAdapterType(str, Enum):
    """Available cache adapter types."""

    REDIS = "redis"
    IN_MEMORY = "in_memory"


# =============================================================================
# Common/Port Type - Interface for all cache adapters
# =============================================================================


class CacheConfigType(TypedDict):
    """
    Common cache configuration type (Port interface).

    All cache adapters must provide these base fields.
    """

    adapter: Literal["redis", "in_memory"]
    default_ttl: int
    key_prefix: str


# =============================================================================
# Adapter Types - Specific configuration for each adapter
# =============================================================================


class RedisCacheConfigType(TypedDict):
    """
    Redis cache adapter configuration type.

    Contains all settings needed to connect to Redis cache.
    """

    # Connection
    host: str
    port: int
    db: int
    password: Optional[str]
    username: Optional[str]

    # Pool settings
    max_connections: int
    socket_timeout: int
    socket_connect_timeout: int

    # SSL
    ssl: bool

    # Retry
    retry_on_timeout: bool
    max_retries: int

    # Cache settings
    default_ttl: int
    key_prefix: str

    # Computed
    url: str


class InMemoryCacheConfigType(TypedDict):
    """
    In-memory cache adapter configuration type.

    Simple configuration for in-memory caching.
    """

    # Cache settings
    default_ttl: int
    key_prefix: str

    # In-memory specific
    max_size: int
    cleanup_interval: int
