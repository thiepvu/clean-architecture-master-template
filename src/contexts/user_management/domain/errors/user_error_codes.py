"""
User Management Error Codes.
Defines all error codes specific to the User Management bounded context.
"""

from enum import Enum

from shared.errors.error_codes import ErrorCodeRegistry


class UserErrorCode(str, Enum):
    """
    Error codes for User Management bounded context.

    Naming convention: USER_XXX where XXX describes the error.
    """

    # Validation errors (001-009)
    INVALID_EMAIL_FORMAT = "USER_001"
    INVALID_USERNAME_FORMAT = "USER_002"
    INVALID_NAME_FORMAT = "USER_003"
    INVALID_USER_ID = "USER_004"

    # Business rule errors (010-019)
    USER_EMAIL_EXISTS = "USER_010"
    USER_USERNAME_EXISTS = "USER_011"
    USER_NOT_FOUND = "USER_012"
    USER_ALREADY_ACTIVE = "USER_013"
    USER_ALREADY_INACTIVE = "USER_014"
    CANNOT_DELETE_ACTIVE_USER = "USER_015"

    # Authorization errors (020-029)
    INSUFFICIENT_PERMISSIONS = "USER_020"
    CANNOT_MODIFY_OWN_ROLE = "USER_021"
    CANNOT_DEACTIVATE_SELF = "USER_022"


def register_user_error_codes() -> None:
    """
    Register User Management error codes with the global registry.
    Should be called during application startup.
    """
    registry = ErrorCodeRegistry()

    # Validation errors - 422 Unprocessable Entity
    registry.register(
        UserErrorCode.INVALID_EMAIL_FORMAT.value,
        422,
        "Invalid email format",
    )
    registry.register(
        UserErrorCode.INVALID_USERNAME_FORMAT.value,
        422,
        "Invalid username format",
    )
    registry.register(
        UserErrorCode.INVALID_NAME_FORMAT.value,
        422,
        "Invalid name format",
    )
    registry.register(
        UserErrorCode.INVALID_USER_ID.value,
        422,
        "Invalid user ID format",
    )

    # Business rule errors - 409 Conflict or 404 Not Found
    registry.register(
        UserErrorCode.USER_EMAIL_EXISTS.value,
        409,
        "Email already registered",
    )
    registry.register(
        UserErrorCode.USER_USERNAME_EXISTS.value,
        409,
        "Username already taken",
    )
    registry.register(
        UserErrorCode.USER_NOT_FOUND.value,
        404,
        "User not found",
    )
    registry.register(
        UserErrorCode.USER_ALREADY_ACTIVE.value,
        409,
        "User is already active",
    )
    registry.register(
        UserErrorCode.USER_ALREADY_INACTIVE.value,
        409,
        "User is already inactive",
    )
    registry.register(
        UserErrorCode.CANNOT_DELETE_ACTIVE_USER.value,
        409,
        "Cannot delete an active user",
    )

    # Authorization errors - 403 Forbidden
    registry.register(
        UserErrorCode.INSUFFICIENT_PERMISSIONS.value,
        403,
        "Insufficient permissions",
    )
    registry.register(
        UserErrorCode.CANNOT_MODIFY_OWN_ROLE.value,
        403,
        "Cannot modify own role",
    )
    registry.register(
        UserErrorCode.CANNOT_DEACTIVATE_SELF.value,
        403,
        "Cannot deactivate own account",
    )
