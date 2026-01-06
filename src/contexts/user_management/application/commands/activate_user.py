"""
Activate User Command and Handler.

This command activates a user account.
"""

from uuid import UUID

from shared.application.base_command import Command, CommandHandler
from shared.domain.result import Result

from ...domain.errors.user_error_codes import UserErrorCode
from ..ports import IUserManagementUoWFactory
from ..read_models import UserReadModel


class ActivateUserCommand(Command):
    """
    Command to activate a user account.

    Attributes:
        user_id: UUID of the user to activate
    """

    user_id: UUID


class ActivateUserHandler(CommandHandler[ActivateUserCommand, UserReadModel]):
    """
    Handler for ActivateUserCommand.

    Responsibilities:
    - Validate user exists
    - Activate user account
    - Persist changes
    - Publish domain events
    """

    def __init__(self, uow_factory: IUserManagementUoWFactory):
        """
        Initialize handler.

        Args:
            uow_factory: Factory for creating User Management UoW instances
        """
        self._uow_factory = uow_factory

    async def handle(self, command: ActivateUserCommand) -> Result[UserReadModel]:
        """
        Handle the activate user command.

        Args:
            command: ActivateUserCommand with user ID

        Returns:
            Result containing UserReadModel on success, or error on failure
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

            # 2. Check if already active
            if user.is_active:
                return Result.fail(
                    code=UserErrorCode.USER_ALREADY_ACTIVE.value,
                    message=f"User {command.user_id} is already active",
                )

            # 3. Activate user (domain method)
            user.activate()

            # 4. Persist changes
            updated_user = await uow.users.update(user)
            uow.track(updated_user)
            await uow.commit()

        # Return success result with read model
        return Result.ok(self._to_read_model(updated_user))

    def _to_read_model(self, user) -> UserReadModel:
        """Convert domain entity to read model."""
        return UserReadModel(
            id=user.id,
            email=user.email.value,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
