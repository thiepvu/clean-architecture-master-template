"""
User Management API Routes.

Uses CQRS pattern with Command Bus and Query Bus.

NOTE: No @with_session decorator needed!
- UoW creates its own session in Application Layer
- Controller is thin (no transaction knowledge)
- Clean Architecture compliant
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from contexts.user_management import UserListItemReadModel, UserReadModel
from shared.presentation import ApiResponse, PaginatedResponse, PaginationParams

from .controllers.user_controller import UserController
from .dependencies import CommandBusDep, QueryBusDep
from .schemas import CreateUserRequest, UpdateUserEmailRequest, UpdateUserRequest

# Create router
router = APIRouter(prefix="/users", tags=["Users"])

# Create controller instance
controller = UserController()


# ============================================================================
# CREATE USER (Command)
# ============================================================================


@router.post(
    "/",
    response_model=ApiResponse[UserReadModel],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with email, username, and profile information",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "User with email or username already exists"},
        422: {"description": "Validation error"},
    },
)
async def create_user(request: CreateUserRequest, command_bus: CommandBusDep):
    """Create a new user via Command Bus"""
    return await controller.create_user(request, command_bus)


# ============================================================================
# GET USER BY ID (Query)
# ============================================================================


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserReadModel],
    summary="Get user by ID",
    description="Retrieve a specific user by their unique identifier",
    responses={200: {"description": "User found"}, 404: {"description": "User not found"}},
)
async def get_user(user_id: UUID, query_bus: QueryBusDep):
    """Get user by ID via Query Bus"""
    return await controller.get_user(user_id, query_bus)


# ============================================================================
# GET USER BY EMAIL (Query)
# ============================================================================


@router.get(
    "/email/{email}",
    response_model=ApiResponse[UserReadModel],
    summary="Get user by email",
    description="Retrieve a user by their email address",
    responses={200: {"description": "User found"}, 404: {"description": "User not found"}},
)
async def get_user_by_email(email: str, query_bus: QueryBusDep):
    """Get user by email via Query Bus"""
    return await controller.get_user_by_email(email, query_bus)


# ============================================================================
# GET USER BY USERNAME (Query)
# ============================================================================


@router.get(
    "/username/{username}",
    response_model=ApiResponse[UserReadModel],
    summary="Get user by username",
    description="Retrieve a user by their username",
    responses={200: {"description": "User found"}, 404: {"description": "User not found"}},
)
async def get_user_by_username(username: str, query_bus: QueryBusDep):
    """Get user by username via Query Bus"""
    return await controller.get_user_by_username(username, query_bus)


# ============================================================================
# UPDATE USER (Command)
# ============================================================================


@router.put(
    "/{user_id}",
    response_model=ApiResponse[UserReadModel],
    summary="Update user profile",
    description="Update user's first name and last name",
    responses={
        200: {"description": "User updated successfully"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
    },
)
async def update_user(user_id: UUID, request: UpdateUserRequest, command_bus: CommandBusDep):
    """Update user profile via Command Bus"""
    return await controller.update_user(user_id, request, command_bus)


# ============================================================================
# UPDATE USER EMAIL (Command)
# ============================================================================


@router.patch(
    "/{user_id}/email",
    response_model=ApiResponse[UserReadModel],
    summary="Update user email",
    description="Update user's email address",
    responses={
        200: {"description": "Email updated successfully"},
        404: {"description": "User not found"},
        409: {"description": "Email already in use"},
        422: {"description": "Validation error"},
    },
)
async def update_user_email(
    user_id: UUID, request: UpdateUserEmailRequest, command_bus: CommandBusDep
):
    """Update user email via Command Bus"""
    return await controller.update_user_email(user_id, request, command_bus)


# ============================================================================
# ACTIVATE USER (Command)
# ============================================================================


@router.post(
    "/{user_id}/activate",
    response_model=ApiResponse[UserReadModel],
    summary="Activate user",
    description="Activate a user account",
    responses={
        200: {"description": "User activated successfully"},
        404: {"description": "User not found"},
        409: {"description": "User already active"},
    },
)
async def activate_user(user_id: UUID, command_bus: CommandBusDep):
    """Activate user account via Command Bus"""
    return await controller.activate_user(user_id, command_bus)


# ============================================================================
# DEACTIVATE USER (Command)
# ============================================================================


@router.post(
    "/{user_id}/deactivate",
    response_model=ApiResponse[UserReadModel],
    summary="Deactivate user",
    description="Deactivate a user account",
    responses={
        200: {"description": "User deactivated successfully"},
        404: {"description": "User not found"},
        409: {"description": "User already inactive"},
    },
)
async def deactivate_user(user_id: UUID, command_bus: CommandBusDep):
    """Deactivate user account via Command Bus"""
    return await controller.deactivate_user(user_id, command_bus)


# ============================================================================
# DELETE USER (Command)
# ============================================================================


@router.delete(
    "/{user_id}",
    response_model=ApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user",
    description="Soft delete a user from the system",
    responses={
        200: {"description": "User deleted successfully"},
        404: {"description": "User not found"},
    },
)
async def delete_user(user_id: UUID, command_bus: CommandBusDep):
    """Delete user via Command Bus"""
    return await controller.delete_user(user_id, command_bus)


# ============================================================================
# LIST USERS (Query)
# ============================================================================


@router.get(
    "/",
    response_model=ApiResponse[PaginatedResponse[UserListItemReadModel]],
    summary="List users",
    description="Get a paginated list of all users with optional filtering",
    responses={200: {"description": "Users retrieved successfully"}},
)
async def list_users(
    params: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    query_bus: QueryBusDep = None,
):
    """List all users with pagination via Query Bus"""
    return await controller.list_users(params, is_active, query_bus)
