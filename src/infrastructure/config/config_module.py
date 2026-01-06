"""
ConfigModule - Pure Configuration Composer.

This module is responsible ONLY for composing configurations.
It does NOT manage singleton instances - that's the DI container's job.

Architecture:
─────────────
┌─────────────────┐
│  ConfigModule   │  ← Pure Composer (no singleton management)
│  - load .env    │
│  - compose all  │
│  - validate     │
└────────┬────────┘
         │ create_service()
         ▼
┌─────────────────┐
│  ConfigService  │  ← Access layer for configs
└────────┬────────┘
         │ registered as Singleton
         ▼
┌─────────────────┐
│  DI Container   │  ← Manages lifecycle
└─────────────────┘

Usage:
──────
1. DI Container Registration:
   config_service = providers.Singleton(ConfigModule.create_service)

2. Application Layer (via DI injection):
   class MyService:
       def __init__(self, config_service: IConfigService):
           self._config = config_service
"""

from typing import Any, Dict, Optional

# Import configs and mapping from src/config
from config import CONFIG_MAPPING, ConfigName

# Import env_loader for centralized env detection and loading
from config.env_loader import detect_environment, is_env_loaded, load_env_files
from shared.application.ports import IConfigService

from .config_service import ConfigService


class ConfigModule:
    """
    Pure Configuration Composer.

    Responsibilities:
    - Load .env files by environment
    - Load all config classes from src/config
    - Validate using Pydantic schemas
    - Create ConfigService instance

    NOT responsible for:
    - Singleton management (DI container does this)
    - Global instance access (use DI injection instead)

    Example:
        # In DI container registration
        config_service = providers.Singleton(ConfigModule.create_service)
    """

    @staticmethod
    def create_service(environment: Optional[str] = None) -> IConfigService:
        """
        Create ConfigService instance.

        This is the main method for DI container to call.
        DI container should call this once and register as Singleton.

        Flow:
        1. Detect/use environment
        2. Load .env files
        3. Load all config classes (Pydantic validation)
        4. Create and return ConfigService

        Args:
            environment: Override environment detection (optional)

        Returns:
            IConfigService instance
        """
        env = environment or detect_environment()

        print(f"\n{'='*60}")
        print("[ConfigModule] Loading configuration...")
        print(f"{'='*60}")
        print(f"Environment: {env}")

        # 1. Load env files
        if is_env_loaded():
            print("[ConfigModule] Env files already loaded, skipping...")
        else:
            loaded_files = load_env_files(env)
            if loaded_files:
                print(f"[ConfigModule] Loaded env files: {loaded_files}")
            else:
                print("[ConfigModule] No .env files found")

        # 2. Load all config classes (Pydantic validation)
        configs: Dict[ConfigName, Any] = {}
        for name, config_cls in CONFIG_MAPPING.items():
            try:
                configs[name] = config_cls()
            except Exception as e:
                raise ValueError(f"Failed to load {name.value} config: {e}") from e

        print(f"[ConfigModule] Loaded {len(configs)} config modules")
        print(f"{'='*60}\n")

        # 3. Create and return ConfigService
        return ConfigService(
            configs=configs,
            environment=env,
        )
