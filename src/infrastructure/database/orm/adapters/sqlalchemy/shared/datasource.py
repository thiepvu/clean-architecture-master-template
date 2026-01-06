"""
SQLAlchemy DataSource for scripts and CLI tools.

Provides a simple singleton-based database connection manager,
suitable for scripts, CLI tools, migrations, and testing.

For application code (FastAPI), use:
- DatabaseFactory from infrastructure.database.factory
- PostgresDatabaseAdapter from infrastructure.database.adapters.postgres

Usage (scripts/CLI):
    from infrastructure.database.orm.adapters.sqlalchemy.shared import datasource

    datasource.initialize()

    # Option 1: Use session directly
    async with datasource.session_context() as session:
        result = await session.execute(...)

    # Option 2: Use with UoW
    from infrastructure.database.orm.adapters.sqlalchemy.shared import BaseUnitOfWork
    async with BaseUnitOfWork(datasource.session_factory) as uow:
        ...

    await datasource.close()
"""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

from shared.bootstrap import create_config_service

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class DataSource:
    """
    SQLAlchemy DataSource for scripts and CLI.

    Manages engine and session factory lifecycle.
    This is a lightweight alternative to the full DatabaseAdapter
    for use in scripts, CLI tools, and migrations.
    """

    def __init__(self, logger: Optional["ILogger"] = None):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._config_service = None
        self._logger = logger

    def set_logger(self, logger: "ILogger") -> None:
        """Set logger instance (for late initialization)."""
        self._logger = logger

    def initialize(self, database_url: Optional[str] = None) -> None:
        """
        Initialize database engine and session factory.

        Args:
            database_url: Optional database URL. If not provided, uses settings.
        """
        if self._engine is not None:
            if self._logger:
                self._logger.warning("DataSource already initialized")
            return

        self._config_service = create_config_service()
        db_config = self._config_service.database
        base_config = self._config_service.base
        url = database_url or db_config.DATABASE_URL

        if self._logger:
            self._logger.info("Initializing DataSource...")
            self._logger.debug(f"Database URL: {url.split('@')[1] if '@' in url else 'masked'}")

        # Create engine with appropriate settings
        engine_kwargs = {
            "echo": db_config.DB_ECHO,
            "pool_pre_ping": True,
            "future": True,
        }

        # Use NullPool for testing, AsyncAdaptedQueuePool for production
        if base_config.is_testing:
            engine_kwargs["poolclass"] = NullPool
            if self._logger:
                self._logger.debug("Using NullPool for testing")
        else:
            engine_kwargs["poolclass"] = AsyncAdaptedQueuePool
            engine_kwargs["pool_size"] = db_config.DB_POOL_SIZE
            engine_kwargs["max_overflow"] = db_config.DB_MAX_OVERFLOW
            engine_kwargs["pool_timeout"] = 30
            engine_kwargs["pool_recycle"] = 3600
            if self._logger:
                self._logger.debug(
                    f"Using AsyncAdaptedQueuePool (size={db_config.DB_POOL_SIZE}, "
                    f"overflow={db_config.DB_MAX_OVERFLOW})"
                )

        self._engine = create_async_engine(url, **engine_kwargs)

        # Create session factory
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        if self._logger:
            self._logger.info("✓ DataSource initialized")

    async def close(self) -> None:
        """
        Close database connection.
        Should be called during shutdown.
        """
        if self._engine is None:
            if self._logger:
                self._logger.warning("DataSource not initialized, nothing to close")
            return

        if self._logger:
            self._logger.info("Closing DataSource...")
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None
        if self._logger:
            self._logger.info("✓ DataSource closed")

    @property
    def engine(self) -> AsyncEngine:
        """Get database engine."""
        if self._engine is None:
            raise RuntimeError("DataSource not initialized. Call initialize() first.")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        Get session factory for creating new sessions.

        This can be passed to UoW factories.
        """
        if self._session_factory is None:
            raise RuntimeError("DataSource not initialized. Call initialize() first.")
        return self._session_factory

    @property
    def is_initialized(self) -> bool:
        """Check if DataSource is initialized."""
        return self._engine is not None

    @asynccontextmanager
    async def session_context(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for database session.

        Usage:
            async with datasource.session_context() as session:
                result = await session.execute(...)
        """
        if self._session_factory is None:
            raise RuntimeError("DataSource not initialized. Call initialize() first.")

        async with self._session_factory() as session:
            try:
                yield session
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Session error: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()


# Global singleton instance for scripts/CLI
datasource = DataSource()


# Convenience function
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session (generator).

    Usage:
        async for session in get_session():
            result = await session.execute(...)
    """
    async with datasource.session_context() as session:
        yield session
