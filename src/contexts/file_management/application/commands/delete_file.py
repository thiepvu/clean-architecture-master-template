"""
Delete File Command and Handler.

This command handles soft delete of files and removes them from storage.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from shared.application.base_command import Command, CommandHandler
from shared.domain.result import Result

from ...domain.errors.file_error_codes import FileErrorCode
from ..ports import IFileManagementUoWFactory

if TYPE_CHECKING:
    from shared.application.ports import ILogger, IStorageService


class DeleteFileCommand(Command):
    """
    Command to delete a file (soft delete).

    Attributes:
        file_id: File UUID to delete
        user_id: User performing the delete (must be owner)
        hard_delete: If True, also remove from storage (default: False)
    """

    file_id: UUID
    user_id: UUID
    hard_delete: bool = False


class DeleteFileHandler(CommandHandler[DeleteFileCommand, None]):
    """
    Handler for DeleteFileCommand.

    Responsibilities:
    - Validate file exists
    - Validate user is owner
    - Soft delete file in database
    - Optionally remove from storage (hard delete)
    - Persist changes
    - Publish domain events
    """

    def __init__(
        self,
        uow_factory: IFileManagementUoWFactory,
        storage_service: "IStorageService",
        logger: "ILogger",
    ):
        """
        Initialize handler.

        Args:
            uow_factory: Factory for creating File Management UoW instances
            storage_service: Service for storage operations
            logger: Logger instance
        """
        self._uow_factory = uow_factory
        self._storage_service = storage_service
        self._logger = logger

    async def handle(self, command: DeleteFileCommand) -> Result[None]:
        """Handle the delete file command."""
        # All repository operations inside UoW context
        async with self._uow_factory.create() as uow:
            # 1. Get existing file
            file = await uow.files.get_by_id(command.file_id)
            if file is None:
                return Result.fail(
                    code=FileErrorCode.FILE_NOT_FOUND.value,
                    message=f"File with ID {command.file_id} not found",
                )

            # 2. Validate user is owner
            if file.owner_id != command.user_id:
                return Result.fail(
                    code=FileErrorCode.FILE_ACCESS_DENIED.value,
                    message="Only the file owner can delete the file",
                )

            # 3. Store path before soft delete for potential storage cleanup
            storage_path = file.path

            # 4. Soft delete in database
            file.soft_delete()

            # 5. Persist changes
            await uow.files.update(file)
            uow.track(file)
            await uow.commit()

            self._logger.info(f"🗑️ DeleteFileHandler: Soft deleted file {str(command.file_id)[:8]}")

        # 6. Hard delete from storage if requested (outside transaction)
        if command.hard_delete:
            try:
                deleted = await self._storage_service.delete(
                    storage_path.value if hasattr(storage_path, "value") else str(storage_path)
                )
                if deleted:
                    self._logger.info(f"🗑️ DeleteFileHandler: Removed from storage: {storage_path}")
                else:
                    self._logger.warning(
                        f"🗑️ DeleteFileHandler: File not found in storage: {storage_path}"
                    )
            except Exception as e:
                # Log but don't fail - DB record already deleted
                self._logger.error(f"🗑️ DeleteFileHandler: Failed to remove from storage: {e}")

        return Result.ok(None)
