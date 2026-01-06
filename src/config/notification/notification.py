"""
Common Notification Configuration (Port Interface).

This is the port/interface layer for notification configuration.
Determines which adapter to use and common settings.

Environment Variables:
    NOTIFICATION_ADAPTER: "in_memory" or "novu" (default: "in_memory")
    NOTIFICATION_DEFAULT_FROM_EMAIL: Default sender email
    NOTIFICATION_DEFAULT_FROM_NAME: Default sender name
    NOTIFICATION_ENABLED_CHANNELS: Comma-separated list of enabled channels
"""

from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class NotificationConfig(BaseSettings):
    """
    Common notification configuration (Port interface).

    This configuration determines which adapter to use
    and provides common settings for all adapters.
    """

    model_config = {"env_prefix": "NOTIFICATION_", "extra": "ignore"}

    # Adapter selection
    NOTIFICATION_ADAPTER: Literal["in_memory", "novu"] = Field(
        default="in_memory",
        description="Notification adapter type",
    )

    # Common settings
    DEFAULT_FROM_EMAIL: str = Field(
        default="noreply@example.com",
        description="Default sender email address",
    )

    DEFAULT_FROM_NAME: str = Field(
        default="Application",
        description="Default sender name",
    )

    ENABLED_CHANNELS: str = Field(
        default="email,in_app",
        description="Comma-separated list of enabled notification channels",
    )

    @property
    def is_novu(self) -> bool:
        """Check if using Novu adapter."""
        return self.NOTIFICATION_ADAPTER == "novu"

    @property
    def is_in_memory(self) -> bool:
        """Check if using in-memory adapter."""
        return self.NOTIFICATION_ADAPTER == "in_memory"

    @property
    def enabled_channels_list(self) -> List[str]:
        """Get enabled channels as a list."""
        return [ch.strip() for ch in self.ENABLED_CHANNELS.split(",") if ch.strip()]
