"""
Notification Module.

Pure composer for notification service creation.
Follows the Module pattern for DI composition.
"""

from typing import TYPE_CHECKING

from config.notification import NotificationConfig
from config.types import NotificationAdapterType
from shared.application.ports.notification import INotificationService

from .factory import NotificationFactory

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class NotificationModule:
    """
    Pure Notification Composer - No singleton management.

    Responsibilities:
    - Load NotificationConfig from environment
    - Read adapter type from config
    - Delegate to NotificationFactory
    - Return notification instance

    NOT responsible for:
    - Creating adapter (factory does this)
    - Init/health check (factory does this)
    - Singleton management (DI container does this)

    Usage:
        # In DI container
        notification_service = providers.Singleton(
            NotificationModule.create_notification,
            logger=logger,
        )

        # Direct usage
        notification = await NotificationModule.create_notification(
            logger=logger,
        )
    """

    @staticmethod
    async def create_notification(
        logger: "ILogger",
    ) -> INotificationService:
        """
        Create and return notification instance.

        Flow:
        1. Load NotificationConfig from environment
        2. Read adapter type from config
        3. Delegate to NotificationFactory
        4. Return notification instance

        Args:
            logger: Logger instance

        Returns:
            Initialized notification service
        """
        notification_config = NotificationConfig()
        adapter_type = NotificationAdapterType(notification_config.NOTIFICATION_ADAPTER)

        logger.info(
            f"Creating notification service with adapter: {adapter_type.value}",
            extra={"adapter": adapter_type.value},
        )

        return await NotificationFactory.create(
            adapter_type=adapter_type,
            notification_config=notification_config,
            logger=logger,
        )
