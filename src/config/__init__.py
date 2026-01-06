"""
Configuration Index

Central export point for all configuration.
Follows Nest.js Clean Architecture pattern.

Usage:
    from config import configs, ConfigName
    from config import APIConfig, DatabaseConfig
    from config.types import APIConfigType, DatabaseConfigType

    # Get config via ConfigService (DI pattern):
    from infrastructure.config import ConfigModule
    config_service = ConfigModule.get_global_service()
    db_config = config_service.get("database")
"""

# Import config classes from each concern
from .api import APIConfig
from .base import BaseConfig

# Import from concern folders (Port & Adapter pattern)
from .buses import BusesConfig, InMemoryBusConfig
from .cache import CacheConfig, InMemoryCacheConfig, RedisCacheConfig, RedisCacheSettings
from .cors import CORSConfig
from .database import DatabaseConfig, PostgresConfig
from .events import EventsConfig, InMemoryEventBusConfig
from .jobs import InMemoryJobsConfig, JobsConfig, RedisCeleryJobsConfig, RedisCeleryJobsSettings
from .logging import LoggingConfig, StandardLoggerConfig
from .notification import (
    InMemoryNotificationConfig,
    InMemoryNotificationSettings,
    NotificationConfig,
    NovuNotificationConfig,
    NovuNotificationSettings,
)
from .security import SecurityConfig
from .storage import (
    LocalStorageConfig,
    LocalStorageSettings,
    S3StorageConfig,
    S3StorageSettings,
    StorageConfig,
)

# Export types
from .types import (
    APIConfigType,
    BaseConfigType,
    BusAdapterType,
    BusesConfigType,
    CacheAdapterType,
    CacheConfigType,
    ConfigName,
    CORSConfigType,
    DatabaseAdapterType,
    DatabaseConfigType,
    EventBusAdapterType,
    EventsConfigType,
    InMemoryBusConfigType,
    InMemoryCacheConfigType,
    InMemoryEventBusConfigType,
    InMemoryJobsConfigType,
    InMemoryNotificationConfigType,
    JobsAdapterType,
    JobsConfigType,
    LocalStorageConfigType,
    LoggingConfigType,
    NotificationAdapterType,
    NotificationConfigType,
    NovuNotificationConfigType,
    PostgresConfigType,
    RedisCacheConfigType,
    RedisCeleryJobsConfigType,
    S3StorageConfigType,
    SecurityConfigType,
    StandardLoggerConfigType,
    StorageConfigType,
)

# Export array of all config classes for easy import
# Used by ConfigModule.for_root() to load all configs
configs = [
    BaseConfig,
    APIConfig,
    BusesConfig,
    CORSConfig,
    SecurityConfig,
    CacheConfig,
    DatabaseConfig,
    EventsConfig,
    JobsConfig,
    LoggingConfig,
    NotificationConfig,
    StorageConfig,
]

# Map ConfigName to config class
CONFIG_MAPPING = {
    ConfigName.BASE: BaseConfig,
    ConfigName.API: APIConfig,
    ConfigName.BUSES: BusesConfig,
    ConfigName.CORS: CORSConfig,
    ConfigName.SECURITY: SecurityConfig,
    ConfigName.CACHE: CacheConfig,
    ConfigName.DATABASE: DatabaseConfig,
    ConfigName.EVENTS: EventsConfig,
    ConfigName.JOBS: JobsConfig,
    ConfigName.LOGGING: LoggingConfig,
    ConfigName.NOTIFICATION: NotificationConfig,
    ConfigName.STORAGE: StorageConfig,
}

__all__ = [
    # Config array for easy loading
    "configs",
    "CONFIG_MAPPING",
    # ConfigName enum
    "ConfigName",
    # Base configs (no adapter needed)
    "BaseConfig",
    "APIConfig",
    "CORSConfig",
    "SecurityConfig",
    # Buses (Port + Adapters)
    "BusesConfig",
    "InMemoryBusConfig",
    # Cache (Port + Adapters)
    "CacheConfig",
    "RedisCacheSettings",
    "RedisCacheConfig",
    "InMemoryCacheConfig",
    # Database (Port + Adapters)
    "DatabaseConfig",
    "PostgresConfig",
    # Events (Port + Adapters)
    "EventsConfig",
    "InMemoryEventBusConfig",
    # Jobs (Port + Adapters)
    "JobsConfig",
    "RedisCeleryJobsSettings",
    "RedisCeleryJobsConfig",
    "InMemoryJobsConfig",
    # Logging (Port + Adapters)
    "LoggingConfig",
    "StandardLoggerConfig",
    # Storage (Port + Adapters)
    "StorageConfig",
    "LocalStorageSettings",
    "LocalStorageConfig",
    "S3StorageSettings",
    "S3StorageConfig",
    # Notification (Port + Adapters)
    "NotificationConfig",
    "InMemoryNotificationSettings",
    "InMemoryNotificationConfig",
    "NovuNotificationSettings",
    "NovuNotificationConfig",
    # Types
    "BaseConfigType",
    "APIConfigType",
    "BusAdapterType",
    "BusesConfigType",
    "InMemoryBusConfigType",
    "CORSConfigType",
    "SecurityConfigType",
    "CacheAdapterType",
    "CacheConfigType",
    "RedisCacheConfigType",
    "InMemoryCacheConfigType",
    "DatabaseAdapterType",
    "DatabaseConfigType",
    "PostgresConfigType",
    "EventBusAdapterType",
    "EventsConfigType",
    "InMemoryEventBusConfigType",
    "JobsAdapterType",
    "JobsConfigType",
    "RedisCeleryJobsConfigType",
    "InMemoryJobsConfigType",
    "LoggingConfigType",
    "StandardLoggerConfigType",
    "StorageConfigType",
    "LocalStorageConfigType",
    "S3StorageConfigType",
    # Notification Types
    "NotificationAdapterType",
    "NotificationConfigType",
    "InMemoryNotificationConfigType",
    "NovuNotificationConfigType",
]
