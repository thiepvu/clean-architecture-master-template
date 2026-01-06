"""
ConfigService Port (Interface).

Defines the contract for configuration access.
Implementations: ConfigService (infrastructure/config)
"""

from typing import Any, Dict, Optional, Protocol, Union, runtime_checkable


@runtime_checkable
class IConfigService(Protocol):
    """
    ConfigService port (interface).

    All config service implementations must implement this protocol.
    Provides unified access to application configuration.

    Example:
        class ConfigService:
            def get(self, name: str) -> Any:
                return self._configs.get(name)

    Usage:
        # In application/infrastructure code
        def __init__(self, config_service: IConfigService):
            self._config = config_service

        # Access config
        db_config = self._config.database
        cache_config = self._config.get("cache")
    """

    # =========================================================================
    # Get by name methods
    # =========================================================================

    def get(self, name: Union[str, Any]) -> Any:
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
        ...

    def get_or_throw(self, name: Union[str, Any]) -> Any:
        """
        Get config by name or raise error if not found.

        Args:
            name: Config name (string or ConfigName enum)

        Returns:
            Config instance

        Raises:
            ValueError: If config not found
        """
        ...

    def get_dict(self, name: Union[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get config as typed dictionary.

        Args:
            name: Config name

        Returns:
            Config as TypedDict or None
        """
        ...

    # =========================================================================
    # Direct property access (typed)
    # =========================================================================

    @property
    def base(self) -> Any:
        """Get base config (BaseConfig)"""
        ...

    @property
    def api(self) -> Any:
        """Get API config (APIConfig)"""
        ...

    @property
    def cache(self) -> Any:
        """Get cache config (CacheConfig)"""
        ...

    @property
    def cors(self) -> Any:
        """Get CORS config (CORSConfig)"""
        ...

    @property
    def database(self) -> Any:
        """Get database config (DatabaseConfig)"""
        ...

    @property
    def events(self) -> Any:
        """Get events config (EventsConfig)"""
        ...

    @property
    def jobs(self) -> Any:
        """Get jobs config (JobsConfig)"""
        ...

    @property
    def logging(self) -> Any:
        """Get logging config (LoggingConfig)"""
        ...

    @property
    def security(self) -> Any:
        """Get security config (SecurityConfig)"""
        ...

    @property
    def storage(self) -> Any:
        """Get storage config (StorageConfig)"""
        ...

    # =========================================================================
    # Environment helpers
    # =========================================================================

    @property
    def environment(self) -> str:
        """Get current environment name"""
        ...

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        ...

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        ...

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        ...

    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment"""
        ...

    # =========================================================================
    # Utility methods
    # =========================================================================

    def summary(self) -> Dict[str, Any]:
        """
        Get configuration summary.

        Returns:
            Dictionary with key config values for debugging/logging
        """
        ...
