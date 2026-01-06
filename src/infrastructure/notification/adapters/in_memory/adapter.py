"""
In-Memory Notification Adapter.

Implements INotificationService for development and testing.
Stores notifications in memory with optional TTL cleanup.
"""

import asyncio
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Optional

from shared.application.ports.notification import (
    BulkNotificationResult,
    INotificationService,
    NotificationChannel,
    NotificationPayload,
    NotificationRequest,
    NotificationResult,
    NotificationStatus,
)

if TYPE_CHECKING:
    from config.notification import InMemoryNotificationConfig
    from shared.application.ports import ILogger


class InMemoryNotificationAdapter(INotificationService):
    """
    In-memory notification adapter.

    Implements INotificationService for development and testing.
    Stores notifications in memory with configurable retention.

    Features:
    - Simple in-memory storage
    - Automatic cleanup of old notifications
    - Topic-based subscriptions
    - Useful for testing and development
    """

    def __init__(
        self,
        config: "InMemoryNotificationConfig",
        logger: Optional["ILogger"] = None,
    ):
        """
        Initialize in-memory notification adapter.

        Args:
            config: In-memory notification configuration
            logger: Logger instance (optional)
        """
        self._config = config
        self._logger = logger
        self._initialized = False

        # Storage
        self._notifications: dict[str, NotificationResult] = {}
        self._subscribers: dict[str, dict[str, Any]] = {}  # subscriber_id -> data
        self._topic_subscriptions: dict[str, set[str]] = defaultdict(set)  # topic -> subscriber_ids

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize the notification service."""
        if self._initialized:
            return

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        self._initialized = True
        if self._logger:
            self._logger.info(
                "In-memory notification adapter initialized",
                extra={"max_queue_size": self._config.max_queue_size},
            )

    async def close(self) -> None:
        """Close the notification service."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

        self._notifications.clear()
        self._subscribers.clear()
        self._topic_subscriptions.clear()
        self._initialized = False

        if self._logger:
            self._logger.info("In-memory notification adapter closed")

    async def health_check(self) -> bool:
        """Check if notification service is healthy."""
        return self._initialized

    async def _cleanup_loop(self) -> None:
        """Background task to cleanup old notifications."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_notifications()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Error in notification cleanup: {e}")

    async def _cleanup_old_notifications(self) -> None:
        """Remove notifications older than retention period."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self._config.retention_hours)
        to_remove = []

        for notification_id, result in self._notifications.items():
            if result.sent_at and result.sent_at < cutoff:
                to_remove.append(notification_id)

        for notification_id in to_remove:
            del self._notifications[notification_id]

        if to_remove and self._logger:
            self._logger.debug(f"Cleaned up {len(to_remove)} old notifications")

    async def send(self, request: NotificationRequest) -> NotificationResult:
        """
        Send a notification.

        Args:
            request: Notification request

        Returns:
            NotificationResult with status
        """
        notification_id = str(uuid.uuid4())
        channel = request.channels[0] if request.channels else NotificationChannel.EMAIL

        # Check if channel is enabled
        if channel.value not in self._config.enabled_channels:
            result = NotificationResult(
                notification_id=notification_id,
                status=NotificationStatus.FAILED,
                channel=channel,
                recipient_id=request.recipient.subscriber_id,
                error_message=f"Channel {channel.value} is not enabled",
            )
            self._notifications[notification_id] = result
            return result

        now = datetime.now(timezone.utc)

        # Simulate sending (in-memory just stores it)
        result = NotificationResult(
            notification_id=notification_id,
            status=NotificationStatus.SENT,
            channel=channel,
            recipient_id=request.recipient.subscriber_id,
            sent_at=now,
            delivered_at=now,  # Immediate "delivery" for in-memory
            metadata={
                "subject": request.payload.subject,
                "template_id": request.payload.template_id,
                "priority": request.priority.value,
            },
        )

        # Enforce max queue size
        if len(self._notifications) >= self._config.max_queue_size:
            # Remove oldest
            oldest_id = next(iter(self._notifications))
            del self._notifications[oldest_id]

        self._notifications[notification_id] = result

        if self._logger:
            self._logger.debug(
                f"Notification sent (in-memory): {notification_id}",
                extra={
                    "recipient": request.recipient.subscriber_id,
                    "channel": channel.value,
                },
            )

        return result

    async def send_bulk(
        self,
        requests: list[NotificationRequest],
    ) -> BulkNotificationResult:
        """Send notifications to multiple recipients."""
        results = []
        successful = 0
        failed = 0

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
        subscriber_ids = self._topic_subscriptions.get(topic, set())

        if not subscriber_ids:
            return BulkNotificationResult(total=0, successful=0, failed=0, results=[])

        requests = []
        for subscriber_id in subscriber_ids:
            subscriber = self._subscribers.get(subscriber_id, {})
            from shared.application.ports.notification import NotificationRecipient

            request = NotificationRequest(
                recipient=NotificationRecipient(
                    subscriber_id=subscriber_id,
                    email=subscriber.get("email"),
                    phone=subscriber.get("phone"),
                ),
                payload=payload,
                channels=channels or [NotificationChannel.EMAIL],
            )
            requests.append(request)

        return await self.send_bulk(requests)

    async def get_status(self, notification_id: str) -> Optional[NotificationResult]:
        """Get status of a sent notification."""
        return self._notifications.get(notification_id)

    async def cancel(self, notification_id: str) -> bool:
        """Cancel a scheduled notification."""
        if notification_id in self._notifications:
            result = self._notifications[notification_id]
            if result.status == NotificationStatus.PENDING:
                result.status = NotificationStatus.FAILED
                result.error_message = "Cancelled"
                return True
        return False

    async def subscribe(
        self,
        subscriber_id: str,
        topic: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Subscribe a user to a topic."""
        self._topic_subscriptions[topic].add(subscriber_id)

        if self._logger:
            self._logger.debug(f"Subscribed {subscriber_id} to topic {topic}")

        return True

    async def unsubscribe(self, subscriber_id: str, topic: str) -> bool:
        """Unsubscribe a user from a topic."""
        if topic in self._topic_subscriptions:
            self._topic_subscriptions[topic].discard(subscriber_id)

            if self._logger:
                self._logger.debug(f"Unsubscribed {subscriber_id} from topic {topic}")

            return True
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
        """Create or update a subscriber profile."""
        self._subscribers[subscriber_id] = {
            "email": email,
            "phone": phone,
            "first_name": first_name,
            "last_name": last_name,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc),
        }

        if self._logger:
            self._logger.debug(f"Created/updated subscriber: {subscriber_id}")

        return True

    async def delete_subscriber(self, subscriber_id: str) -> bool:
        """Delete a subscriber profile."""
        if subscriber_id in self._subscribers:
            del self._subscribers[subscriber_id]

            # Remove from all topics
            for topic_subscribers in self._topic_subscriptions.values():
                topic_subscribers.discard(subscriber_id)

            if self._logger:
                self._logger.debug(f"Deleted subscriber: {subscriber_id}")

            return True
        return False

    # Helper methods for testing
    def get_all_notifications(self) -> list[NotificationResult]:
        """Get all stored notifications (for testing)."""
        return list(self._notifications.values())

    def get_notifications_for_recipient(self, subscriber_id: str) -> list[NotificationResult]:
        """Get notifications for a specific recipient (for testing)."""
        return [n for n in self._notifications.values() if n.recipient_id == subscriber_id]

    def clear_all(self) -> None:
        """Clear all stored data (for testing)."""
        self._notifications.clear()
        self._subscribers.clear()
        self._topic_subscriptions.clear()
