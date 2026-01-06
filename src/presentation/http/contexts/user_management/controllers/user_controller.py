"""
User API Controller using CQRS pattern.

This controller uses Command Bus for write operations and Query Bus for read operations.

NOTE: Controller is THIN - no database/transaction knowledge!
- UoW is handled in Application Layer (Handlers)
- Controller only maps HTTP requests to Commands/Queries
"""

from typing import Optional
from uuid import UUID

# Import from context public API
from contexts.user_management import (  # Commands; Queries; Read Models
    ActivateUserCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    DeleteUserCommand,
    GetUserByEmailQuery,
    GetUserByIdQuery,
    GetUserByUsernameQuery,
    ListUsersQuery,
    PaginatedUsersReadModel,
    UpdateUserCommand,
    UserListItemReadModel,
    UserReadModel,
)
from shared.application.ports import ICommandBus, IQueryBus
from shared.presentation import ApiResponse, BaseController, PaginatedResponse, PaginationParams

# Request Schemas (Presentation layer)
from ..schemas import CreateUserRequest, UpdateUserEmailRequest, UpdateUserRequest


class UserController(BaseController):
    """
    User API controller using CQRS pattern.

    Write Operations: CommandBus.dispatch(Command) → CommandHandler → Result
    Read Operations: QueryBus.dispatch(Query) → QueryHandler → Result

    NOTE: Controller does NOT know about UoW/transactions!
    UoW is managed by Handlers in Application Layer.
    """

    def __init__(self):
        super().__init__()

    # ========================================================================
    # WRITE OPERATIONS - Command Bus
    # ========================================================================

    async def create_user(
        self,
        request: CreateUserRequest,
        command_bus: ICommandBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Create a new user.

        Args:
            request: User creation request from API
            command_bus: Command bus for dispatching

        Returns:
            Created user response
        """
        # Map request schema to command
        command = CreateUserCommand(
            email=request.email,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        # Dispatch command via bus (Handler manages UoW)
        result = await command_bus.dispatch(command)

        # Handle result
        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.created(result.value, "User created successfully")

    async def update_user(
        self,
        user_id: UUID,
        request: UpdateUserRequest,
        command_bus: ICommandBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Update user profile.

        Args:
            user_id: User UUID
            request: User update request from API
            command_bus: Command bus for dispatching

        Returns:
            Updated user response
        """
        # Map request schema to command
        command = UpdateUserCommand(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value, "User updated successfully")

    async def update_user_email(
        self,
        user_id: UUID,
        request: UpdateUserEmailRequest,
        command_bus: ICommandBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Update user email.

        Args:
            user_id: User UUID
            request: Email update request from API
            command_bus: Command bus for dispatching

        Returns:
            Updated user response
        """
        # Map request schema to command
        command = UpdateUserCommand(
            user_id=user_id,
            email=request.email,
        )

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value, "Email updated successfully")

    async def delete_user(
        self,
        user_id: UUID,
        command_bus: ICommandBus,
    ) -> ApiResponse:
        """
        Delete user (soft delete).

        Args:
            user_id: User UUID
            command_bus: Command bus for dispatching

        Returns:
            Success response
        """
        command = DeleteUserCommand(user_id=user_id)

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.no_content("User deleted successfully")

    async def activate_user(
        self,
        user_id: UUID,
        command_bus: ICommandBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Activate user account.

        Args:
            user_id: User UUID
            command_bus: Command bus for dispatching

        Returns:
            Activated user response
        """
        command = ActivateUserCommand(user_id=user_id)

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value, "User activated successfully")

    async def deactivate_user(
        self,
        user_id: UUID,
        command_bus: ICommandBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Deactivate user account.

        Args:
            user_id: User UUID
            command_bus: Command bus for dispatching

        Returns:
            Deactivated user response
        """
        command = DeactivateUserCommand(user_id=user_id)

        result = await command_bus.dispatch(command)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value, "User deactivated successfully")

    # ========================================================================
    # READ OPERATIONS - Query Bus
    # ========================================================================

    async def get_user(
        self,
        user_id: UUID,
        query_bus: IQueryBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Get user by ID.

        Args:
            user_id: User UUID
            query_bus: Query bus for dispatching

        Returns:
            User response
        """
        query = GetUserByIdQuery(user_id=user_id)
        result = await query_bus.dispatch(query)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value)

    async def list_users(
        self,
        params: PaginationParams,
        is_active: Optional[bool],
        query_bus: IQueryBus,
    ) -> ApiResponse[PaginatedResponse[UserListItemReadModel]]:
        """
        List all users with pagination.

        Args:
            params: Pagination parameters
            is_active: Filter by active status
            query_bus: Query bus for dispatching

        Returns:
            Paginated user list response
        """
        query = ListUsersQuery(
            skip=params.skip,
            limit=params.limit,
            is_active=is_active,
        )

        result = await query_bus.dispatch(query)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        # Extract paginated result
        paginated: PaginatedUsersReadModel = result.value

        return self.paginated(
            paginated.users,
            paginated.total,
            params,
        )

    async def get_user_by_email(
        self,
        email: str,
        query_bus: IQueryBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Get user by email.

        Args:
            email: User email address
            query_bus: Query bus for dispatching

        Returns:
            User response
        """
        query = GetUserByEmailQuery(email=email)
        result = await query_bus.dispatch(query)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value)

    async def get_user_by_username(
        self,
        username: str,
        query_bus: IQueryBus,
    ) -> ApiResponse[UserReadModel]:
        """
        Get user by username.

        Args:
            username: Username
            query_bus: Query bus for dispatching

        Returns:
            User response
        """
        query = GetUserByUsernameQuery(username=username)
        result = await query_bus.dispatch(query)

        if result.is_failure:
            self.handle_error(result)  # Raises HTTPException

        return self.success(result.value)
