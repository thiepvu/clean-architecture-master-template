"""
Database Infrastructure Module.

Provides database connectivity with Port & Adapter + Factory pattern.

Adapters:
- PostgreSQL: Production-ready with SQLAlchemy async

Usage:
──────
1. DI Container Registration (Recommended):
    from infrastructure.database import DatabaseModule

    database = providers.Singleton(
        DatabaseModule.create_database,
        config_service=config_service,
        logger=logger,
    )

2. Direct Factory Usage:
    from infrastructure.database import DatabaseFactory
    from config.types import DatabaseAdapterType

    database = await DatabaseFactory.create(
        adapter_type=DatabaseAdapterType.POSTGRES,
        config_service=config_service,
        logger=logger,
    )

3. Scripts/CLI (import directly to avoid circular imports):
    from infrastructure.database.orm.adapters.sqlalchemy.shared.datasource import datasource

    datasource.initialize()
    async with datasource.session_context() as session:
        result = await session.execute(...)
    await datasource.close()

4. ORM Base Classes:
    from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import BaseModel
"""

from .adapters import PostgresDatabaseAdapter
from .database_module import DatabaseModule
from .factory import DatabaseFactory

__all__ = [
    # Module (primary interface for DI)
    "DatabaseModule",
    # Factory
    "DatabaseFactory",
    # Adapters
    "PostgresDatabaseAdapter",
]


def __getattr__(name: str):
    """Lazy load ORM components to avoid circular imports."""
    lazy_imports = {
        "BaseModel": ".orm.adapters.sqlalchemy.shared.base_model",
        "ModuleBase": ".orm.adapters.sqlalchemy.shared.base_model",
        "MODULE_BASES": ".orm.adapters.sqlalchemy.shared.base_model",
        "register_module_base": ".orm.adapters.sqlalchemy.shared.base_model",
        "get_module_base": ".orm.adapters.sqlalchemy.shared.base_model",
        "get_combined_metadata": ".orm.adapters.sqlalchemy.shared.base_model",
        "datasource": ".orm.adapters.sqlalchemy.shared.datasource",
    }

    if name in lazy_imports:
        import importlib

        module = importlib.import_module(lazy_imports[name], package=__name__)
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
