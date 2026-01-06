"""
File Management Controller.

Handles HTTP requests for file operations using CQRS pattern.
All write operations go through Command Bus, read operations through Query Bus.
"""

import io
from typing import Optional
from uuid import UUID

from fastapi import UploadFile
from fastapi.responses import StreamingResponse

# Import from context public API
from contexts.file_management import (  # Commands; Queries; Read Models
    DeleteFileCommand,
    FileListItemReadModel,
    FileReadModel,
    GetFileByIdQuery,
    GetFileDownloadQuery,
    ListFilesQuery,
    PaginatedFilesReadModel,
    ShareFileCommand,
    UpdateFileCommand,
    UploadFileCommand,
)
from shared.presentation import ApiResponse, BaseController, PaginatedResponse, PaginationParams

from ..dependencies import CommandBusDep, QueryBusDep
from ..schemas import ShareFileRequest, UpdateFileRequest


class FileController(BaseController):
    """
    File API controller using CQRS pattern.

    Write Operations (Commands):
    - upload_file → UploadFileCommand
    - update_file → UpdateFileCommand
    - delete_file → DeleteFileCommand
    - share_file → ShareFileCommand

    Read Operations (Queries):
    - get_file → GetFileByIdQuery
    - list_files → ListFilesQuery
    - download_file → GetFileDownloadQuery
    """

    def __init__(self):
        super().__init__()

    # ========================================================================
    # WRITE OPERATIONS - Commands via Command Bus
    # ========================================================================

    async def upload_file(
        self,
        file: UploadFile,
        description: Optional[str],
        is_public: bool,
        user_id: UUID,
        command_bus: CommandBusDep,
    ) -> ApiResponse[FileReadModel]:
        """
        Upload a new file.

        Args:
            file: Uploaded file
            description: File description
            is_public: Public access flag
            user_id: Current user ID (TODO: from auth)
            command_bus: Command bus (auto-injected)

        Returns:
            Uploaded file response
        """
        # Read file content
        file_content = await file.read()

        # Create command
        command = UploadFileCommand(
            original_name=file.filename or "unnamed",
            content=file_content,
            mime_type=file.content_type or "application/octet-stream",
            owner_id=user_id,
            description=description,
            is_public=is_public,
        )

        # Execute command
        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.created(result.value, "File uploaded successfully")

    async def update_file(
        self,
        file_id: UUID,
        request: UpdateFileRequest,
        user_id: UUID,
        command_bus: CommandBusDep,
    ) -> ApiResponse[FileReadModel]:
        """
        Update file metadata.

        Args:
            file_id: File UUID
            request: Update request data
            user_id: Current user ID
            command_bus: Command bus

        Returns:
            Updated file response
        """
        command = UpdateFileCommand(
            file_id=file_id,
            user_id=user_id,
            name=request.name,
        )

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value, "File updated successfully")

    async def delete_file(
        self,
        file_id: UUID,
        user_id: UUID,
        command_bus: CommandBusDep,
    ) -> ApiResponse:
        """
        Delete file.

        Args:
            file_id: File UUID
            user_id: Current user ID
            command_bus: Command bus

        Returns:
            Success response
        """
        command = DeleteFileCommand(
            file_id=file_id,
            user_id=user_id,
        )

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.no_content("File deleted successfully")

    async def share_file(
        self,
        file_id: UUID,
        request: ShareFileRequest,
        user_id: UUID,
        command_bus: CommandBusDep,
    ) -> ApiResponse[FileReadModel]:
        """
        Share file with another user.

        Args:
            file_id: File UUID
            request: Share request data
            user_id: Current user ID (file owner)
            command_bus: Command bus

        Returns:
            Updated file response
        """
        command = ShareFileCommand(
            file_id=file_id,
            owner_id=user_id,
            target_user_id=request.user_id,
            permission=request.permission,
        )

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value, "File shared successfully")

    # ========================================================================
    # READ OPERATIONS - Queries via Query Bus
    # ========================================================================

    async def get_file(
        self,
        file_id: UUID,
        user_id: UUID,
        query_bus: QueryBusDep,
    ) -> ApiResponse[FileReadModel]:
        """
        Get file metadata.

        Args:
            file_id: File UUID
            user_id: Current user ID
            query_bus: Query bus

        Returns:
            File response
        """
        query = GetFileByIdQuery(
            file_id=file_id,
            user_id=user_id,
        )

        result = await query_bus.dispatch(query)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value)

    async def list_files(
        self,
        params: PaginationParams,
        owner_only: bool,
        public_only: bool,
        user_id: UUID,
        query_bus: QueryBusDep,
    ) -> ApiResponse[PaginatedResponse[FileListItemReadModel]]:
        """
        List files with pagination.

        Args:
            params: Pagination parameters
            owner_only: Show only user's files
            public_only: Show only public files
            user_id: Current user ID
            query_bus: Query bus

        Returns:
            Paginated file list response
        """
        query = ListFilesQuery(
            user_id=user_id,
            skip=params.skip,
            limit=params.limit,
            owner_only=owner_only,
            public_only=public_only,
        )

        result = await query_bus.dispatch(query)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        paginated = result.value
        return self.paginated(paginated.items, paginated.total, params)

    async def download_file(
        self,
        file_id: UUID,
        user_id: UUID,
        query_bus: QueryBusDep,
    ) -> StreamingResponse:
        """
        Download file content.

        Args:
            file_id: File UUID
            user_id: Current user ID
            query_bus: Query bus

        Returns:
            Streaming response with file content
        """
        query = GetFileDownloadQuery(
            file_id=file_id,
            user_id=user_id,
        )

        result = await query_bus.dispatch(query)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        download_info = result.value

        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(download_info.content),
            media_type=download_info.mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{download_info.original_name}"'
            },
        )
