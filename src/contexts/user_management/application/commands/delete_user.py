"""
Delete User Command and Handler.

This command handles soft/hard deletion of users.
"""

from uuid import UUID

from shared.application.base_command import Command, CommandHandler
from shared.domain.result import Result

from ...domain.errors.user_error_codes import UserErrorCode
from ..ports import IUserManagementUoWFactory


class DeleteUserCommand(Command):
    """
    Command to delete a user.

    Attributes:
        user_id: UUID of the user to delete
        hard_delete: If True, permanently delete; if False, soft delete (default)
    """

    user_id: UUID
    hard_delete: bool = False


class DeleteUserHandler(CommandHandler[DeleteUserCommand, None]):
    """
    Handler for DeleteUserCommand.

    Responsibilities:
    - Validate user exists
    - Perform soft or hard delete
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

    async def handle(self, command: DeleteUserCommand) -> Result[None]:
        """
        Handle the delete user command.

        Args:
            command: DeleteUserCommand with user ID

        Returns:
            Result indicating success or failure
        """
        # All repository operations inside UoW context
        async with self._uow_factory.create() as uow:
            # 1. Check if user exists
            exists = await uow.users.exists(command.user_id)
            if not exists:
                return Result.fail(
                    code=UserErrorCode.USER_NOT_FOUND.value,
                    message=f"User with ID {command.user_id} not found",
                )

            # 2. Get user first then delete
            user = await uow.users.get_by_id(command.user_id)
            if user:
                await uow.users.delete(user)

            # Commit transaction
            await uow.commit()

        # Return success result
        return Result.ok(None)
