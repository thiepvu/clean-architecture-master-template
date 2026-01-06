"""
Novu Notification Adapter Configuration.

Configuration specific to the Novu notification adapter.
Novu is a notification infrastructure platform for managing
multi-channel notifications.

Environment Variables:
    NOVU_API_KEY: Novu API key (required)
    NOVU_API_URL: Novu API URL (optional, for self-hosted)
    NOVU_APPLICATION_IDENTIFIER: Application identifier (optional)
    NOVU_BACKEND_URL: Backend URL for self-hosted (optional)
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from .notification import NotificationConfig


class NovuNotificationSettings(BaseSettings):
    """
    Novu-specific settings loaded from environment variables.

    These are settings that should come from environment/secrets.
    """

    model_config = {"env_prefix": "NOVU_", "extra": "ignore"}

    # Required
    API_KEY: str = Field(
        default="",
        description="Novu API key",
    )

    # Optional - for self-hosted Novu
    API_URL: Optional[str] = Field(
        default=None,
        description="Novu API URL (for self-hosted)",
    )

    APPLICATION_IDENTIFIER: Optional[str] = Field(
        default=None,
        description="Novu application identifier",
    )

    BACKEND_URL: Optional[str] = Field(
        default=None,
        description="Novu backend URL (for self-hosted)",
    )


@dataclass
class NovuNotificationConfig:
    """
    Novu notification adapter configuration.

    Created from NovuNotificationSettings and NotificationConfig.
    """

    # Common settings (from NotificationConfig)
    default_from_email: str
    default_from_name: str
    enabled_channels: List[str]

    # Novu specific settings
    api_key: str
    api_url: Optional[str]
    application_identifier: Optional[str]
    backend_url: Optional[str]

    @classmethod
    def from_settings(
        cls,
        novu_settings: NovuNotificationSettings,
        notification_config: "NotificationConfig",
    ) -> "NovuNotificationConfig":
        """
        Create NovuNotificationConfig from settings.

        Args:
            novu_settings: Novu-specific settings
            notification_config: Common notification configuration

        Returns:
            NovuNotificationConfig instance
        """
        return cls(
            default_from_email=notification_config.DEFAULT_FROM_EMAIL,
            default_from_name=notification_config.DEFAULT_FROM_NAME,
            enabled_channels=notification_config.enabled_channels_list,
            api_key=novu_settings.API_KEY,
            api_url=novu_settings.API_URL,
            application_identifier=novu_settings.APPLICATION_IDENTIFIER,
            backend_url=novu_settings.BACKEND_URL,
        )

    @property
    def is_configured(self) -> bool:
        """Check if Novu is properly configured."""
        return bool(self.api_key)
