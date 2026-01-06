"""
Redis cache adapter configuration.

This is the ADAPTER-specific config for Redis cache.
Includes both Redis connection settings and cache-specific settings.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import RedisCacheConfigType

if TYPE_CHECKING:
    from config.cache import CacheConfig


class RedisCacheSettings(BaseSettings):
    """
    Redis connection settings loaded from environment.

    Environment Variables:
        REDIS_HOST: Redis host
        REDIS_PORT: Redis port
        REDIS_DB: Redis database number
        REDIS_USERNAME: Redis username (Redis 6+)
        REDIS_PASSWORD: Redis password
        REDIS_MAX_CONNECTIONS: Maximum connections
        REDIS_SOCKET_TIMEOUT: Socket timeout
        REDIS_SOCKET_CONNECT_TIMEOUT: Socket connect timeout
        REDIS_SSL: Enable SSL/TLS
        REDIS_RETRY_ON_TIMEOUT: Retry on timeout
        REDIS_MAX_RETRIES: Maximum retry attempts
    """

    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    REDIS_DB: int = Field(default=0, ge=0, le=15, description="Redis database number")
    REDIS_USERNAME: Optional[str] = Field(default=None, description="Redis username")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, ge=1, description="Max connections")
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, ge=1, description="Socket timeout")
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(default=5, ge=1, description="Connect timeout")
    REDIS_SSL: bool = Field(default=False, description="Enable SSL/TLS")
    REDIS_RETRY_ON_TIMEOUT: bool = Field(default=True, description="Retry on timeout")
    REDIS_MAX_RETRIES: int = Field(default=3, ge=0, description="Max retries")

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )


@dataclass
class RedisCacheConfig:
    """
    Redis cache adapter configuration.

    Contains all settings needed to connect to Redis as a cache.
    Created from RedisCacheSettings + CacheConfig.
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

    @property
    def url(self) -> str:
        """Build Redis connection URL."""
        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        elif self.password:
            auth = f":{self.password}@"

        protocol = "rediss" if self.ssl else "redis"
        return f"{protocol}://{auth}{self.host}:{self.port}/{self.db}"

    @classmethod
    def from_settings(
        cls,
        redis_settings: RedisCacheSettings,
        cache_config: "CacheConfig",
    ) -> "RedisCacheConfig":
        """
        Create from RedisCacheSettings and CacheConfig.

        Args:
            redis_settings: Redis connection settings
            cache_config: Cache common configuration

        Returns:
            RedisCacheConfig instance
        """
        return cls(
            host=redis_settings.REDIS_HOST,
            port=redis_settings.REDIS_PORT,
            db=redis_settings.REDIS_DB,
            password=redis_settings.REDIS_PASSWORD,
            username=redis_settings.REDIS_USERNAME,
            max_connections=redis_settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=redis_settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=redis_settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            ssl=redis_settings.REDIS_SSL,
            retry_on_timeout=redis_settings.REDIS_RETRY_ON_TIMEOUT,
            max_retries=redis_settings.REDIS_MAX_RETRIES,
            default_ttl=cache_config.CACHE_DEFAULT_TTL,
            key_prefix=cache_config.CACHE_KEY_PREFIX,
        )

    def to_dict(self) -> RedisCacheConfigType:
        """Convert to typed dictionary format."""
        return RedisCacheConfigType(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            username=self.username,
            max_connections=self.max_connections,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout,
            ssl=self.ssl,
            retry_on_timeout=self.retry_on_timeout,
            max_retries=self.max_retries,
            default_ttl=self.default_ttl,
            key_prefix=self.key_prefix,
            url=self.url,
        )
