"""
PostgreSQL Database Adapter.

Implements IDatabaseAdapter using SQLAlchemy async engine.
Adapter only receives config from Factory and implements IDatabaseAdapter interface.
"""

from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

from config.database import PostgresConfig

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class PostgresDatabaseAdapter:
    """
    PostgreSQL database adapter implementing IDatabaseAdapter.

    Uses SQLAlchemy async engine for database operations.
    Supports connection pooling for production and NullPool for testing.

    Note: This adapter only receives PostgresConfig from Factory.
    It does NOT load config itself - that's the Factory's job.

    Example:
        # Factory creates config and passes to adapter
        adapter = PostgresDatabaseAdapter(config, logger)
        adapter.initialize()

        async with adapter.session_factory() as session:
            result = await session.execute(text("SELECT 1"))
    """

    def __init__(self, config: PostgresConfig, logger: "ILogger"):
        """
        Initialize PostgreSQL database adapter.

        Args:
            config: PostgreSQL configuration
            logger: Logger instance
        """
        self._config = config
        self._logger = logger
        self._engine: AsyncEngine = None
        self._session_factory: async_sessionmaker[AsyncSession] = None

    def initialize(self) -> None:
        """Initialize database engine and session factory."""
        if self._engine is not None:
            self._logger.warning("Database already initialized")
            return

        self._logger.info("🔧 Initializing PostgreSQL database adapter")

        # Build engine kwargs
        engine_kwargs = {
            "echo": self._config.echo,
            "pool_pre_ping": True,
            "future": True,
        }

        # Use NullPool for testing, AsyncAdaptedQueuePool for production
        if self._config.is_testing:
            engine_kwargs["poolclass"] = NullPool
            self._logger.debug("Using NullPool for testing")
        else:
            engine_kwargs["poolclass"] = AsyncAdaptedQueuePool
            engine_kwargs["pool_size"] = self._config.pool_size
            engine_kwargs["max_overflow"] = self._config.max_overflow
            engine_kwargs["pool_timeout"] = self._config.pool_timeout
            engine_kwargs["pool_recycle"] = self._config.pool_recycle
            self._logger.debug(
                f"Using AsyncAdaptedQueuePool (size={self._config.pool_size}, "
                f"overflow={self._config.max_overflow})"
            )

        self._engine = create_async_engine(self._config.url, **engine_kwargs)

        # Create session factory
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        self._logger.info("✅ PostgreSQL database adapter initialized")

    async def close(self) -> None:
        """Close database connection."""
        if self._engine is None:
            self._logger.warning("Database not initialized, nothing to close")
            return

        self._logger.info("Closing PostgreSQL database connection...")
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None
        self._logger.info("✅ PostgreSQL database connection closed")

    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        if self._session_factory is None:
            return False

        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            self._logger.error(f"Database health check failed: {e}")
            return False

    @property
    def engine(self) -> AsyncEngine:
        """Get database engine."""
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get session factory for creating new sessions."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._session_factory

    @property
    def is_initialized(self) -> bool:
        """Check if database is initialized."""
        return self._engine is not None
