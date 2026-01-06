"""
Database Adapter Port (Interface).

Defines the contract for database operations.
Implementations: PostgresDatabaseAdapter
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IDatabaseAdapter(Protocol):
    """
    Database adapter port (interface).

    All database adapters must implement this protocol.
    Provides connection management and session factory access.

    Example:
        class PostgresDatabaseAdapter:
            async def health_check(self) -> bool:
                async with self._session_factory() as session:
                    await session.execute(text("SELECT 1"))
                return True
    """

    @property
    def session_factory(self) -> Any:
        """
        Get the session factory for creating database sessions.

        Returns:
            Session factory (e.g., async_sessionmaker for SQLAlchemy)
        """
        ...

    @property
    def engine(self) -> Any:
        """
        Get the database engine.

        Returns:
            Database engine (e.g., AsyncEngine for SQLAlchemy)
        """
        ...

    @property
    def is_initialized(self) -> bool:
        """
        Check if database is initialized.

        Returns:
            True if initialized, False otherwise
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            True if healthy, False otherwise
        """
        ...

    def initialize(self) -> None:
        """
        Initialize the database connection.

        Called during application startup.
        Should create engine and session factory.
        """
        ...

    async def close(self) -> None:
        """
        Close the database connection.

        Called during application shutdown.
        Should dispose engine and cleanup resources.
        """
        ...
