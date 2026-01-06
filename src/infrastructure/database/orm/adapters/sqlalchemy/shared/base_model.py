"""
SQLAlchemy Base Models and Declarative Base.

All ORM models should inherit from BaseModel.
Supports multi-schema modular architecture.

Usage (single schema):
    from infrastructure.database.orm.adapters.sqlalchemy.shared import BaseModel

    class UserModel(BaseModel):
        __tablename__ = "users"
        email = Column(String(255), unique=True)

Usage (multi-schema):
    from infrastructure.database.orm.adapters.sqlalchemy.shared import register_module_base

    module_base = register_module_base("user", "user_schema")

    class UserModel(module_base.BaseModel):
        __tablename__ = "users"
        email = Column(String(255), unique=True)
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Type

from sqlalchemy import Boolean, Column, DateTime, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


class ModuleBase:
    """
    Container for module's declarative base and schema info.
    Each module gets its own Base with associated schema.
    """

    def __init__(self, module_name: str, schema_name: str):
        self.module_name = module_name
        self.schema_name = schema_name

        # Create declarative base for this module
        self.Base = declarative_base()

        # Set schema for all tables in this module
        self.Base.metadata.schema = schema_name

        # Create BaseModel for this module
        self.BaseModel = self._create_base_model()

    def _create_base_model(self):
        """Create BaseModel class for this module."""

        class BaseModel(self.Base):
            """
            Base model with common fields for all entities.
            Provides: id, created_at, updated_at, is_deleted
            """

            __abstract__ = True

            id = Column(
                UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                nullable=False,
                comment="Primary key UUID",
            )

            created_at = Column(
                DateTime,
                default=datetime.utcnow,
                nullable=False,
                comment="Record creation timestamp",
            )

            updated_at = Column(
                DateTime,
                default=datetime.utcnow,
                onupdate=datetime.utcnow,
                nullable=False,
                comment="Record last update timestamp",
            )

            is_deleted = Column(
                Boolean,
                default=False,
                nullable=False,
                index=True,
                comment="Soft delete flag",
            )

            def __repr__(self) -> str:
                """String representation of model."""
                return f"<{self.__class__.__name__}(id={self.id})>"

            def soft_delete(self):
                """Mark record as deleted (soft delete)."""
                self.is_deleted = True

            def restore(self):
                """Restore soft-deleted record."""
                self.is_deleted = False

        return BaseModel


# Global registry of module bases
MODULE_BASES: Dict[str, ModuleBase] = {}

# =============================================================================
# Default Schema Registry
# =============================================================================
# This provides default schema mappings so ORM models can be defined
# without needing to call get_config_service() at module level.
#
# These defaults match the DatabaseConfig.MODULE_SCHEMAS defaults.
# If you need to override, call configure_schemas() before importing models.
# =============================================================================

DEFAULT_MODULE_SCHEMAS: Dict[str, str] = {
    "user": "user_schema",
    "file": "file_schema",
}

# Active schema registry (can be overridden via configure_schemas)
_schema_registry: Dict[str, str] = DEFAULT_MODULE_SCHEMAS.copy()


def configure_schemas(schemas: Dict[str, str]) -> None:
    """
    Configure schema registry with custom mappings.

    Call this at app startup BEFORE importing ORM models if you need
    to override the default schema mappings.

    Args:
        schemas: Dict mapping module names to schema names

    Example:
        from infrastructure.database.orm.adapters.sqlalchemy.shared import configure_schemas

        # At app startup (before importing models)
        configure_schemas({
            "user": "custom_user_schema",
            "file": "custom_file_schema",
        })
    """
    global _schema_registry
    _schema_registry = schemas.copy()


def get_schema_for_module(module_name: str) -> str:
    """
    Get schema name for a module from registry.

    Args:
        module_name: Name of the module

    Returns:
        Schema name

    Raises:
        KeyError: If module not in registry
    """
    if module_name not in _schema_registry:
        raise KeyError(
            f"Module '{module_name}' not in schema registry. "
            f"Available: {list(_schema_registry.keys())}"
        )
    return _schema_registry[module_name]


def register_module_base(module_name: str, schema_name: Optional[str] = None) -> ModuleBase:
    """
    Register a module and get its Base and BaseModel.

    This function should be called at the top of each module's models.py file.
    If schema_name is not provided, it will be looked up from the schema registry.

    Args:
        module_name: Name of the module (e.g., "user", "file")
        schema_name: Optional. PostgreSQL schema name. If not provided,
                     uses default from schema registry.

    Returns:
        ModuleBase: Container with Base and BaseModel for defining models

    Example:
        # Using default schema from registry (RECOMMENDED)
        module_base = register_module_base("user")

        # Or with explicit schema (for custom setups)
        module_base = register_module_base("user", "custom_user_schema")

        class UserModel(module_base.BaseModel):
            __tablename__ = "users"
            email = Column(String(255), unique=True, nullable=False)
    """
    # Use provided schema or look up from registry
    if schema_name is None:
        schema_name = get_schema_for_module(module_name)

    if module_name not in MODULE_BASES:
        MODULE_BASES[module_name] = ModuleBase(module_name, schema_name)

    return MODULE_BASES[module_name]


def get_module_base(module_name: str) -> ModuleBase:
    """
    Get the ModuleBase for a module.

    Args:
        module_name: Name of the module

    Returns:
        ModuleBase: The module's base

    Raises:
        KeyError: If module not registered
    """
    if module_name not in MODULE_BASES:
        raise KeyError(f"Module '{module_name}' not registered. Call register_module_base() first.")
    return MODULE_BASES[module_name]


def get_combined_metadata() -> MetaData:
    """
    Get combined metadata from all registered contexts.
    Used by Alembic for migrations.

    Returns:
        MetaData: Combined metadata containing all tables from all contexts
    """
    combined = MetaData()

    for module_name, module_base in MODULE_BASES.items():
        for table in module_base.Base.metadata.tables.values():
            table.to_metadata(combined)

    return combined


# ============================================================================
# Default Base (single schema, backward compatibility)
# ============================================================================

Base: Any = declarative_base()


class BaseModel(Base):  # type: ignore[valid-type, misc]
    """
    Default BaseModel (single schema).

    For multi-schema setup, use register_module_base() instead.
    """

    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Primary key UUID",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Record creation timestamp",
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Record last update timestamp",
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Soft delete flag",
    )

    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def soft_delete(self):
        """Mark record as deleted (soft delete)."""
        self.is_deleted = True

    def restore(self):
        """Restore soft-deleted record."""
        self.is_deleted = False
