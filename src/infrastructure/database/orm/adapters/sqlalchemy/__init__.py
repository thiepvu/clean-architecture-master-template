"""
SQLAlchemy adapter for database operations.

Contains:
- shared/: Base implementations for UoW and Repository
- contexts/: Context-specific implementations

Usage:
──────
# For ORM base classes
from infrastructure.database.orm.adapters.sqlalchemy import BaseModel, BaseRepository

# For DataSource (scripts/CLI) - import directly to avoid circular imports
from infrastructure.database.orm.adapters.sqlalchemy.shared.datasource import datasource
"""

from .shared import (
    MODULE_BASES,
    Base,
    BaseModel,
    BaseRepository,
    BaseUnitOfWork,
    BaseUnitOfWorkFactory,
    ModuleBase,
    get_combined_metadata,
    get_module_base,
    register_module_base,
)

__all__ = [
    # UoW & Repository Base
    "BaseUnitOfWork",
    "BaseUnitOfWorkFactory",
    "BaseRepository",
    # ORM Base
    "Base",
    "BaseModel",
    "ModuleBase",
    "MODULE_BASES",
    "register_module_base",
    "get_module_base",
    "get_combined_metadata",
]


def __getattr__(name: str):
    """Lazy load DataSource to avoid circular imports."""
    if name in ("DataSource", "datasource", "get_session"):
        from .shared.datasource import DataSource, datasource, get_session

        return {"DataSource": DataSource, "datasource": datasource, "get_session": get_session}[
            name
        ]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
