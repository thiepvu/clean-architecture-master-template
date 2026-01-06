"""
PostgreSQL database adapter configuration.

This is the ADAPTER-specific config for PostgreSQL.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict

from config.types import PostgresConfigType

if TYPE_CHECKING:
    from config.base import BaseConfig
    from config.database import DatabaseConfig


@dataclass
class PostgresConfig:
    """
    PostgreSQL database adapter configuration.

    Contains all settings needed to connect to PostgreSQL.
    Created from DatabaseConfig + BaseConfig.
    """

    # Connection
    url: str

    # Pool settings
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int

    # Query settings
    echo: bool
    echo_pool: bool

    # Schema mapping
    module_schemas: Dict[str, str]

    # State
    is_testing: bool

    @classmethod
    def from_configs(
        cls,
        database_config: "DatabaseConfig",
        base_config: "BaseConfig",
    ) -> "PostgresConfig":
        """
        Create from DatabaseConfig and BaseConfig.

        Args:
            database_config: Database common configuration
            base_config: Base/environment configuration

        Returns:
            PostgresConfig instance
        """
        return cls(
            url=database_config.DATABASE_URL,
            pool_size=database_config.DB_POOL_SIZE,
            max_overflow=database_config.DB_MAX_OVERFLOW,
            pool_timeout=database_config.DB_POOL_TIMEOUT,
            pool_recycle=database_config.DB_POOL_RECYCLE,
            echo=database_config.DB_ECHO,
            echo_pool=database_config.DB_ECHO_POOL,
            module_schemas=database_config.MODULE_SCHEMAS,
            is_testing=base_config.is_testing,
        )

    def to_dict(self) -> PostgresConfigType:
        """Convert to typed dictionary format."""
        return PostgresConfigType(
            url=self.url,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            echo=self.echo,
            echo_pool=self.echo_pool,
            module_schemas=self.module_schemas,
            is_testing=self.is_testing,
        )
