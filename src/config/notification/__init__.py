"""
Notification Configuration Module.

Port & Adapter pattern for notification configuration:
- NotificationConfig: Common/Port interface (adapter selection + shared settings)
- InMemoryNotificationConfig: In-memory adapter specific settings
- NovuNotificationConfig: Novu adapter specific settings

Requirements:
    pip install novu  # For Novu adapter
"""

from .in_memory import InMemoryNotificationConfig, InMemoryNotificationSettings
from .notification import NotificationConfig
from .novu import NovuNotificationConfig, NovuNotificationSettings

__all__ = [
    # Common/Port
    "NotificationConfig",
    # In-Memory Adapter
    "InMemoryNotificationSettings",
    "InMemoryNotificationConfig",
    # Novu Adapter
    "NovuNotificationSettings",
    "NovuNotificationConfig",
]
