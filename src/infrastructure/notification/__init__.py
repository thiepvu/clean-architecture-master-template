"""
Notification Infrastructure Module.

Provides notification capabilities with Port & Adapter pattern.

Adapters:
- InMemoryNotificationAdapter: In-memory notification (development/testing)
- NovuNotificationAdapter: Novu notification platform (production)

Usage:
──────
# Via DI Container (Recommended)
notification_service = providers.Singleton(
    NotificationModule.create_notification,
    logger=logger,
)

# Direct Factory Usage
from infrastructure.notification import NotificationFactory
from config.types import NotificationAdapterType
from config.notification import NotificationConfig

notification = await NotificationFactory.create(
    adapter_type=NotificationAdapterType.IN_MEMORY,
    notification_config=NotificationConfig(),
    logger=logger,
)

# Direct Adapter Usage (Development)
from infrastructure.notification import InMemoryNotificationAdapter
from config.notification import NotificationConfig, InMemoryNotificationConfig

notification_config = NotificationConfig()
config = InMemoryNotificationConfig.from_config(notification_config)
notification = InMemoryNotificationAdapter(config, logger)
await notification.initialize()

Configuration:
─────────────
Environment variables:
- NOTIFICATION_ADAPTER: "in_memory" or "novu" (default: "in_memory")
- NOTIFICATION_DEFAULT_FROM_EMAIL: Default sender email
- NOTIFICATION_DEFAULT_FROM_NAME: Default sender name
- NOTIFICATION_ENABLED_CHANNELS: Comma-separated list of enabled channels

Novu-specific:
- NOVU_API_KEY: Novu API key (required for Novu adapter)
- NOVU_API_URL: Novu API URL (optional, for self-hosted)

See config/notification/ for full configuration options.
"""

# Adapters (for direct usage or testing)
from .adapters import InMemoryNotificationAdapter, NovuNotificationAdapter

# Factory (for direct creation)
from .factory import NotificationFactory

# Module (primary interface for DI)
from .notification_module import NotificationModule

__all__ = [
    # Module (primary interface)
    "NotificationModule",
    # Factory
    "NotificationFactory",
    # Adapters
    "InMemoryNotificationAdapter",
    "NovuNotificationAdapter",
]
