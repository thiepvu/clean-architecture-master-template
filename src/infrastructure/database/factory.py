"""
Database Factory.

Creates database adapters based on configuration.
Supports: PostgreSQL (MySQL, SQLite planned for future)
"""

from config.database import PostgresConfig
from config.types import DatabaseAdapterType
from shared.application.ports import IConfigService, IDatabaseAdapter, ILogger


class DatabaseFactory:
    """
    Factory for creating database adapters.

    Creates and initializes the appropriate database adapter
    based on configuration. Performs health check before returning.

    Example:
        database = await DatabaseFactory.create(
            adapter_type=DatabaseAdapterType.POSTGRES,
            config_service=config_service,
            logger=logger,
        )
    """

    @staticmethod
    async def create(
        adapter_type: DatabaseAdapterType,
        config_service: IConfigService,
        logger: ILogger,
    ) -> IDatabaseAdapter:
        """
        Create and initialize database adapter.

        Args:
            adapter_type: Type of database adapter to create
            config_service: ConfigService instance
            logger: Logger instance

        Returns:
            Initialized database adapter

        Raises:
            ValueError: If adapter type is unknown
            RuntimeError: If health check fails
        """
        logger.info(f"🔧 Creating database adapter: {adapter_type.value}")

        if adapter_type == DatabaseAdapterType.POSTGRES:
            from .adapters.postgres import PostgresDatabaseAdapter

            # Factory loads adapter-specific config from config layer
            database_config = config_service.database
            base_config = config_service.base
            adapter_config = PostgresConfig.from_configs(database_config, base_config)

            # Adapter only receives config and implements
            adapter = PostgresDatabaseAdapter(adapter_config, logger)

        # Future adapters:
        # elif adapter_type == DatabaseAdapterType.MYSQL:
        #     from .adapters.mysql import MySQLDatabaseAdapter
        #     adapter = MySQLDatabaseAdapter(config, logger)

        else:
            raise ValueError(f"Unknown database adapter type: {adapter_type}")

        # Initialize adapter (sync for database)
        adapter.initialize()

        # Verify health
        if not await adapter.health_check():
            raise RuntimeError(f"Database adapter health check failed: {adapter_type.value}")

        logger.info(f"✅ Database adapter ready: {adapter_type.value}")
        return adapter
