"""
Notification configuration types - Port & Adapter pattern.

Contains:
- NotificationAdapterType: Enum for adapter selection
- NotificationConfigType: Common/Port interface for all notification adapters
- InMemoryNotificationConfigType: In-memory adapter specific
- NovuNotificationConfigType: Novu adapter specific
"""

from enum import Enum
from typing import List, Literal, Optional, TypedDict


class NotificationAdapterType(str, Enum):
    """Available notification adapter types."""

    IN_MEMORY = "in_memory"
    NOVU = "novu"


class NotificationConfigType(TypedDict):
    """Common notification configuration type (Port interface)."""

    adapter: Literal["in_memory", "novu"]
    default_from_email: str
    default_from_name: str
    enabled_channels: List[str]


class InMemoryNotificationConfigType(TypedDict):
    """In-memory notification adapter configuration type."""

    # Common settings
    default_from_email: str
    default_from_name: str
    enabled_channels: List[str]

    # In-memory specific
    max_queue_size: int
    retention_hours: int


class NovuNotificationConfigType(TypedDict):
    """Novu notification adapter configuration type."""

    # Common settings
    default_from_email: str
    default_from_name: str
    enabled_channels: List[str]

    # Novu specific
    api_key: str
    api_url: Optional[str]
    application_identifier: Optional[str]
    backend_url: Optional[str]
