"""
Notification Factory.

Creates notification adapters based on configuration.
Follows the Factory pattern for adapter instantiation.
"""

from typing import TYPE_CHECKING

from config.notification import (
    InMemoryNotificationConfig,
    InMemoryNotificationSettings,
    NotificationConfig,
    NovuNotificationConfig,
    NovuNotificationSettings,
)
from config.types import NotificationAdapterType
from shared.application.ports.notification import INotificationService

from .adapters.in_memory import InMemoryNotificationAdapter
from .adapters.novu import NovuNotificationAdapter

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class NotificationFactory:
    """
    Factory for creating notification adapters.

    Responsibilities:
    - Read adapter type from config
    - Load adapter-specific configuration
    - Create adapter instance
    - Initialize adapter
    - Perform health check
    - Return initialized adapter
    """

    @staticmethod
    async def create(
        adapter_type: NotificationAdapterType,
        notification_config: NotificationConfig,
        logger: "ILogger",
    ) -> INotificationService:
        """
        Create and initialize notification adapter.

        Flow:
        1. Determine adapter type
        2. Load adapter-specific config from config layer
        3. Create adapter instance
        4. Initialize adapter
        5. Perform health check
        6. Return initialized adapter

        Args:
            adapter_type: Type of adapter to create
            notification_config: Common notification configuration
            logger: Logger instance

        Returns:
            Initialized notification adapter

        Raises:
            ValueError: If adapter type is unknown
            RuntimeError: If health check fails
        """
        if adapter_type == NotificationAdapterType.IN_MEMORY:
            # Load in-memory specific settings and config
            in_memory_settings = InMemoryNotificationSettings()
            adapter_config = InMemoryNotificationConfig.from_config(
                notification_config,
                in_memory_settings,
            )
            adapter = InMemoryNotificationAdapter(adapter_config, logger)
            logger.info(
                "Creating in-memory notification adapter",
                extra={"max_queue_size": adapter_config.max_queue_size},
            )

        elif adapter_type == NotificationAdapterType.NOVU:
            # Load Novu-specific settings
            novu_settings = NovuNotificationSettings()
            adapter_config = NovuNotificationConfig.from_settings(
                novu_settings,
                notification_config,
            )
            adapter = NovuNotificationAdapter(adapter_config, logger)
            logger.info(
                "Creating Novu notification adapter",
                extra={
                    "api_url": adapter_config.api_url or "default",
                    "is_configured": adapter_config.is_configured,
                },
            )

        else:
            raise ValueError(f"Unknown notification adapter type: {adapter_type}")

        # Initialize and verify
        await adapter.initialize()

        if not await adapter.health_check():
            raise RuntimeError(f"Notification adapter health check failed for {adapter_type.value}")

        logger.info(
            f"Notification adapter initialized: {adapter_type.value}",
            extra={"adapter": adapter_type.value},
        )

        return adapter
