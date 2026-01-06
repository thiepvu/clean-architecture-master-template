"""
LoggingModule - Pure Logger Composer.

This module is responsible ONLY for composing logger instances.
It does NOT manage singleton instances - that's the DI container's job.

Architecture:
─────────────
┌─────────────────┐
│  LoggingModule  │  ← Pure Composer
│  - load config  │     Load LoggingConfig from ConfigService
│  - call factory │     Pass config to LoggerFactory
└────────┬────────┘
         │ create_logger()
         ▼
┌─────────────────┐
│  LoggerFactory  │  ← Adapter Switcher
│  - read adapter │     Read adapter type from config
│  - load config  │     Load specific config
│  - create adapt │     Create adapter
│  - init + check │     Init + health check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    ILogger      │  ← Logger instance
└────────┬────────┘
         │ registered as Singleton
         ▼
┌─────────────────┐
│  DI Container   │  ← Manages lifecycle
└─────────────────┘

Usage:
──────
1. DI Container Registration:
   logger = providers.Singleton(
       LoggingModule.create_logger,
       config_service=config_service,
   )

2. Application Layer (via DI injection):
   class MyService:
       def __init__(self, logger: ILogger):
           self._logger = logger
"""

from shared.application.ports import IConfigService, ILogger

from .factory import LoggerFactory


class LoggingModule:
    """
    Pure Logger Composer.

    Responsibilities:
    - Load LoggingConfig from ConfigService
    - Pass config to LoggerFactory
    - Return adapter instance to DI

    NOT responsible for:
    - Reading adapter type (factory does this)
    - Loading specific config (factory does this)
    - Creating adapter (factory does this)
    - Init/health check (factory does this)
    - Singleton management (DI container does this)

    Example:
        # In DI container registration
        logger = providers.Singleton(
            LoggingModule.create_logger,
            config_service=config_service,
        )
    """

    @staticmethod
    def create_logger(
        config_service: IConfigService,
        name: str = "app",
    ) -> ILogger:
        """
        Create and return logger instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Flow:
        1. Load LoggingConfig from ConfigService
        2. Pass config to LoggerFactory
        3. Factory reads adapter type, loads specific config, creates adapter
        4. Factory init + health check
        5. Return adapter instance to DI

        Args:
            config_service: ConfigService instance (from DI)
            name: Logger name

        Returns:
            ILogger instance
        """
        print(f"\n{'='*60}")
        print("[LoggingModule] Creating logger...")
        print(f"{'='*60}")
        print(f"Logger name: {name}")

        # Load logging config from ConfigService
        logging_config = config_service.logging

        # Delegate to factory - it handles everything else
        logger = LoggerFactory.create(
            logging_config=logging_config,
            name=name,
        )

        print(f"{'='*60}\n")

        return logger
