"""
Database configuration - Common/Port interface.

This is the PORT that defines what all database adapters need.
"""

from typing import Dict, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.types import DatabaseConfigType


class DatabaseConfig(BaseSettings):
    """
    Common database configuration (Port interface).

    This config is used to select which adapter to use and common settings.
    Adapter-specific configs (PostgresConfig, etc.) extend this.

    Environment Variables:
        DATABASE_ADAPTER: Database adapter type (postgres | mysql | sqlite)
        DATABASE_URL: Database connection URL
        DB_POOL_SIZE: Connection pool size
        DB_MAX_OVERFLOW: Max overflow connections
        DB_POOL_TIMEOUT: Pool connection timeout
        DB_POOL_RECYCLE: Pool recycle time
        DB_ECHO: Echo SQL queries
        DB_ECHO_POOL: Echo pool events
        MODULE_SCHEMAS: Schema mapping for modules
    """

    DATABASE_ADAPTER: Literal["postgres", "mysql", "sqlite"] = Field(
        default="postgres",
        description="Database adapter: postgres | mysql | sqlite",
    )
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/modular_db",
        description="Database connection URL",
    )
    DB_POOL_SIZE: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Connection pool size",
    )
    DB_MAX_OVERFLOW: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Max overflow connections",
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        ge=1,
        description="Pool connection timeout in seconds",
    )
    DB_POOL_RECYCLE: int = Field(
        default=3600,
        ge=0,
        description="Pool recycle time in seconds",
    )
    DB_ECHO: bool = Field(
        default=False,
        description="Echo SQL queries to console",
    )
    DB_ECHO_POOL: bool = Field(
        default=False,
        description="Echo pool events to console",
    )
    MODULE_SCHEMAS: Dict[str, str] = Field(
        default={"user": "user_schema", "file": "file_schema"},
        description="Schema mapping for modules",
    )
    ALEMBIC_CONFIG: str = Field(
        default="alembic.ini",
        description="Alembic configuration file",
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        if "postgresql" in v and "asyncpg" not in v:
            raise ValueError("Use asyncpg driver for PostgreSQL: postgresql+asyncpg://...")
        return v

    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL adapter."""
        return self.DATABASE_ADAPTER == "postgres"

    @property
    def is_mysql(self) -> bool:
        """Check if using MySQL adapter."""
        return self.DATABASE_ADAPTER == "mysql"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite adapter."""
        return self.DATABASE_ADAPTER == "sqlite"

    def to_dict(self) -> DatabaseConfigType:
        """Convert to typed dictionary format."""
        return DatabaseConfigType(
            adapter=self.DATABASE_ADAPTER,
            url=self.DATABASE_URL,
            echo=self.DB_ECHO,
            pool_size=self.DB_POOL_SIZE,
            max_overflow=self.DB_MAX_OVERFLOW,
        )
