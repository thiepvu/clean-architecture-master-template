"""
User Read Repository Interface.

This is the Query-side repository interface, separate from the
Write-side repository (IUserRepository in domain layer).

Read repositories:
- Return Read Models (DTOs), not domain entities
- Are optimized for queries
- May use different database tables/views
- Can include caching
- Never modify data
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..read_models import UserListItemReadModel, UserReadModel


class IUserReadRepository(ABC):
    """
    Read-only repository for User queries.

    This interface is used by Query Handlers to fetch data
    in a read-optimized way. It returns Read Models directly,
    avoiding the overhead of loading full domain entities.

    Note: This is separate from IUserRepository which is used
    by Command Handlers for write operations.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[UserReadModel]:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            UserReadModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserReadModel]:
        """
        Get user by email.

        Args:
            email: User email address

        Returns:
            UserReadModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[UserReadModel]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            UserReadModel if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[UserListItemReadModel]:
        """
        List users with pagination and optional filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status (optional)

        Returns:
            List of UserListItemReadModel
        """
        pass

    @abstractmethod
    async def count(self, is_active: Optional[bool] = None) -> int:
        """
        Count users matching criteria.

        Args:
            is_active: Filter by active status (optional)

        Returns:
            Count of matching users
        """
        pass

    @abstractmethod
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[UserListItemReadModel]:
        """
        Search users by term.

        Searches in username, email, first_name, last_name.

        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching UserListItemReadModel
        """
        pass

    @abstractmethod
    async def exists(self, user_id: UUID) -> bool:
        """
        Check if user exists.

        Args:
            user_id: User UUID

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def email_exists(self, email: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """
        Check if email is already in use.

        Args:
            email: Email to check
            exclude_user_id: User ID to exclude from check (for updates)

        Returns:
            True if email exists, False otherwise
        """
        pass

    @abstractmethod
    async def username_exists(self, username: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """
        Check if username is already in use.

        Args:
            username: Username to check
            exclude_user_id: User ID to exclude from check (for updates)

        Returns:
            True if username exists, False otherwise
        """
        pass
