"""
Share File Command and Handler.

This command handles sharing a file with another user.
"""

from uuid import UUID

from shared.application.base_command import Command, CommandHandler
from shared.domain.result import Result

from ...domain.entities.file import File
from ...domain.errors.file_error_codes import FileErrorCode
from ..ports import IFileManagementUoWFactory
from ..read_models import FileReadModel


class ShareFileCommand(Command):
    """
    Command to share a file with another user.

    Attributes:
        file_id: File UUID to share
        owner_id: File owner (must match actual owner)
        target_user_id: User ID to share with
    """

    file_id: UUID
    owner_id: UUID
    target_user_id: UUID


class ShareFileHandler(CommandHandler[ShareFileCommand, FileReadModel]):
    """
    Handler for ShareFileCommand.

    Responsibilities:
    - Validate file exists
    - Validate user is owner
    - Validate not sharing with self
    - Share file with target user
    - Persist changes
    - Publish domain events
    """

    def __init__(self, uow_factory: IFileManagementUoWFactory):
        """
        Initialize handler.

        Args:
            uow_factory: Factory for creating File Management UoW instances
        """
        self._uow_factory = uow_factory

    async def handle(self, command: ShareFileCommand) -> Result[FileReadModel]:
        """Handle the share file command."""
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
            if file.owner_id != command.owner_id:
                return Result.fail(
                    code=FileErrorCode.FILE_ACCESS_DENIED.value,
                    message="Only the file owner can share the file",
                )

            # 3. Validate not sharing with self
            if command.target_user_id == command.owner_id:
                return Result.fail(
                    code=FileErrorCode.CANNOT_SHARE_OWN_FILE.value,
                    message="Cannot share file with yourself",
                )

            # 4. Check if already shared
            if command.target_user_id in file.shared_with:
                return Result.fail(
                    code=FileErrorCode.FILE_ALREADY_SHARED.value,
                    message=f"File is already shared with user {command.target_user_id}",
                )

            # 5. Share file
            file.share_with(command.target_user_id)

            # 6. Persist changes
            updated_file = await uow.files.update(file)
            uow.track(updated_file)
            await uow.commit()

        # Return success result with read model
        return Result.ok(self._to_read_model(updated_file))

    def _to_read_model(self, file: File) -> FileReadModel:
        """Convert domain entity to read model."""
        return FileReadModel(
            id=file.id,
            name=file.name,
            original_name=file.original_name,
            path=file.path.value,
            size=file.size.bytes,
            mime_type=file.mime_type.value,
            owner_id=file.owner_id,
            description=file.description,
            is_public=file.is_public,
            download_count=file.download_count,
            shared_with=file.shared_with,
            is_deleted=file.is_deleted,
            created_at=file.created_at,
            updated_at=file.updated_at,
        )
