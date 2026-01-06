"""
Alembic migration environment configuration.
This file is used by Alembic to configure migrations.
Works with multi-schema MODULE_BASES architecture.
"""

from sqlalchemy import pool, MetaData, create_engine, text
from sqlalchemy.engine import Connection
from alembic import context
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Initialize config service and logger (bootstrap level - uses helpers)
from shared.bootstrap import create_config_service, create_logger

config_service = create_config_service()
logger = create_logger(config_service=config_service)

# Import MODULE_BASES registry
from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import MODULE_BASES

# Import all context models to register them in MODULE_BASES
# This is CRUCIAL - importing models registers them
try:
    from infrastructure.database.orm.adapters.sqlalchemy.contexts.user_management.models import (
        UserModel,
        UserProfileModel,
        UserSessionModel,
    )
    logger.info("✓ Loaded user_management models")
except ImportError as e:
    logger.warning(f"⚠ Could not import user_management models: {e}")

try:
    from infrastructure.database.orm.adapters.sqlalchemy.contexts.file_management.models import (
        FileModel,
    )
    logger.info("✓ Loaded file_management models")
except ImportError as e:
    logger.warning(f"⚠ Could not import file_management models: {e}")

# Import outbox model (uses shared Base, not MODULE_BASES)
try:
    from infrastructure.database.orm.adapters.sqlalchemy.shared.outbox import (
        OutboxEventModel,
    )
    logger.info("✓ Loaded outbox models")
except ImportError as e:
    logger.warning(f"⚠ Could not import outbox models: {e}")

# Add more contexts as needed:
# try:
#     from infrastructure.database.orm.adapters.sqlalchemy.contexts.order_management.models import (
#         OrderModel,
#     )
#     logger.info("✓ Loaded order_management models")
# except ImportError as e:
#     logger.warning(f"⚠ Could not import order_management models: {e}")

# Alembic Config object
alembic_config = context.config

# Combine metadata from all registered contexts
target_metadata = MetaData()

logger.info(f"Registered contexts: {list(MODULE_BASES.keys())}")

for module_name, module_base in MODULE_BASES.items():
    tables = list(module_base.Base.metadata.tables.keys())
    logger.info(f"  {module_name}: {len(tables)} tables - {tables}")

    # Copy tables to target_metadata
    for table in module_base.Base.metadata.tables.values():
        table.to_metadata(target_metadata)

# Also include shared Base tables (e.g., outbox_events)
from infrastructure.database.orm.adapters.sqlalchemy.shared.base_model import Base as SharedBase

shared_tables = list(SharedBase.metadata.tables.keys())
logger.info(f"  shared: {len(shared_tables)} tables - {shared_tables}")

for table in SharedBase.metadata.tables.values():
    if table.name not in target_metadata.tables:  # Avoid duplicates
        table.to_metadata(target_metadata)

logger.info(f"Total tables in target_metadata: {len(target_metadata.tables)}")


def get_url() -> str:
    """
    Get database URL from ConfigService.
    Converts async URL to sync if needed.
    """
    url = config_service.database.DATABASE_URL

    # Convert async URL to sync for Alembic
    if "postgresql+asyncpg://" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        logger.info("Converted async URL to sync for Alembic")

    return url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    This configures the context with just a URL and not an Engine.
    """
    url = get_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,  # Important for multi-schema
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using sync engine.

    This uses a sync (non-async) SQLAlchemy engine which is simpler
    and avoids event loop conflicts.
    """
    url = get_url()

    # Create sync engine
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create schemas if they don't exist
        for module_name, module_base in MODULE_BASES.items():
            schema_name = module_base.schema_name
            logger.info(f"Creating schema if not exists: {schema_name}")

            connection.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            )

        connection.commit()

        # Configure and run migrations
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
