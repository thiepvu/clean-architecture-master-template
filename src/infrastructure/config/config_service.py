"""
ConfigService - Global configuration access service.

Implements IConfigService interface following Nest.js ConfigService pattern:
- get(name): Get config by concern name
- get_or_throw(name): Get config or raise error
- Typed access to all config sections

Usage:
    # Via DI injection (recommended)
    class MyService:
        def __init__(self, config_service: IConfigService):
            self._config = config_service

    # Get by name
    db_config = config_service.get("database")
    cache_config = config_service.get(ConfigName.CACHE)

    # Direct typed access
    db = config_service.database
    cache = config_service.cache
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Union, overload

from config.types import ConfigName
from shared.application.ports import IConfigService

if TYPE_CHECKING:
    from config import (
        APIConfig,
        BaseConfig,
        BusesConfig,
        CacheConfig,
        CORSConfig,
        DatabaseConfig,
        EventsConfig,
        JobsConfig,
        LoggingConfig,
        NotificationConfig,
        SecurityConfig,
        StorageConfig,
    )


class ConfigService(IConfigService):
    """
    Global configuration access service.

    Implements IConfigService interface from shared.application.ports.

    Provides:
    - Type-safe config access via get(name)
    - Direct property access for each config
    - Environment helpers
    - Config summary

    Example:
        # Via DI injection
        class MyService:
            def __init__(self, config_service: IConfigService):
                self._config = config_service

        # Get by name (string or enum)
        db_config = config_service.get("database")
        db_config = config_service.get(ConfigName.DATABASE)

        # Direct access
        db = config_service.database
        cache = config_service.cache

        # Typed dict format
        db_dict = config_service.get_dict("database")
    """

    def __init__(self, configs: Dict[ConfigName, Any], environment: str):
        """
        Initialize ConfigService.

        Args:
            configs: Dictionary of loaded config instances
            environment: Current environment name
        """
        self._configs = configs
        self._environment = environment

    # =========================================================================
    # Get by name methods
    # =========================================================================

    @overload
    def get(self, name: str) -> Any: ...

    @overload
    def get(self, name: ConfigName) -> Any: ...

    def get(self, name: Union[str, ConfigName]) -> Any:
        """
        Get config by concern name.

        Args:
            name: Config name (string or ConfigName enum)

        Returns:
            Config instance or None if not found

        Example:
            db_config = service.get("database")
            db_config = service.get(ConfigName.DATABASE)
        """
        if isinstance(name, str):
            try:
                name = ConfigName(name)
            except ValueError:
                return None

        return self._configs.get(name)

    def get_or_throw(self, name: Union[str, ConfigName]) -> Any:
        """
        Get config by name or raise error if not found.

        Args:
            name: Config name (string or ConfigName enum)

        Returns:
            Config instance

        Raises:
            ValueError: If config not found
        """
        config = self.get(name)
        if config is None:
            raise ValueError(f"Config '{name}' not found")
        return config

    # =========================================================================
    # Get typed dictionary format
    # =========================================================================

    def get_dict(self, name: Union[str, ConfigName]) -> Optional[Dict[str, Any]]:
        """
        Get config as typed dictionary.

        Args:
            name: Config name

        Returns:
            Config as TypedDict or None
        """
        config = self.get(name)
        if config is None:
            return None

        if hasattr(config, "to_dict"):
            return config.to_dict()

        return None

    # =========================================================================
    # Direct property access (typed)
    # =========================================================================

    @property
    def base(self) -> Optional["BaseConfig"]:
        """Get base config."""
        return self._configs.get(ConfigName.BASE)

    @property
    def api(self) -> Optional["APIConfig"]:
        """Get API config."""
        return self._configs.get(ConfigName.API)

    @property
    def buses(self) -> Optional["BusesConfig"]:
        """Get buses config."""
        return self._configs.get(ConfigName.BUSES)

    @property
    def cache(self) -> Optional["CacheConfig"]:
        """Get cache config."""
        return self._configs.get(ConfigName.CACHE)

    @property
    def cors(self) -> Optional["CORSConfig"]:
        """Get CORS config."""
        return self._configs.get(ConfigName.CORS)

    @property
    def database(self) -> Optional["DatabaseConfig"]:
        """Get database config."""
        return self._configs.get(ConfigName.DATABASE)

    @property
    def events(self) -> Optional["EventsConfig"]:
        """Get events config."""
        return self._configs.get(ConfigName.EVENTS)

    @property
    def jobs(self) -> Optional["JobsConfig"]:
        """Get jobs config."""
        return self._configs.get(ConfigName.JOBS)

    @property
    def logging(self) -> Optional["LoggingConfig"]:
        """Get logging config."""
        return self._configs.get(ConfigName.LOGGING)

    @property
    def security(self) -> Optional["SecurityConfig"]:
        """Get security config."""
        return self._configs.get(ConfigName.SECURITY)

    @property
    def storage(self) -> Optional["StorageConfig"]:
        """Get storage config."""
        return self._configs.get(ConfigName.STORAGE)

    @property
    def notification(self) -> Optional["NotificationConfig"]:
        """Get notification config."""
        return self._configs.get(ConfigName.NOTIFICATION)

    # =========================================================================
    # Environment helpers
    # =========================================================================

    @property
    def environment(self) -> str:
        """Get current environment"""
        return self._environment

    @property
    def is_development(self) -> bool:
        return self._environment == "development"

    @property
    def is_production(self) -> bool:
        return self._environment == "production"

    @property
    def is_testing(self) -> bool:
        return self._environment == "testing"

    @property
    def is_staging(self) -> bool:
        return self._environment == "staging"

    # =========================================================================
    # Utility methods
    # =========================================================================

    def summary(self) -> Dict[str, Any]:
        """
        Get configuration summary.

        Returns:
            Dictionary with key config values
        """
        return {
            "environment": self._environment,
            "debug": self.base.DEBUG if self.base else False,
            "app_name": self.base.APP_NAME if self.base else "Unknown",
            "app_version": self.base.APP_VERSION if self.base else "Unknown",
            "server_url": self.base.SERVER_URL if self.base else "Unknown",
            # Infrastructure adapters
            "bus_adapter": self.buses.BUS_ADAPTER if self.buses else "unknown",
            "cache_adapter": self.cache.CACHE_ADAPTER if self.cache else "unknown",
            "database_adapter": self.database.DATABASE_ADAPTER if self.database else "unknown",
            "event_bus_adapter": self.events.EVENT_BUS_ADAPTER if self.events else "unknown",
            "jobs_adapter": self.jobs.JOBS_ADAPTER if self.jobs else "unknown",
            "log_adapter": self.logging.LOG_ADAPTER if self.logging else "unknown",
            "storage_adapter": self.storage.STORAGE_ADAPTER if self.storage else "unknown",
            "notification_adapter": (
                self.notification.NOTIFICATION_ADAPTER if self.notification else "unknown"
            ),
            # Status
            "database": (
                "configured" if self.database and self.database.DATABASE_URL else "not configured"
            ),
            "docs": "enabled" if self.api and self.api.docs_enabled else "disabled",
            "log_level": self.logging.LOG_LEVEL if self.logging else "INFO",
            "cors": "enabled" if self.cors and self.cors.CORS_ENABLED else "disabled",
        }

    def __repr__(self) -> str:
        return (
            f"ConfigService(environment={self._environment}, configs={list(self._configs.keys())})"
        )
