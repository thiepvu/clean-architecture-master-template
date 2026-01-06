"""
Database configuration types - Port & Adapter pattern.

Contains:
- DatabaseAdapterType: Enum for adapter selection
- DatabaseConfigType: Common/Port interface for all database adapters
- PostgresConfigType: PostgreSQL adapter specific config
"""

from enum import Enum
from typing import Dict, Literal, TypedDict

# =============================================================================
# Adapter Type Enum
# =============================================================================


class DatabaseAdapterType(str, Enum):
    """Available database adapter types."""

    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"


# =============================================================================
# Common/Port Type - Interface for all database adapters
# =============================================================================


class DatabaseConfigType(TypedDict):
    """
    Common database configuration type (Port interface).

    All database adapters must provide these base fields.
    """

    adapter: Literal["postgres", "mysql", "sqlite"]
    url: str
    echo: bool
    pool_size: int
    max_overflow: int


# =============================================================================
# Adapter Types - Specific configuration for each adapter
# =============================================================================


class PostgresConfigType(TypedDict):
    """
    PostgreSQL database adapter configuration type.

    Contains all settings needed to connect to PostgreSQL.
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
