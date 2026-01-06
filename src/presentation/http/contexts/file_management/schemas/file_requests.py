"""
File Management API Request Schemas.

Presentation layer schemas for API request validation.
These are separate from Application DTOs to maintain clean layer separation.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UpdateFileRequest(BaseModel):
    """
    Request schema for updating file metadata.

    Only allows updating the display name of the file.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="New display name for the file",
    )


class ShareFileRequest(BaseModel):
    """
    Request schema for sharing a file with another user.

    Specifies the target user and permission level.
    """

    user_id: UUID = Field(
        ...,
        description="ID of the user to share the file with",
    )
    permission: str = Field(
        default="read",
        pattern="^(read|write)$",
        description="Permission level: 'read' or 'write'",
    )


class FileUploadMetadata(BaseModel):
    """
    Optional metadata for file upload.

    Can be provided alongside the file during upload.
    """

    custom_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Custom display name (uses original filename if not provided)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional description of the file",
    )
