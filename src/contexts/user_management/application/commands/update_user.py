"""
Update User Command and Handler.

This command updates an existing user's information.
"""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from shared.application.base_command import Command, CommandHandler
from shared.domain.result import Result

from ...domain.errors.user_error_codes import UserErrorCode
from ...domain.value_objects.email import Email
from ..dto.mappers import UserMapper
from ..ports import IUserManagementUoW, IUserManagementUoWFactory
from ..read_models import UserReadModel

if TYPE_CHECKING:
    from shared.application.ports import ICacheService


class UpdateUserCommand(Command):
    """
    Command to update an existing user.

    Attributes:
        user_id: UUID of the user to update
        first_name: New first name (optional)
        last_name: New last name (optional)
        email: New email address (optional)
    """

    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class UpdateUserHandler(CommandHandler[UpdateUserCommand, UserReadModel]):
    """
    Handler for UpdateUserCommand.

    Responsibilities:
    - Validate user exists
    - Validate new email if provided
    - Check email uniqueness if changed
    - Update user entity
    - Persist changes
    - Publish domain events
    - Invalidate cache if provided
    """

    # Cache key prefix (must match GetUserByIdHandler)
    CACHE_KEY_PREFIX = "user:by_id:"

    def __init__(
        self,
        uow_factory: IUserManagementUoWFactory,
        cache_service: Optional["ICacheService"] = None,
    ):
        """
        Initialize handler.

        Args:
            uow_factory: Factory for creating User Management UoW instances
            cache_service: Optional cache service for invalidating cached data
        """
        self._uow_factory = uow_factory
        self._cache_service = cache_service

    async def handle(self, command: UpdateUserCommand) -> Result[UserReadModel]:
        """
        Handle the update user command.

        Args:
            command: UpdateUserCommand with update data

        Returns:
            Result containing updated UserReadModel on success, or error on failure
        """
        # All repository operations inside UoW context
        async with self._uow_factory.create() as uow:
            # 1. Get existing user
            user = await uow.users.get_by_id(command.user_id)
            if user is None:
                return Result.fail(
                    code=UserErrorCode.USER_NOT_FOUND.value,
                    message=f"User with ID {command.user_id} not found",
                )

            # 2. Validate and update email if provided
            if command.email is not None:
                email_result = await self._update_email(uow, user, command.email)
                if email_result.is_failure:
                    return email_result

            # 3. Update profile if names provided
            if command.first_name is not None or command.last_name is not None:
                first_name = (
                    command.first_name if command.first_name is not None else user.first_name
                )
                last_name = command.last_name if command.last_name is not None else user.last_name
                user.update_profile(first_name, last_name)

            # 4. Persist changes
            updated_user = await uow.users.update(user)

            # Track aggregate for event collection
            uow.track(updated_user)

            # Commit transaction
            await uow.commit()

        # Invalidate cache after successful update
        if self._cache_service:
            cache_key = f"{self.CACHE_KEY_PREFIX}{command.user_id}"
            await self._cache_service.delete(cache_key)

        # Return success result with read model
        return Result.ok(UserMapper.to_read_model(updated_user))

    async def _update_email(self, uow: IUserManagementUoW, user, new_email: str) -> Result:
        """Validate and update user email. Must be called inside UoW context."""
        # Validate email format
        try:
            Email(new_email)
        except ValueError as e:
            return Result.from_exception(e, UserErrorCode.INVALID_EMAIL_FORMAT.value)

        # Check if email is different
        if user.email.value == new_email.lower():
            return Result.ok(None)

        # Check if new email is already in use
        existing = await uow.users.get_by_email(Email(new_email))
        if existing and existing.id != user.id:
            return Result.fail(
                code=UserErrorCode.USER_EMAIL_EXISTS.value,
                message=f"Email {new_email} is already in use",
            )

        # Update email (domain method)
        user.change_email(new_email)

        return Result.ok(None)
