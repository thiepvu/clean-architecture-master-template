"""
Logging Infrastructure Module.

Provides logging capabilities with Port & Adapter pattern.

Architecture:
─────────────
- LoggingModule: Pure composer (loads LoggingConfig, delegates to factory)
- LoggerFactory: Adapter switcher (reads adapter type, creates adapter, init + health check)
- StandardLoggerAdapter: Standard Python logging implementation
- DI Container: Manages logger as Singleton

Usage:
──────
1. Bootstrap/App Level (main.py, scripts, app_factory.py):
   from shared.bootstrap import create_logger

   logger = create_logger()
   logger.info("Application started")

2. DI Container Registration:
   from infrastructure.logging import LoggingModule

   logger = providers.Singleton(
       LoggingModule.create_logger,
       config_service=config_service,
   )

3. Module/Application Layer (via DI injection):
   from shared.application.ports import ILogger

   class MyService:
       def __init__(self, logger: ILogger):
           self._logger = logger
"""

from .adapters import StandardLoggerAdapter
from .logging_module import LoggingModule

__all__ = [
    # Module (primary interface for DI)
    "LoggingModule",
    # Adapters (for direct usage if needed)
    "StandardLoggerAdapter",
]
