"""
In-Memory Notification Adapter Configuration.

Configuration specific to the in-memory notification adapter.
Used for development, testing, and single-process applications.

Environment Variables:
    IN_MEMORY_NOTIFICATION_MAX_QUEUE_SIZE: Maximum notifications to keep (default: 10000)
    IN_MEMORY_NOTIFICATION_RETENTION_HOURS: Hours to retain notifications (default: 24)
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from pydantic import Field
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from .notification import NotificationConfig


class InMemoryNotificationSettings(BaseSettings):
    """
    In-memory notification settings loaded from environment variables.

    These settings configure the in-memory notification adapter behavior.
    """

    model_config = {"env_prefix": "IN_MEMORY_NOTIFICATION_", "extra": "ignore"}

    MAX_QUEUE_SIZE: int = Field(
        default=10000,
        description="Maximum number of notifications to keep in memory",
    )

    RETENTION_HOURS: int = Field(
        default=24,
        description="Hours to retain notifications before cleanup",
    )


@dataclass
class InMemoryNotificationConfig:
    """
    In-memory notification adapter configuration.

    Created from NotificationConfig with in-memory specific defaults.
    """

    # Common settings (from NotificationConfig)
    default_from_email: str
    default_from_name: str
    enabled_channels: List[str]

    # In-memory specific settings
    max_queue_size: int
    retention_hours: int

    @classmethod
    def from_config(
        cls,
        notification_config: "NotificationConfig",
        in_memory_settings: "InMemoryNotificationSettings | None" = None,
    ) -> "InMemoryNotificationConfig":
        """
        Create InMemoryNotificationConfig from NotificationConfig.

        Args:
            notification_config: Common notification configuration
            in_memory_settings: In-memory specific settings (optional)

        Returns:
            InMemoryNotificationConfig instance
        """
        settings = in_memory_settings or InMemoryNotificationSettings()
        return cls(
            default_from_email=notification_config.DEFAULT_FROM_EMAIL,
            default_from_name=notification_config.DEFAULT_FROM_NAME,
            enabled_channels=notification_config.enabled_channels_list,
            max_queue_size=settings.MAX_QUEUE_SIZE,
            retention_hours=settings.RETENTION_HOURS,
        )
