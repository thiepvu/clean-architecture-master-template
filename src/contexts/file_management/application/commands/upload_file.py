"""
Upload File Command and Handler.

This command handles file upload operations.
"""

import uuid as uuid_lib
from pathlib import Path
from typing import Optional
from uuid import UUID

from shared.application.base_command import Command, CommandHandler
from shared.application.ports import IStorageService
from shared.domain.result import Result

from ...domain.entities.file import File
from ...domain.errors.file_error_codes import FileErrorCode
from ...domain.exceptions import (
    FileSizeLimitExceededException,
    InvalidFileTypeException,
    InvalidMimeTypeException,
)
from ..dto.mappers import FileMapper
from ..ports import IFileManagementUoWFactory
from ..read_models import FileReadModel


class UploadFileCommand(Command):
    """
    Command to upload a new file.

    Attributes:
        original_name: Original filename
        content: File content as bytes
        mime_type: MIME type
        owner_id: Owner user ID
        description: Optional file description
        is_public: Whether file is public
    """

    original_name: str
    content: bytes
    mime_type: str
    owner_id: UUID
    description: Optional[str] = None
    is_public: bool = False


class UploadFileHandler(CommandHandler[UploadFileCommand, FileReadModel]):
    """
    Handler for UploadFileCommand.

    Responsibilities:
    - Validate file size and type
    - Generate unique filename
    - Save file to storage
    - Create file entity
    - Persist to database
    - Publish domain events
    """

    def __init__(
        self,
        uow_factory: IFileManagementUoWFactory,
        storage_service: IStorageService,
    ):
        """
        Initialize handler.

        Args:
            uow_factory: Factory for creating File Management UoW instances
            storage_service: Service for file storage operations
        """
        self._uow_factory = uow_factory
        self._storage_service = storage_service

    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename while preserving extension.

        Args:
            original_filename: Original filename

        Returns:
            Unique filename with UUID
        """
        extension = Path(original_filename).suffix
        return f"{uuid_lib.uuid4()}{extension}"

    async def handle(self, command: UploadFileCommand) -> Result[FileReadModel]:
        """
        Handle the upload file command.

        Args:
            command: UploadFileCommand with file data

        Returns:
            Result containing FileReadModel on success, or error on failure
        """
        try:
            # 1. Generate unique filename
            unique_name = self._generate_unique_filename(command.original_name)

            # 2. Build storage path: owner_id/filename
            storage_path = f"{command.owner_id}/{unique_name}"

            # 3. Save file to storage using IStorageService
            storage_file = await self._storage_service.save_bytes(
                content=command.content,
                path=storage_path,
                content_type=command.mime_type,
            )

            # 4. Create file entity (validates size and type)
            file = File.create(
                name=unique_name,
                original_name=command.original_name,
                path=storage_file.path,
                size=len(command.content),
                mime_type=command.mime_type,
                owner_id=command.owner_id,
                description=command.description,
                is_public=command.is_public,
            )

            # 5. Persist in transaction using UoW with repository
            async with self._uow_factory.create() as uow:
                saved_file = await uow.files.add(file)
                uow.track(saved_file)
                await uow.commit()

            # 6. Return success result with read model
            return Result.ok(FileMapper.to_read_model(saved_file))

        except FileSizeLimitExceededException as e:
            return Result.from_exception(e, FileErrorCode.FILE_SIZE_EXCEEDED.value)

        except (InvalidFileTypeException, InvalidMimeTypeException) as e:
            return Result.from_exception(e, FileErrorCode.FILE_TYPE_NOT_ALLOWED.value)

        except Exception as e:
            return Result.fail(
                code=FileErrorCode.FILE_UPLOAD_FAILED.value,
                message=f"Failed to upload file: {e}",
            )
