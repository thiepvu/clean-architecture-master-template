"""
User Verification Service.

This service verifies user existence via Query Bus - demonstrating
cross-context communication through CQRS without direct dependencies.

Example 5: Sync dependency giữa User và File qua CQRS (không Facade)

Architecture:
─────────────
┌─────────────────────┐
│  File Management BC │
│  ┌─────────────────┐│
│  │UserVerification ││──── Query ────┐
│  │    Service      ││               │
│  └─────────────────┘│               ▼
└─────────────────────┘       ┌───────────────┐
                              │   QueryBus    │
                              └───────┬───────┘
                                      │
                                      ▼
                              ┌───────────────────┐
                              │ User Management BC│
                              │ ┌───────────────┐ │
                              │ │GetUserByIdQry │ │
                              │ └───────────────┘ │
                              └───────────────────┘

Benefits:
- Loose coupling: File BC doesn't import User BC directly
- Testable: Mock QueryBus for unit tests
- Evolvable: User BC internals can change without affecting File BC
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import UUID

if TYPE_CHECKING:
    from shared.application.ports import ILogger, IQueryBus


@dataclass
class UserInfo:
    """
    Minimal user information needed by File Management.

    This is a local representation - File BC defines what it needs,
    not what User BC provides. Decouples contexts further.
    """

    user_id: UUID
    email: str
    is_active: bool


class UserNotFoundError(Exception):
    """Raised when user is not found."""

    pass


class UserInactiveError(Exception):
    """Raised when user is inactive."""

    pass


class UserVerificationService:
    """
    Service for verifying user information via Query Bus.

    This demonstrates cross-context communication through CQRS:
    1. File BC needs to verify user exists before file upload
    2. Instead of importing User BC facade, it uses Query Bus
    3. Query Bus routes to User BC's GetUserByIdHandler
    4. Result is mapped to local UserInfo (Anti-Corruption Layer pattern)

    Usage:
        service = UserVerificationService(query_bus, logger)

        # Verify user exists and is active
        user_info = await service.verify_user(owner_id)

        # Or just check existence
        exists = await service.user_exists(owner_id)
    """

    def __init__(self, query_bus: "IQueryBus", logger: "ILogger"):
        """
        Initialize the service.

        Args:
            query_bus: Query bus for cross-context queries
            logger: Logger instance
        """
        self._query_bus = query_bus
        self._logger = logger

    async def verify_user(self, user_id: UUID) -> UserInfo:
        """
        Verify user exists and is active.

        This method queries User Management BC through the Query Bus,
        ensuring loose coupling between contexts.

        Args:
            user_id: User UUID to verify

        Returns:
            UserInfo with user details

        Raises:
            UserNotFoundError: If user doesn't exist
            UserInactiveError: If user is inactive
        """
        # Import query type (only the query DTO, not handler)
        from contexts.user_management.application.queries import GetUserByIdQuery

        # Create and dispatch query through Query Bus
        query = GetUserByIdQuery(user_id=user_id)
        result = await self._query_bus.dispatch(query)

        # Handle not found
        if result.is_failure:
            self._logger.warning(f"User verification failed: {result.error_message}")
            raise UserNotFoundError(f"User {user_id} not found")

        # Map to local representation (Anti-Corruption Layer)
        user_data = result.value

        # Check if user is active
        if not user_data.is_active:
            self._logger.warning(f"User {user_id} is inactive")
            raise UserInactiveError(f"User {user_id} is inactive")

        return UserInfo(
            user_id=user_data.id,
            email=user_data.email,
            is_active=user_data.is_active,
        )

    async def user_exists(self, user_id: UUID) -> bool:
        """
        Check if user exists (regardless of active status).

        Args:
            user_id: User UUID to check

        Returns:
            True if user exists, False otherwise
        """
        from contexts.user_management.application.queries import GetUserByIdQuery

        query = GetUserByIdQuery(user_id=user_id)
        result = await self._query_bus.dispatch(query)

        return result.is_success

    async def get_user_info(self, user_id: UUID) -> Optional[UserInfo]:
        """
        Get user info without raising exceptions.

        Args:
            user_id: User UUID

        Returns:
            UserInfo if found, None otherwise
        """
        try:
            return await self.verify_user(user_id)
        except (UserNotFoundError, UserInactiveError):
            return None
