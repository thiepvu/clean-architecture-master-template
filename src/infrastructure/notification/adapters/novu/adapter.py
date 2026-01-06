"""
Novu Notification Adapter.

Implements INotificationService using Novu notification platform.

Requirements:
    pip install novu

Novu Features:
- Multi-channel notifications (email, SMS, push, in-app, chat)
- Template management
- Subscriber management
- Topic/broadcast notifications
- Delivery tracking
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

from shared.application.ports.notification import (
    BulkNotificationResult,
    INotificationService,
    NotificationChannel,
    NotificationError,
    NotificationPayload,
    NotificationRequest,
    NotificationResult,
    NotificationSendError,
    NotificationStatus,
)

if TYPE_CHECKING:
    from novu.api import EventApi, SubscriberApi, TopicApi

    from config.notification import NovuNotificationConfig
    from shared.application.ports import ILogger


class NovuNotificationAdapter(INotificationService):
    """
    Novu notification adapter.

    Implements INotificationService using Novu platform.
    Supports multi-channel notifications with templates.

    Features:
    - Email, SMS, Push, In-App notifications
    - Template-based notifications
    - Subscriber management
    - Topic subscriptions
    - Delivery tracking
    """

    def __init__(
        self,
        config: "NovuNotificationConfig",
        logger: Optional["ILogger"] = None,
    ):
        """
        Initialize Novu notification adapter.

        Args:
            config: Novu notification configuration
            logger: Logger instance (optional)
        """
        self._config = config
        self._logger = logger
        self._initialized = False

        # Novu API clients
        self._event_api: Optional["EventApi"] = None
        self._subscriber_api: Optional["SubscriberApi"] = None
        self._topic_api: Optional["TopicApi"] = None

    async def initialize(self) -> None:
        """Initialize the Novu client."""
        if self._initialized:
            return

        if not self._config.is_configured:
            raise NotificationError(
                "Novu is not configured. Set NOVU_API_KEY environment variable."
            )

        try:
            from novu.api import EventApi, SubscriberApi, TopicApi
            from novu.config import NovuConfig

            # Configure Novu
            novu_config = NovuConfig(
                api_key=self._config.api_key,
                url=self._config.api_url,
            )

            # Initialize API clients
            self._event_api = EventApi(novu_config)
            self._subscriber_api = SubscriberApi(novu_config)
            self._topic_api = TopicApi(novu_config)

            self._initialized = True
            if self._logger:
                self._logger.info(
                    "Novu notification adapter initialized",
                    extra={"api_url": self._config.api_url or "default"},
                )
        except ImportError as e:
            raise NotificationError(
                "novu package is required for Novu notifications. " "Install with: pip install novu"
            ) from e
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to initialize Novu: {e}")
            raise NotificationError(f"Failed to initialize Novu: {e}") from e

    async def close(self) -> None:
        """Close the Novu client."""
        self._event_api = None
        self._subscriber_api = None
        self._topic_api = None
        self._initialized = False

        if self._logger:
            self._logger.info("Novu notification adapter closed")

    async def health_check(self) -> bool:
        """Check if Novu is healthy."""
        if not self._initialized or not self._subscriber_api:
            return False

        try:
            # Try to list subscribers (limit 1) to verify connectivity
            self._subscriber_api.list(page=0, limit=1)
            return True
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Novu health check failed: {e}")
            return False

    def _map_channel_to_novu(self, channel: NotificationChannel) -> str:
        """Map our channel enum to Novu channel names."""
        channel_map = {
            NotificationChannel.EMAIL: "email",
            NotificationChannel.SMS: "sms",
            NotificationChannel.PUSH: "push",
            NotificationChannel.IN_APP: "in_app",
            NotificationChannel.SLACK: "chat",
            NotificationChannel.WEBHOOK: "webhook",
        }
        return channel_map.get(channel, "email")

    async def send(self, request: NotificationRequest) -> NotificationResult:
        """
        Send a notification via Novu.

        Args:
            request: Notification request

        Returns:
            NotificationResult with status
        """
        if not self._initialized or not self._event_api:
            raise NotificationError("Novu adapter not initialized")

        notification_id = request.idempotency_key or str(uuid.uuid4())
        channel = request.channels[0] if request.channels else NotificationChannel.EMAIL

        try:
            # Build payload for Novu
            payload = {}

            if request.payload.template_variables:
                payload.update(request.payload.template_variables)

            # Add default payload data
            payload.update(
                {
                    "subject": request.payload.subject or "",
                    "body": request.payload.body,
                    "html_body": request.payload.html_body,
                }
            )

            if request.payload.data:
                payload.update(request.payload.data)

            # Determine template/event name
            template_id = request.payload.template_id or "default-notification"

            # Trigger the notification
            response = self._event_api.trigger(
                name=template_id,
                recipients=request.recipient.subscriber_id,
                payload=payload,
                transaction_id=notification_id,
            )

            now = datetime.now(timezone.utc)

            # Parse response
            provider_message_id = None
            if hasattr(response, "data") and response.data:
                provider_message_id = getattr(response.data, "transaction_id", None)

            result = NotificationResult(
                notification_id=notification_id,
                status=NotificationStatus.SENT,
                channel=channel,
                recipient_id=request.recipient.subscriber_id,
                sent_at=now,
                provider_message_id=provider_message_id,
                metadata={
                    "template_id": template_id,
                    "priority": request.priority.value,
                },
            )

            if self._logger:
                self._logger.debug(
                    f"Novu notification sent: {notification_id}",
                    extra={
                        "recipient": request.recipient.subscriber_id,
                        "template": template_id,
                    },
                )

            return result

        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to send Novu notification: {e}")

            return NotificationResult(
                notification_id=notification_id,
                status=NotificationStatus.FAILED,
                channel=channel,
                recipient_id=request.recipient.subscriber_id,
                error_message=str(e),
            )

    async def send_bulk(
        self,
        requests: list[NotificationRequest],
    ) -> BulkNotificationResult:
        """Send notifications to multiple recipients."""
        if not self._initialized or not self._event_api:
            raise NotificationError("Novu adapter not initialized")

        results = []
        successful = 0
        failed = 0

        # Group by template for efficiency
        for request in requests:
            result = await self.send(request)
            results.append(result)

            if result.status == NotificationStatus.FAILED:
                failed += 1
            else:
                successful += 1

        return BulkNotificationResult(
            total=len(requests),
            successful=successful,
            failed=failed,
            results=results,
        )

    async def send_to_topic(
        self,
        topic: str,
        payload: NotificationPayload,
        channels: Optional[list[NotificationChannel]] = None,
    ) -> BulkNotificationResult:
        """Send notification to all subscribers of a topic."""
        if not self._initialized or not self._event_api:
            raise NotificationError("Novu adapter not initialized")

        notification_id = str(uuid.uuid4())
        template_id = payload.template_id or "default-notification"

        try:
            # Build payload
            novu_payload = {}
            if payload.template_variables:
                novu_payload.update(payload.template_variables)

            novu_payload.update(
                {
                    "subject": payload.subject or "",
                    "body": payload.body,
                }
            )

            if payload.data:
                novu_payload.update(payload.data)

            # Trigger to topic
            self._event_api.broadcast(
                name=template_id,
                payload=novu_payload,
                transaction_id=notification_id,
            )

            if self._logger:
                self._logger.debug(
                    f"Novu topic notification sent: {notification_id}",
                    extra={"topic": topic, "template": template_id},
                )

            # Novu handles broadcast internally, we can't get individual results
            return BulkNotificationResult(
                total=1,  # We don't know actual count
                successful=1,
                failed=0,
                results=[
                    NotificationResult(
                        notification_id=notification_id,
                        status=NotificationStatus.SENT,
                        channel=channels[0] if channels else NotificationChannel.EMAIL,
                        recipient_id=f"topic:{topic}",
                        sent_at=datetime.now(timezone.utc),
                    )
                ],
            )

        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to send topic notification: {e}")

            return BulkNotificationResult(
                total=1,
                successful=0,
                failed=1,
                results=[
                    NotificationResult(
                        notification_id=notification_id,
                        status=NotificationStatus.FAILED,
                        channel=channels[0] if channels else NotificationChannel.EMAIL,
                        recipient_id=f"topic:{topic}",
                        error_message=str(e),
                    )
                ],
            )

    async def get_status(self, notification_id: str) -> Optional[NotificationResult]:
        """Get status of a sent notification."""
        # Novu doesn't provide a direct way to query by transaction_id
        # This would require storing notification IDs and querying activity feed
        if self._logger:
            self._logger.debug(f"get_status not fully implemented for Novu: {notification_id}")
        return None

    async def cancel(self, notification_id: str) -> bool:
        """Cancel a scheduled notification."""
        if not self._initialized or not self._event_api:
            return False

        try:
            self._event_api.delete(notification_id)
            return True
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Failed to cancel notification: {e}")
            return False

    async def subscribe(
        self,
        subscriber_id: str,
        topic: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Subscribe a user to a topic."""
        if not self._initialized or not self._topic_api:
            raise NotificationError("Novu adapter not initialized")

        try:
            # Ensure topic exists
            try:
                self._topic_api.create(key=topic, name=topic)
            except Exception:
                pass  # Topic may already exist

            # Add subscriber to topic
            self._topic_api.subscriber_addition(
                topic_key=topic,
                subscribers=[subscriber_id],
            )

            if self._logger:
                self._logger.debug(f"Subscribed {subscriber_id} to topic {topic}")

            return True
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to subscribe to topic: {e}")
            return False

    async def unsubscribe(self, subscriber_id: str, topic: str) -> bool:
        """Unsubscribe a user from a topic."""
        if not self._initialized or not self._topic_api:
            raise NotificationError("Novu adapter not initialized")

        try:
            self._topic_api.subscriber_removal(
                topic_key=topic,
                subscribers=[subscriber_id],
            )

            if self._logger:
                self._logger.debug(f"Unsubscribed {subscriber_id} from topic {topic}")

            return True
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to unsubscribe from topic: {e}")
            return False

    async def create_subscriber(
        self,
        subscriber_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Create or update a subscriber profile in Novu."""
        if not self._initialized or not self._subscriber_api:
            raise NotificationError("Novu adapter not initialized")

        try:
            from novu.dto.subscriber import SubscriberDto

            subscriber_dto = SubscriberDto(
                subscriber_id=subscriber_id,
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                data=metadata,
            )

            # Create or update subscriber
            self._subscriber_api.create(subscriber_dto)

            if self._logger:
                self._logger.debug(f"Created/updated Novu subscriber: {subscriber_id}")

            return True
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to create subscriber: {e}")
            return False

    async def delete_subscriber(self, subscriber_id: str) -> bool:
        """Delete a subscriber profile from Novu."""
        if not self._initialized or not self._subscriber_api:
            raise NotificationError("Novu adapter not initialized")

        try:
            self._subscriber_api.delete(subscriber_id)

            if self._logger:
                self._logger.debug(f"Deleted Novu subscriber: {subscriber_id}")

            return True
        except Exception as e:
            if self._logger:
                self._logger.error(f"Failed to delete subscriber: {e}")
            return False
