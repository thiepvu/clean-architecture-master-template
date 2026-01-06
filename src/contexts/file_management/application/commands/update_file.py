"""
Update File Command and Handler.

This command handles file metadata updates.
"""

from typing import Optional
from uuid import UUID

from shared.application.base_command import Command, CommandHandler
from shared.domain.result import Result

from ...domain.entities.file import File
from ...domain.errors.file_error_codes import FileErrorCode
from ..ports import IFileManagementUoWFactory
from ..read_models import FileReadModel


class UpdateFileCommand(Command):
    """
    Command to update file metadata.

    Attributes:
        file_id: File UUID to update
        user_id: User performing the update (must be owner)
        original_name: New original filename (optional)
        description: New description (optional)
        is_public: New visibility setting (optional)
    """

    file_id: UUID
    user_id: UUID
    original_name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class UpdateFileHandler(CommandHandler[UpdateFileCommand, FileReadModel]):
    """
    Handler for UpdateFileCommand.

    Responsibilities:
    - Validate file exists
    - Validate user is owner
    - Update file metadata
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

    async def handle(self, command: UpdateFileCommand) -> Result[FileReadModel]:
        """Handle the update file command."""
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
                    message="Only the file owner can update file metadata",
                )

            # 3. Update metadata if provided
            if command.original_name is not None or command.description is not None:
                file.update_metadata(
                    original_name=command.original_name,
                    description=command.description,
                )

            # 4. Update visibility if provided
            if command.is_public is not None:
                if command.is_public:
                    file.make_public()
                else:
                    file.make_private()

            # 5. Persist changes
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
