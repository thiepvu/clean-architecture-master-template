"""
Config Module - Configuration Composer with DI Pattern.

Architecture:
─────────────
- ConfigModule: Pure composer (loads env, composes configs, validates)
- ConfigService: Concrete implementation of IConfigService

Usage:
──────
1. DI Container Registration:
   from infrastructure.config import ConfigModule
   config_service = providers.Singleton(
       lambda: ConfigModule().load().create_service()
   )

2. Bootstrap/App Level (main.py, scripts):
   from shared.bootstrap import create_config_service

3. Module/Application Layer (via DI injection):
   from shared.application.ports import IConfigService

   class MyService:
       def __init__(self, config_service: IConfigService):
           self._config = config_service
"""

from .config_module import ConfigModule
from .config_service import ConfigService

__all__ = [
    "ConfigModule",
    "ConfigService",
]
