"""
DatabaseModule - Pure Database Composer.

This module is responsible ONLY for composing database instances.
It does NOT manage singleton instances - that's the DI container's job.

Architecture:
─────────────
┌─────────────────┐
│ DatabaseModule  │  ← Pure Composer
│  - load config  │     Load DatabaseConfig from ConfigService
│  - call factory │     Pass config to DatabaseFactory
└────────┬────────┘
         │ create_database()
         ▼
┌─────────────────┐
│DatabaseFactory  │  ← Adapter Switcher
│  - read adapter │     Read adapter type from config
│  - create adapt │     Create adapter
│  - init + check │     Init + health check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│IDatabaseAdapter │  ← Database instance
└────────┬────────┘
         │ registered as Singleton
         ▼
┌─────────────────┐
│  DI Container   │  ← Manages lifecycle
└─────────────────┘

Usage:
──────
1. DI Container Registration:
   database = providers.Singleton(
       DatabaseModule.create_database,
       config_service=config_service,
       logger=logger,
   )

2. Application Layer (via DI injection):
   class MyService:
       def __init__(self, database: IDatabaseAdapter):
           self._database = database
"""

from config.types import DatabaseAdapterType
from shared.application.ports import IConfigService, IDatabaseAdapter, ILogger

from .factory import DatabaseFactory


class DatabaseModule:
    """
    Pure Database Composer.

    Responsibilities:
    - Load DatabaseConfig from ConfigService
    - Read adapter type from config
    - Pass to DatabaseFactory
    - Return database instance to DI

    NOT responsible for:
    - Creating adapter (factory does this)
    - Init/health check (factory does this)
    - Singleton management (DI container does this)
    """

    @staticmethod
    async def create_database(
        config_service: IConfigService,
        logger: ILogger,
    ) -> IDatabaseAdapter:
        """
        Create and return database instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Args:
            config_service: ConfigService instance (from DI)
            logger: Logger instance (from DI)

        Returns:
            IDatabaseAdapter instance
        """
        # Load database config from ConfigService
        db_config = config_service.database

        # Read adapter type from config
        adapter_type = DatabaseAdapterType(db_config.DATABASE_ADAPTER)

        # Delegate to factory
        return await DatabaseFactory.create(
            adapter_type=adapter_type,
            config_service=config_service,
            logger=logger,
        )
