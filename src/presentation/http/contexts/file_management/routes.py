"""
File Management API Routes (v1).

All routes use CQRS pattern via Command Bus and Query Bus.

NOTE: No @with_session decorator needed!
- UoW creates its own session in Application Layer
- Controller is thin (no transaction knowledge)
- Clean Architecture compliant
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import File as FastAPIFile
from fastapi import Query, UploadFile, status

from contexts.file_management import FileListItemReadModel, FileReadModel
from shared.presentation import ApiResponse, PaginationParams

from .controllers.file_controller import FileController
from .dependencies import CommandBusDep, QueryBusDep
from .schemas import ShareFileRequest, UpdateFileRequest

# Create router
router = APIRouter(prefix="/files", tags=["Files"])

# Create controller
controller = FileController()

# Mock user ID (TODO: Replace with auth)
MOCK_USER_ID = UUID("9acbe950-6c96-42df-9314-829e74cc64ef")


# ============================================================================
# UPLOAD FILE - Command
# ============================================================================


@router.post(
    "/upload",
    response_model=ApiResponse[FileReadModel],
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
    description="Upload a new file with metadata",
)
async def upload_file(
    command_bus: CommandBusDep,
    file: UploadFile = FastAPIFile(...),
    description: Optional[str] = Query(None, description="File description"),
    is_public: bool = Query(False, description="Make file public"),
):
    """Upload a new file."""
    return await controller.upload_file(
        file=file,
        description=description,
        is_public=is_public,
        user_id=MOCK_USER_ID,
        command_bus=command_bus,
    )


# ============================================================================
# GET FILE BY ID - Query
# ============================================================================


@router.get(
    "/{file_id}",
    response_model=ApiResponse[FileReadModel],
    summary="Get file metadata",
    description="Retrieve file metadata by ID",
)
async def get_file(
    file_id: UUID,
    query_bus: QueryBusDep,
):
    """Get file metadata."""
    return await controller.get_file(
        file_id=file_id,
        user_id=MOCK_USER_ID,
        query_bus=query_bus,
    )


# ============================================================================
# UPDATE FILE - Command
# ============================================================================


@router.put(
    "/{file_id}",
    response_model=ApiResponse[FileReadModel],
    summary="Update file metadata",
    description="Update file display name",
)
async def update_file(
    file_id: UUID,
    request: UpdateFileRequest,
    command_bus: CommandBusDep,
):
    """Update file metadata."""
    return await controller.update_file(
        file_id=file_id,
        request=request,
        user_id=MOCK_USER_ID,
        command_bus=command_bus,
    )


# ============================================================================
# DELETE FILE - Command
# ============================================================================


@router.delete(
    "/{file_id}",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete file",
    description="Delete file (soft delete)",
)
async def delete_file(
    file_id: UUID,
    command_bus: CommandBusDep,
):
    """Delete file."""
    return await controller.delete_file(
        file_id=file_id,
        user_id=MOCK_USER_ID,
        command_bus=command_bus,
    )


# ============================================================================
# LIST FILES - Query
# ============================================================================


@router.get(
    "/",
    response_model=None,
    summary="List files",
    description="Get paginated list of files",
)
async def list_files(
    query_bus: QueryBusDep,
    params: PaginationParams = Depends(),
    owner_only: bool = Query(False, description="Show only my files"),
    public_only: bool = Query(False, description="Show only public files"),
):
    """List files with filters."""
    return await controller.list_files(
        params=params,
        owner_only=owner_only,
        public_only=public_only,
        user_id=MOCK_USER_ID,
        query_bus=query_bus,
    )


# ============================================================================
# SHARE FILE - Command
# ============================================================================


@router.post(
    "/{file_id}/share",
    response_model=ApiResponse[FileReadModel],
    summary="Share file",
    description="Share file with another user",
)
async def share_file(
    file_id: UUID,
    request: ShareFileRequest,
    command_bus: CommandBusDep,
):
    """Share file with user."""
    return await controller.share_file(
        file_id=file_id,
        request=request,
        user_id=MOCK_USER_ID,
        command_bus=command_bus,
    )


# ============================================================================
# DOWNLOAD FILE - Query
# ============================================================================


@router.get(
    "/{file_id}/download",
    summary="Download file",
    description="Download file content",
    responses={
        200: {
            "description": "File content",
            "content": {"application/octet-stream": {}},
        }
    },
)
async def download_file(
    file_id: UUID,
    query_bus: QueryBusDep,
):
    """Download file."""
    return await controller.download_file(
        file_id=file_id,
        user_id=MOCK_USER_ID,
        query_bus=query_bus,
    )
