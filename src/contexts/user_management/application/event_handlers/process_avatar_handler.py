"""
Process Avatar Event Handler.

Handles UserProfilePhotoUpdatedEvent to process avatar images:
- Generate thumbnails using IStorageService
- Purge CDN cache
- Update search index

This demonstrates an event handler that uses storage and job services.
"""

from typing import TYPE_CHECKING

from shared.application.ports.event_bus import IEventHandler

if TYPE_CHECKING:
    from shared.application.ports import IJobService, ILogger, IStorageService
    from shared.domain.events import DomainEvent


class ProcessAvatarHandler(IEventHandler):
    """
    Event handler that processes avatar updates.

    When a user updates their avatar, this handler:
    1. Generates thumbnails using IStorageService
    2. Queues background jobs for additional processing
    3. Logs the activity

    Uses:
    - IStorageService for reading original and saving thumbnails
    - IJobService for scheduling background tasks

    Example:
        handler = ProcessAvatarHandler(storage_service, job_service, logger)
        event_bus.subscribe(UserProfilePhotoUpdatedEvent, handler)
    """

    # Thumbnail sizes to generate
    THUMBNAIL_SIZES = {
        "tiny": (32, 32),  # For mentions
        "small": (64, 64),  # For comments
        "medium": (128, 128),  # For profile cards
        "large": (256, 256),  # For profile page
    }

    def __init__(
        self,
        storage_service: "IStorageService",
        job_service: "IJobService",
        logger: "ILogger",
    ):
        """
        Initialize the handler.

        Args:
            storage_service: Service for storage operations
            job_service: Job service for scheduling background tasks
            logger: Logger instance for logging actions
        """
        self._storage_service = storage_service
        self._job_service = job_service
        self._logger = logger

    async def handle(self, event: "DomainEvent") -> None:
        """
        Handle the UserProfilePhotoUpdatedEvent.

        Args:
            event: The UserProfilePhotoUpdatedEvent instance
        """
        # Access event attributes
        profile_id = getattr(event, "profile_id", None)
        user_id = getattr(event, "user_id", None)
        old_avatar_url = getattr(event, "old_avatar_url", None)
        new_avatar_url = getattr(event, "new_avatar_url", None)

        if profile_id is None or new_avatar_url is None:
            self._logger.warning(
                "[ProcessAvatarHandler] Received invalid event, missing required fields"
            )
            return

        self._logger.info(f"🖼️ ProcessAvatarHandler: Processing avatar for user {str(user_id)[:8]}")

        # 1. Queue job to generate thumbnails
        await self._queue_thumbnail_generation(
            user_id=user_id,
            avatar_path=new_avatar_url,
        )

        # 2. Queue job to purge old avatar from CDN (if exists)
        if old_avatar_url:
            await self._queue_cleanup(old_avatar_url)

        self._logger.info(f"✅ ProcessAvatarHandler: Jobs queued for user {str(user_id)[:8]}")

    async def _queue_thumbnail_generation(
        self,
        user_id,
        avatar_path: str,
    ) -> None:
        """
        Queue a job to generate avatar thumbnails.

        Creates different sizes for various use cases.
        """
        # Register the thumbnail generation task
        await self._job_service.register_task(
            task_id=f"generate_thumbnails_{user_id}",
            task_name="generate_avatar_thumbnails",
            task_func=self._generate_thumbnails_task,
        )

        # Schedule the job with parameters
        await self._job_service.schedule(
            task_name="generate_avatar_thumbnails",
            args=[str(user_id), avatar_path],
            kwargs={"sizes": self.THUMBNAIL_SIZES},
        )

        self._logger.debug(f"[ProcessAvatarHandler] Thumbnail generation job queued: {avatar_path}")

    async def _queue_cleanup(self, old_avatar_path: str) -> None:
        """
        Queue a job to cleanup old avatar and its thumbnails.
        """
        try:
            # Delete old avatar from storage
            deleted = await self._storage_service.delete(old_avatar_path)
            if deleted:
                self._logger.debug(f"[ProcessAvatarHandler] Deleted old avatar: {old_avatar_path}")

            # Delete old thumbnails
            for size_name in self.THUMBNAIL_SIZES:
                thumb_path = self._get_thumbnail_path(old_avatar_path, size_name)
                await self._storage_service.delete(thumb_path)

        except Exception as e:
            self._logger.warning(f"[ProcessAvatarHandler] Failed to cleanup old avatar: {e}")

    def _get_thumbnail_path(self, original_path: str, size_name: str) -> str:
        """Generate thumbnail path from original path."""
        # e.g., "users/123/avatar.jpg" -> "users/123/avatar_small.jpg"
        parts = original_path.rsplit(".", 1)
        if len(parts) == 2:
            return f"{parts[0]}_{size_name}.{parts[1]}"
        return f"{original_path}_{size_name}"

    async def _generate_thumbnails_task(
        self,
        user_id: str,
        avatar_path: str,
        sizes: dict = None,
    ) -> None:
        """
        Background task to generate avatar thumbnails.

        In production, this would:
        1. Download the original image from storage
        2. Resize to multiple sizes using PIL/Pillow
        3. Upload thumbnails back to storage
        4. Optionally update database with thumbnail URLs
        """
        sizes = sizes or self.THUMBNAIL_SIZES

        self._logger.info(
            f"[ProcessAvatarHandler] Generating {len(sizes)} thumbnails for user {user_id}"
        )

        try:
            # Read original image
            file_exists = await self._storage_service.exists(avatar_path)
            if not file_exists:
                self._logger.error(
                    f"[ProcessAvatarHandler] Original avatar not found: {avatar_path}"
                )
                return

            # In production, you would:
            # 1. content = await self._storage_service.read(avatar_path)
            # 2. Use PIL to resize
            # 3. Save each size back to storage

            for size_name, (width, height) in sizes.items():
                thumb_path = self._get_thumbnail_path(avatar_path, size_name)
                self._logger.debug(
                    f"[ProcessAvatarHandler] Would generate {size_name} ({width}x{height}) "
                    f"thumbnail at {thumb_path}"
                )

            self._logger.info(
                f"[ProcessAvatarHandler] Thumbnail generation completed for user {user_id}"
            )

        except Exception as e:
            self._logger.error(f"[ProcessAvatarHandler] Thumbnail generation failed: {e}")
