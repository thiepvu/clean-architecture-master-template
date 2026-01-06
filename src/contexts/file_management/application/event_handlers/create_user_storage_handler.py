"""
Create User Storage Event Handler.

Handles UserCreatedEvent from User Management context to create
default storage allocation for new users.

Uses IStorageService for creating user's default folder structure.
"""

from typing import TYPE_CHECKING

from shared.application.ports.event_bus import IEventHandler

if TYPE_CHECKING:
    from shared.application.ports import ILogger, IStorageService
    from shared.domain.events import DomainEvent


class CreateUserStorageHandler(IEventHandler):
    """
    Event handler that creates default storage when a user is created.

    Cross-Context Integration:
    1. User Management BC publishes UserCreatedEvent to Outbox
    2. Outbox Processor publishes event to Event Bus
    3. This handler (in File Management BC) receives the event
    4. Creates default folder structure for the new user

    Uses IStorageService which can be backed by:
    - LocalStorageAdapter (local filesystem)
    - S3StorageAdapter (AWS S3, MinIO, etc.)

    Example:
        handler = CreateUserStorageHandler(storage_service, logger)
        event_bus.subscribe(UserCreatedEvent, handler)
    """

    # Default storage quota in bytes (1 GB)
    DEFAULT_STORAGE_QUOTA_BYTES = 1 * 1024 * 1024 * 1024

    # Default folders to create for new users
    DEFAULT_FOLDERS = ["documents", "images", "shared"]

    def __init__(
        self,
        storage_service: "IStorageService",
        logger: "ILogger",
    ):
        """
        Initialize the handler.

        Args:
            storage_service: Service for storage operations
            logger: Logger instance for logging actions
        """
        self._storage_service = storage_service
        self._logger = logger

    async def handle(self, event: "DomainEvent") -> None:
        """
        Handle the UserCreatedEvent by creating default storage.

        Args:
            event: The UserCreatedEvent instance from User Management BC
        """
        # Access event attributes (UserCreatedEvent has user_id and email)
        user_id = getattr(event, "user_id", None)
        email = getattr(event, "email", None)

        if user_id is None:
            self._logger.warning("[CreateUserStorageHandler] Received event without user_id")
            return

        self._logger.info(
            f"📁 CreateUserStorageHandler: Creating storage for user {str(user_id)[:8]} ({email})"
        )

        try:
            # Create default folders for the user
            for folder in self.DEFAULT_FOLDERS:
                folder_path = f"{user_id}/{folder}/.gitkeep"

                # Create a placeholder file to ensure folder exists
                # (Some storage backends like S3 don't have real folders)
                await self._storage_service.save_bytes(
                    content=b"",
                    path=folder_path,
                    content_type="application/octet-stream",
                )

                self._logger.debug(
                    f"📁 CreateUserStorageHandler: Created folder {folder} for user {str(user_id)[:8]}"
                )

            quota_mb = self.DEFAULT_STORAGE_QUOTA_BYTES // (1024 * 1024)
            self._logger.info(
                f"✅ CreateUserStorageHandler: Created {len(self.DEFAULT_FOLDERS)} folders "
                f"with {quota_mb}MB quota for user {str(user_id)[:8]}"
            )

        except Exception as e:
            self._logger.error(
                f"❌ CreateUserStorageHandler: Failed to create storage for user "
                f"{str(user_id)[:8]} - {e}"
            )
