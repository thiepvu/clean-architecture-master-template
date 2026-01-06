"""User domain entity"""

from typing import Optional
from uuid import UUID

from shared.domain.base_aggregate import AggregateRoot

from ..events.user_events import (
    UserActivatedEvent,
    UserCreatedEvent,
    UserDeactivatedEvent,
    UserUpdatedEvent,
)
from ..exceptions.user_exceptions import InvalidUserStateException
from ..value_objects.email import Email


class User(AggregateRoot):
    """
    User domain entity (Aggregate Root).
    Represents a user in the system with all business logic.
    """

    def __init__(
        self,
        email: Email,
        username: str,
        first_name: str,
        last_name: str,
        is_active: bool = True,
        id: Optional[UUID] = None,
    ):
        """
        Initialize user entity.

        Args:
            email: User email as value object
            username: Unique username
            first_name: User's first name
            last_name: User's last name
            is_active: Whether user is active
            id: Entity UUID (generated if not provided)
        """
        super().__init__(id)
        self._email = email
        self._username = username
        self._first_name = first_name
        self._last_name = last_name
        self._is_active = is_active

    # Properties (read-only access)

    @property
    def email(self) -> Email:
        """Get user email"""
        return self._email

    @property
    def username(self) -> str:
        """Get username"""
        return self._username

    @property
    def first_name(self) -> str:
        """Get first name"""
        return self._first_name

    @property
    def last_name(self) -> str:
        """Get last name"""
        return self._last_name

    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self._first_name} {self._last_name}"

    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self._is_active

    # Factory method

    @staticmethod
    def create(email: str, username: str, first_name: str, last_name: str) -> "User":
        """
        Factory method to create a new user.
        Enforces business rules and emits domain events.

        Args:
            email: User email address
            username: Unique username
            first_name: User's first name
            last_name: User's last name

        Returns:
            New User instance

        Raises:
            InvalidEmailException: If email format is invalid
        """
        # Create email value object (validates format)
        email_vo = Email(email)

        # Create user
        user = User(
            email=email_vo,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        # Emit domain event
        user.add_domain_event(UserCreatedEvent(user.id, email))

        return user

    # Business logic methods

    def update_profile(self, first_name: str, last_name: str) -> None:
        """
        Update user profile information.

        Args:
            first_name: New first name
            last_name: New last name
        """
        self._first_name = first_name
        self._last_name = last_name
        self.update_timestamp()

        # Emit domain event
        self.add_domain_event(UserUpdatedEvent(self.id))

    def change_email(self, new_email: str) -> None:
        """
        Change user email address.

        Args:
            new_email: New email address

        Raises:
            InvalidEmailException: If email format is invalid
        """
        # Validate new email
        new_email_vo = Email(new_email)

        # Update email
        old_email = self._email.value
        self._email = new_email_vo
        self.update_timestamp()

        # Emit domain event
        self.add_domain_event(
            UserUpdatedEvent(self.id, {"old_email": old_email, "new_email": new_email})
        )

    def deactivate(self) -> None:
        """
        Deactivate user account.

        Raises:
            InvalidUserStateException: If user is already inactive
        """
        if not self._is_active:
            raise InvalidUserStateException("User is already inactive")

        self._is_active = False
        self.update_timestamp()

        # Emit domain event
        self.add_domain_event(UserDeactivatedEvent(self.id))

    def activate(self) -> None:
        """
        Activate user account.

        Raises:
            InvalidUserStateException: If user is already active
        """
        if self._is_active:
            raise InvalidUserStateException("User is already active")

        self._is_active = True
        self.update_timestamp()

        # Emit domain event
        self.add_domain_event(UserActivatedEvent(self.id))

    def can_login(self) -> bool:
        """
        Check if user can login.

        Returns:
            True if user can login, False otherwise
        """
        return self._is_active and not self._is_deleted
