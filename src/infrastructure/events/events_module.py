"""
EventsModule - Pure Event Bus Composer.

This module is responsible ONLY for composing event bus instances.
It does NOT manage singleton instances - that's the DI container's job.

Architecture:
─────────────
┌─────────────────┐
│  EventsModule   │  ← Pure Composer
│  - load config  │     Load EventsConfig from ConfigService
│  - call factory │     Pass config to EventBusFactory
└────────┬────────┘
         │ create_event_bus()
         ▼
┌─────────────────┐
│EventBusFactory  │  ← Adapter Switcher
│  - read adapter │     Read adapter type from config
│  - create adapt │     Create adapter
│  - init + check │     Init + health check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   IEventBus     │  ← Event bus instance
└────────┬────────┘
         │ registered as Singleton
         ▼
┌─────────────────┐
│  DI Container   │  ← Manages lifecycle
└─────────────────┘

Usage:
──────
1. DI Container Registration:
   event_bus = providers.Singleton(
       EventsModule.create_event_bus,
       config_service=config_service,
       logger=logger,
   )

2. Application Layer (via DI injection):
   class MyService:
       def __init__(self, event_bus: IEventBus):
           self._event_bus = event_bus
"""

from config.types import EventBusAdapterType
from shared.application.ports import IConfigService, IEventBus, ILogger

from .factory import EventBusFactory


class EventsModule:
    """
    Pure Event Bus Composer.

    Responsibilities:
    - Load EventsConfig from ConfigService
    - Read adapter type from config
    - Pass to EventBusFactory
    - Return event bus instance to DI

    NOT responsible for:
    - Creating adapter (factory does this)
    - Init/health check (factory does this)
    - Singleton management (DI container does this)
    """

    @staticmethod
    async def create_event_bus(
        config_service: IConfigService,
        logger: ILogger,
    ) -> IEventBus:
        """
        Create and return event bus instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Args:
            config_service: ConfigService instance (from DI)
            logger: Logger instance (from DI)

        Returns:
            IEventBus instance
        """
        # Load events config from ConfigService
        events_config = config_service.events

        # Read adapter type from config
        adapter_type = EventBusAdapterType(events_config.EVENT_BUS_ADAPTER)

        # Delegate to factory
        return await EventBusFactory.create(
            adapter_type=adapter_type,
            logger=logger,
        )
