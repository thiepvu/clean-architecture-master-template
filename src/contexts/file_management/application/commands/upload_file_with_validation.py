"""
Upload File With User Validation Command and Handler.

This demonstrates cross-context communication via CQRS:
- File Management needs to verify user exists before upload
- Uses Query Bus instead of direct User Management dependency
- Follows Anti-Corruption Layer pattern

Example 5: Sync dependency giữa User và File qua CQRS (không Facade)
"""

import uuid as uuid_lib
from pathlib import Path
from typing import TYPE_CHECKING, Optional
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
from ..services import UserVerificationService

if TYPE_CHECKING:
    from shared.application.ports import ILogger


class UploadFileWithValidationCommand(Command):
    """
    Command to upload a new file with user validation.

    Unlike basic UploadFileCommand, this validates user via Query Bus
    before proceeding with upload.

    Attributes:
        original_name: Original filename
        content: File content as bytes
        mime_type: MIME type
        owner_id: Owner user ID (will be validated)
        description: Optional file description
        is_public: Whether file is public
    """

    original_name: str
    content: bytes
    mime_type: str
    owner_id: UUID
    description: Optional[str] = None
    is_public: bool = False


class UploadFileWithValidationHandler(
    CommandHandler[UploadFileWithValidationCommand, FileReadModel]
):
    """
    Handler for UploadFileWithValidationCommand.

    Cross-Context Communication Flow:
    1. Receive upload command with owner_id
    2. Use UserVerificationService to verify user via Query Bus
    3. Query Bus routes to User Management BC
    4. If user valid, proceed with file upload
    5. If user invalid, return error

    This demonstrates:
    - Loose coupling between bounded contexts
    - CQRS for cross-context queries
    - Anti-Corruption Layer (UserInfo mapping)
    - No direct imports from User Management internals
    """

    def __init__(
        self,
        uow_factory: IFileManagementUoWFactory,
        storage_service: IStorageService,
        user_verification_service: UserVerificationService,
        logger: "ILogger",
    ):
        """
        Initialize handler.

        Args:
            uow_factory: Factory for creating File Management UoW instances
            storage_service: Service for file storage operations
            user_verification_service: Service for verifying users via Query Bus
            logger: Logger instance
        """
        self._uow_factory = uow_factory
        self._storage_service = storage_service
        self._user_verification_service = user_verification_service
        self._logger = logger

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

    async def handle(self, command: UploadFileWithValidationCommand) -> Result[FileReadModel]:
        """
        Handle the upload file command with user validation.

        Args:
            command: UploadFileWithValidationCommand with file data

        Returns:
            Result containing FileReadModel on success, or error on failure
        """
        # Step 1: Verify user via Query Bus (cross-context communication)
        user_result = await self._verify_owner(command.owner_id)
        if user_result.is_failure:
            return user_result

        user_info = user_result.value

        self._logger.info(
            f"Uploading file for verified user: {user_info.email} " f"(ID: {user_info.user_id})"
        )

        try:
            # Step 2: Generate unique filename
            unique_name = self._generate_unique_filename(command.original_name)

            # Step 3: Build storage path and save file
            storage_path = f"{command.owner_id}/{unique_name}"
            storage_file = await self._storage_service.save_bytes(
                content=command.content,
                path=storage_path,
                content_type=command.mime_type,
            )

            # Step 4: Create file entity (validates size and type)
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

            # Step 5: Persist in transaction using UoW
            async with self._uow_factory.create() as uow:
                saved_file = await uow.files.add(file)
                uow.track(saved_file)
                await uow.commit()

            # Step 6: Return success result
            self._logger.info(
                f"File uploaded successfully: {saved_file.id} " f"for user {user_info.email}"
            )
            return Result.ok(FileMapper.to_read_model(saved_file))

        except FileSizeLimitExceededException as e:
            return Result.from_exception(e, FileErrorCode.FILE_SIZE_EXCEEDED.value)

        except (InvalidFileTypeException, InvalidMimeTypeException) as e:
            return Result.from_exception(e, FileErrorCode.FILE_TYPE_NOT_ALLOWED.value)

        except Exception as e:
            self._logger.error(f"File upload failed: {e}")
            return Result.fail(
                code=FileErrorCode.FILE_UPLOAD_FAILED.value,
                message=f"Failed to upload file: {e}",
            )

    async def _verify_owner(self, owner_id: UUID) -> Result:
        """
        Verify the file owner via Query Bus.

        This method demonstrates cross-context communication:
        - File Management doesn't know about User Management internals
        - Uses Query Bus as communication channel
        - Maps result to local representation

        Args:
            owner_id: User ID to verify

        Returns:
            Result containing UserInfo or error
        """
        from ..services.user_verification_service import UserInactiveError, UserNotFoundError

        try:
            user_info = await self._user_verification_service.verify_user(owner_id)
            return Result.ok(user_info)

        except UserNotFoundError:
            self._logger.warning(f"Upload rejected: User {owner_id} not found")
            return Result.fail(
                code=FileErrorCode.FILE_UPLOAD_FAILED.value,
                message=f"Owner user {owner_id} not found",
            )

        except UserInactiveError:
            self._logger.warning(f"Upload rejected: User {owner_id} is inactive")
            return Result.fail(
                code=FileErrorCode.FILE_UPLOAD_FAILED.value,
                message=f"Owner user {owner_id} is inactive and cannot upload files",
            )

        except Exception as e:
            self._logger.error(f"Error verifying user: {e}")
            return Result.fail(
                code=FileErrorCode.FILE_UPLOAD_FAILED.value,
                message=f"Failed to verify owner: {e}",
            )
