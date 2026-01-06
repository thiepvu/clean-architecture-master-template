"""
Shared SQLAlchemy implementations.

Contains:
- Base classes for UoW and Repository
- ORM Base models (BaseModel, ModuleBase)
- DataSource for scripts/CLI (import directly to avoid circular imports)

Context-specific implementations should extend these base classes.

Usage:
──────
# For ORM base classes
from infrastructure.database.orm.adapters.sqlalchemy.shared import BaseModel, BaseRepository

# For DataSource (scripts/CLI) - import directly to avoid circular imports
from infrastructure.database.orm.adapters.sqlalchemy.shared.datasource import datasource
"""

from .base_model import (
    MODULE_BASES,
    Base,
    BaseModel,
    ModuleBase,
    get_combined_metadata,
    get_module_base,
    register_module_base,
)
from .base_repository import BaseRepository
from .outbox import (
    OutboxEvent,
    OutboxEventModel,
    OutboxRepository,
    OutboxUnitOfWork,
    OutboxUnitOfWorkFactory,
)
from .unit_of_work import BaseUnitOfWork, BaseUnitOfWorkFactory

__all__ = [
    # UoW & Repository
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
    # Outbox
    "OutboxEventModel",
    "OutboxEvent",
    "OutboxRepository",
    "OutboxUnitOfWork",
    "OutboxUnitOfWorkFactory",
]


def __getattr__(name: str):
    """Lazy load DataSource to avoid circular imports."""
    if name in ("DataSource", "datasource", "get_session"):
        from .datasource import DataSource, datasource, get_session

        return {"DataSource": DataSource, "datasource": datasource, "get_session": get_session}[
            name
        ]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
