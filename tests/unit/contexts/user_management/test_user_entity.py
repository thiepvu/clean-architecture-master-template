"""Test User entity"""

import pytest

from contexts.user_management.domain.entities.user import User
from contexts.user_management.domain.exceptions.user_exceptions import (
    InvalidEmailException,
    InvalidUserStateException,
)


class TestUserEntity:
    """Test User domain entity"""

    def test_create_user(self):
        """Test user creation"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        assert user.email.value == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert len(user.domain_events) == 1

    def test_create_user_with_invalid_email(self):
        """Test user creation with invalid email raises exception"""
        with pytest.raises(InvalidEmailException):
            User.create(
                email="invalid-email", username="testuser", first_name="Test", last_name="User"
            )

    def test_update_profile(self):
        """Test updating user profile"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        user.update_profile("NewFirst", "NewLast")

        assert user.first_name == "NewFirst"
        assert user.last_name == "NewLast"
        assert user.full_name == "NewFirst NewLast"
        assert len(user.domain_events) == 2  # Created + Updated

    def test_change_email(self):
        """Test changing user email"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        user.change_email("newemail@example.com")

        assert user.email.value == "newemail@example.com"
        assert len(user.domain_events) == 2

    def test_change_email_invalid(self):
        """Test changing to invalid email raises exception"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        with pytest.raises(InvalidEmailException):
            user.change_email("invalid-email")

    def test_deactivate_user(self):
        """Test deactivating user"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        user.deactivate()

        assert user.is_active is False
        assert len(user.domain_events) == 2

    def test_deactivate_inactive_user_raises_exception(self):
        """Test deactivating inactive user raises exception"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        user.deactivate()

        with pytest.raises(InvalidUserStateException):
            user.deactivate()

    def test_activate_user(self):
        """Test activating user"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        user.deactivate()

        user.activate()

        assert user.is_active is True

    def test_activate_active_user_raises_exception(self):
        """Test activating active user raises exception"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        with pytest.raises(InvalidUserStateException):
            user.activate()

    def test_can_login_active_user(self):
        """Test active user can login"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        assert user.can_login() is True

    def test_can_login_inactive_user(self):
        """Test inactive user cannot login"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        user.deactivate()

        assert user.can_login() is False

    def test_can_login_deleted_user(self):
        """Test deleted user cannot login"""
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        user.mark_as_deleted()

        assert user.can_login() is False
