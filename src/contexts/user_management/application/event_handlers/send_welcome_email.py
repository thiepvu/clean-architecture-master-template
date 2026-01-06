"""
Send Welcome Email Event Handler.

Handles UserCreatedEvent by sending a welcome email to the new user.
Uses INotificationService for sending emails via configured adapter.
"""

from typing import TYPE_CHECKING

from shared.application.ports.event_bus import IEventHandler
from shared.application.ports.notification import (
    NotificationChannel,
    NotificationPayload,
    NotificationRecipient,
    NotificationRequest,
    NotificationSendError,
    NotificationStatus,
)

if TYPE_CHECKING:
    from contexts.user_management.domain.events import UserCreatedEvent
    from shared.application.ports import ILogger, INotificationService
    from shared.domain.events import DomainEvent


class SendWelcomeEmailHandler(IEventHandler):
    """
    Event handler that sends welcome email when a user is created.

    This handler:
    1. Receives UserCreatedEvent from Event Bus
    2. Creates subscriber in notification service
    3. Sends welcome email via INotificationService
    4. Logs the action

    Uses INotificationService which can be backed by:
    - InMemoryNotificationAdapter (development/testing)
    - NovuNotificationAdapter (production)

    Example:
        handler = SendWelcomeEmailHandler(notification_service, logger)
        event_bus.subscribe(UserCreatedEvent, handler)
    """

    def __init__(
        self,
        notification_service: "INotificationService",
        logger: "ILogger",
    ):
        """
        Initialize the handler.

        Args:
            notification_service: Service for sending notifications
            logger: Logger instance for logging actions
        """
        self._notification_service = notification_service
        self._logger = logger

    async def handle(self, event: "DomainEvent") -> None:
        """
        Handle the UserCreatedEvent by sending a welcome email.

        Args:
            event: The UserCreatedEvent instance
        """
        # Type narrowing for IDE support
        user_event: "UserCreatedEvent" = event  # type: ignore

        user_id = user_event.user_id
        email = user_event.email

        try:
            # 1. Create/update subscriber in notification service
            await self._notification_service.create_subscriber(
                subscriber_id=str(user_id),
                email=email,
            )

            # 2. Build notification request
            request = NotificationRequest(
                recipient=NotificationRecipient(
                    subscriber_id=str(user_id),
                    email=email,
                ),
                payload=NotificationPayload(
                    subject="Welcome to Clean Architecture!",
                    body="Hello! Your account has been created successfully.",
                    html_body=f"""
                        <h1>Welcome!</h1>
                        <p>Your account has been created successfully.</p>
                        <p>User ID: {str(user_id)[:8]}...</p>
                    """,
                    template_id="welcome-email",  # For Novu template
                    template_variables={
                        "user_id": str(user_id),
                        "email": email,
                    },
                ),
                channels=[NotificationChannel.EMAIL],
                idempotency_key=f"welcome-{user_id}",
            )

            # 3. Send notification
            result = await self._notification_service.send(request)

            if result.status == NotificationStatus.FAILED:
                self._logger.error(
                    f"📧 SendWelcomeEmailHandler: Failed to send to {email} - "
                    f"{result.error_message}"
                )
            else:
                self._logger.info(
                    f"📧 SendWelcomeEmailHandler: Sent welcome email to {email} "
                    f"(user_id={str(user_id)[:8]}, notification_id={result.notification_id[:8]})"
                )

        except NotificationSendError as e:
            self._logger.error(f"📧 SendWelcomeEmailHandler: Error sending to {email} - {e}")
        except Exception as e:
            self._logger.error(f"📧 SendWelcomeEmailHandler: Unexpected error for {email} - {e}")
