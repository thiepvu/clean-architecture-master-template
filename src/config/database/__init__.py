"""
Database configuration - Port & Adapter pattern.

Contains:
- DatabaseConfig: Common/Port config for all database adapters
- PostgresConfig: PostgreSQL adapter specific config
"""

from .database import DatabaseConfig
from .postgres import PostgresConfig

__all__ = [
    "DatabaseConfig",
    "PostgresConfig",
]
