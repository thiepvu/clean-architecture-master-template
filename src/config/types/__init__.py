"""
Config Types - TypedDict definitions for type-safe config access.

Each concern has common type + adapter-specific types in one file.
Follows Port & Adapter pattern.
"""

from enum import Enum

from .api import APIConfigType
from .base import BaseConfigType
from .buses import BusAdapterType, BusesConfigType, InMemoryBusConfigType
from .cache import CacheAdapterType, CacheConfigType, InMemoryCacheConfigType, RedisCacheConfigType
from .cors import CORSConfigType
from .database import DatabaseAdapterType, DatabaseConfigType, PostgresConfigType
from .events import EventBusAdapterType, EventsConfigType, InMemoryEventBusConfigType
from .jobs import InMemoryJobsConfigType, JobsAdapterType, JobsConfigType, RedisCeleryJobsConfigType
from .logging import LoggingConfigType, StandardLoggerConfigType
from .notification import (
    InMemoryNotificationConfigType,
    NotificationAdapterType,
    NotificationConfigType,
    NovuNotificationConfigType,
)
from .security import SecurityConfigType
from .storage import (
    LocalStorageConfigType,
    S3StorageConfigType,
    StorageAdapterType,
    StorageConfigType,
)


class ConfigName(str, Enum):
    """Configuration concern names for ConfigService.get(name)."""

    BASE = "base"
    API = "api"
    BUSES = "buses"
    CACHE = "cache"
    CORS = "cors"
    DATABASE = "database"
    EVENTS = "events"
    JOBS = "jobs"
    LOGGING = "logging"
    NOTIFICATION = "notification"
    SECURITY = "security"
    STORAGE = "storage"


__all__ = [
    # Enum
    "ConfigName",
    # Base
    "BaseConfigType",
    # API
    "APIConfigType",
    # Buses (adapter type + common + adapters)
    "BusAdapterType",
    "BusesConfigType",
    "InMemoryBusConfigType",
    # Cache (adapter type + common + adapters)
    "CacheAdapterType",
    "CacheConfigType",
    "RedisCacheConfigType",
    "InMemoryCacheConfigType",
    # CORS
    "CORSConfigType",
    # Database (adapter type + common + adapters)
    "DatabaseAdapterType",
    "DatabaseConfigType",
    "PostgresConfigType",
    # Events (adapter type + common + adapters)
    "EventBusAdapterType",
    "EventsConfigType",
    "InMemoryEventBusConfigType",
    # Jobs (adapter type + common + adapters)
    "JobsAdapterType",
    "JobsConfigType",
    "RedisCeleryJobsConfigType",
    "InMemoryJobsConfigType",
    # Logging (common + adapters)
    "LoggingConfigType",
    "StandardLoggerConfigType",
    # Security
    "SecurityConfigType",
    # Storage (adapter type + common + adapters)
    "StorageAdapterType",
    "StorageConfigType",
    "LocalStorageConfigType",
    "S3StorageConfigType",
    # Notification (adapter type + common + adapters)
    "NotificationAdapterType",
    "NotificationConfigType",
    "InMemoryNotificationConfigType",
    "NovuNotificationConfigType",
]
