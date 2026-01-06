"""
Create User Command and Handler.

This command creates a new user in the system.
"""

from shared.application.base_command import Command, CommandHandler
from shared.domain.result import Result

from ...domain.entities.user import User
from ...domain.errors.user_error_codes import UserErrorCode
from ...domain.value_objects.email import Email
from ..dto.mappers import UserMapper
from ..ports import IUserManagementUoWFactory
from ..read_models import UserReadModel


class CreateUserCommand(Command):
    """
    Command to create a new user.

    Attributes:
        email: User email address
        username: Unique username
        first_name: User's first name
        last_name: User's last name
    """

    email: str
    username: str
    first_name: str
    last_name: str


class CreateUserHandler(CommandHandler[CreateUserCommand, UserReadModel]):
    """
    Handler for CreateUserCommand.

    Responsibilities:
    - Validate email format
    - Check for duplicate email/username
    - Create user entity
    - Persist to repository
    - Publish domain events
    """

    def __init__(self, uow_factory: IUserManagementUoWFactory):
        """
        Initialize handler.

        Args:
            uow_factory: Factory for creating User Management UoW instances
        """
        self._uow_factory = uow_factory

    async def handle(self, command: CreateUserCommand) -> Result[UserReadModel]:
        """
        Handle the create user command.

        Args:
            command: CreateUserCommand with user data

        Returns:
            Result containing UserReadModel on success, or error on failure
        """
        # 1. Validate email format (no DB needed)
        email_result = self._validate_email(command.email)
        if email_result.is_failure:
            return email_result

        # 2. All repository operations inside UoW context
        async with self._uow_factory.create() as uow:
            # Check if user with email already exists
            existing_by_email = await uow.users.get_by_email(Email(command.email))
            if existing_by_email:
                return Result.fail(
                    code=UserErrorCode.USER_EMAIL_EXISTS.value,
                    message=f"User with email {command.email} already exists",
                )

            # Check if user with username already exists
            existing_by_username = await uow.users.get_by_username(command.username)
            if existing_by_username:
                return Result.fail(
                    code=UserErrorCode.USER_USERNAME_EXISTS.value,
                    message=f"User with username {command.username} already exists",
                )

            # Create user entity (domain logic)
            user = User.create(
                email=command.email,
                username=command.username,
                first_name=command.first_name,
                last_name=command.last_name,
            )

            # Track aggregate for event collection BEFORE add()
            # (add() returns a new entity without domain events)
            uow.track(user)

            # Persist user
            saved_user = await uow.users.add(user)

            # Commit transaction (events published after commit)
            await uow.commit()

        # Return success result with read model
        return Result.ok(UserMapper.to_read_model(saved_user))

    def _validate_email(self, email: str) -> Result:
        """Validate email format."""
        try:
            Email(email)
            return Result.ok(None)
        except ValueError as e:
            return Result.from_exception(e, UserErrorCode.INVALID_EMAIL_FORMAT.value)
