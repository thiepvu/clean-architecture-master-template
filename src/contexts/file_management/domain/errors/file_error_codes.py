"""
File Management Error Codes.
Defines all error codes specific to the File Management bounded context.
"""

from enum import Enum

from shared.errors.error_codes import ErrorCodeRegistry


class FileErrorCode(str, Enum):
    """
    Error codes for File Management bounded context.

    Naming convention: FILE_XXX where XXX describes the error.
    """

    # Validation errors (001-009)
    INVALID_FILE_PATH = "FILE_001"
    INVALID_FILE_SIZE = "FILE_002"
    INVALID_MIME_TYPE = "FILE_003"
    FILE_SIZE_EXCEEDED = "FILE_004"
    FILE_TYPE_NOT_ALLOWED = "FILE_005"

    # Business rule errors (010-019)
    FILE_NOT_FOUND = "FILE_010"
    FILE_ACCESS_DENIED = "FILE_011"
    FILE_ALREADY_SHARED = "FILE_012"
    FILE_NOT_SHARED = "FILE_013"
    CANNOT_SHARE_OWN_FILE = "FILE_014"
    OWNER_NOT_FOUND = "FILE_015"
    TARGET_USER_NOT_FOUND = "FILE_016"

    # Storage errors (020-029)
    FILE_UPLOAD_FAILED = "FILE_020"
    FILE_DOWNLOAD_FAILED = "FILE_021"
    FILE_DELETE_FAILED = "FILE_022"
    STORAGE_ERROR = "FILE_023"


def register_file_error_codes() -> None:
    """
    Register File Management error codes with the global registry.
    Should be called during application startup.
    """
    registry = ErrorCodeRegistry()

    # Validation errors - 422 Unprocessable Entity
    registry.register(
        FileErrorCode.INVALID_FILE_PATH.value,
        422,
        "Invalid file path",
    )
    registry.register(
        FileErrorCode.INVALID_FILE_SIZE.value,
        422,
        "Invalid file size",
    )
    registry.register(
        FileErrorCode.INVALID_MIME_TYPE.value,
        422,
        "Invalid MIME type",
    )
    registry.register(
        FileErrorCode.FILE_SIZE_EXCEEDED.value,
        413,
        "File size exceeds maximum limit",
    )
    registry.register(
        FileErrorCode.FILE_TYPE_NOT_ALLOWED.value,
        415,
        "File type not allowed",
    )

    # Business rule errors - 404/403/409
    registry.register(
        FileErrorCode.FILE_NOT_FOUND.value,
        404,
        "File not found",
    )
    registry.register(
        FileErrorCode.FILE_ACCESS_DENIED.value,
        403,
        "Access denied to file",
    )
    registry.register(
        FileErrorCode.FILE_ALREADY_SHARED.value,
        409,
        "File is already shared with this user",
    )
    registry.register(
        FileErrorCode.FILE_NOT_SHARED.value,
        409,
        "File is not shared with this user",
    )
    registry.register(
        FileErrorCode.CANNOT_SHARE_OWN_FILE.value,
        409,
        "Cannot share file with yourself",
    )
    registry.register(
        FileErrorCode.OWNER_NOT_FOUND.value,
        404,
        "File owner not found",
    )
    registry.register(
        FileErrorCode.TARGET_USER_NOT_FOUND.value,
        404,
        "Target user not found",
    )

    # Storage errors - 500
    registry.register(
        FileErrorCode.FILE_UPLOAD_FAILED.value,
        500,
        "Failed to upload file",
    )
    registry.register(
        FileErrorCode.FILE_DOWNLOAD_FAILED.value,
        500,
        "Failed to download file",
    )
    registry.register(
        FileErrorCode.FILE_DELETE_FAILED.value,
        500,
        "Failed to delete file",
    )
    registry.register(
        FileErrorCode.STORAGE_ERROR.value,
        500,
        "Storage error occurred",
    )
