"""
BusesModule - Pure CQRS Buses Composer.

This module is responsible ONLY for composing bus instances.
It does NOT manage singleton instances - that's the DI container's job.

Architecture:
─────────────
┌─────────────────┐
│   BusesModule   │  ← Pure Composer
│  - load config  │     Load BusesConfig from ConfigService
│  - call factory │     Pass config to factories
└────────┬────────┘
         │ create_buses()
         ▼
┌─────────────────┐
│ CommandBusFactory│  ← Adapter Switcher
│ QueryBusFactory │
│  - read adapter │     Read adapter type from config
│  - create adapt │     Create adapter
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ICommandBus    │  ← Bus instances
│  IQueryBus      │
└────────┬────────┘
         │ registered as Singleton
         ▼
┌─────────────────┐
│  DI Container   │  ← Manages lifecycle
└─────────────────┘

Usage:
──────
1. DI Container Registration:
   command_bus = providers.Singleton(
       BusesModule.create_command_bus,
       config_service=config_service,
       logger=logger,
   )
   query_bus = providers.Singleton(
       BusesModule.create_query_bus,
       config_service=config_service,
       logger=logger,
   )

2. Application Layer (via DI injection):
   class MyHandler:
       def __init__(self, command_bus: ICommandBus):
           self._command_bus = command_bus
"""

from config.types import BusAdapterType
from shared.application.ports import ICommandBus, IConfigService, ILogger, IQueryBus

from .factory import CommandBusFactory, QueryBusFactory


class BusesModule:
    """
    Pure CQRS Buses Composer.

    Responsibilities:
    - Load BusesConfig from ConfigService
    - Read adapter type from config
    - Pass to factories
    - Return bus instances to DI

    NOT responsible for:
    - Creating adapters (factory does this)
    - Singleton management (DI container does this)
    """

    @staticmethod
    def create_command_bus(
        config_service: IConfigService,
        logger: ILogger,
    ) -> ICommandBus:
        """
        Create and return CommandBus instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Args:
            config_service: ConfigService instance (from DI)
            logger: Logger instance (from DI)

        Returns:
            ICommandBus instance
        """
        # Load buses config from ConfigService
        buses_config = config_service.buses

        # Read adapter type from config
        adapter_type = BusAdapterType(buses_config.BUS_ADAPTER)

        # Delegate to factory
        return CommandBusFactory.create(
            adapter_type=adapter_type,
            logger=logger,
        )

    @staticmethod
    def create_query_bus(
        config_service: IConfigService,
        logger: ILogger,
    ) -> IQueryBus:
        """
        Create and return QueryBus instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Args:
            config_service: ConfigService instance (from DI)
            logger: Logger instance (from DI)

        Returns:
            IQueryBus instance
        """
        # Load buses config from ConfigService
        buses_config = config_service.buses

        # Read adapter type from config
        adapter_type = BusAdapterType(buses_config.BUS_ADAPTER)

        # Delegate to factory
        return QueryBusFactory.create(
            adapter_type=adapter_type,
            logger=logger,
        )
