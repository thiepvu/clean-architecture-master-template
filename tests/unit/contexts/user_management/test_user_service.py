"""Test User service"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from contexts.user_management.application.dto.user_dto import UserCreateDTO, UserUpdateDTO
from contexts.user_management.application.facades.user_facade import UserManagementFacade
from contexts.user_management.domain.entities.user import User
from shared.errors import ConflictException, NotFoundException


class TestUserService:
    """Test UserService application service"""

    @pytest.fixture
    def mock_repository(self):
        """Create mock user repository"""
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_repository):
        """Create user service with mock repository"""
        return UserManagementFacade(mock_repository)

    @pytest.fixture
    def sample_user(self):
        """Create sample user"""
        return User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_repository, sample_user):
        """Test successful user creation"""
        # Arrange
        dto = UserCreateDTO(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        mock_repository.get_by_email.return_value = None
        mock_repository.get_by_username.return_value = None
        mock_repository.add.return_value = sample_user

        # Act
        result = await user_service.create_user(dto)

        # Assert
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        mock_repository.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_email_conflict(self, user_service, mock_repository, sample_user):
        """Test user creation fails when email exists"""
        # Arrange
        dto = UserCreateDTO(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        mock_repository.get_by_email.return_value = sample_user

        # Act & Assert
        with pytest.raises(ConflictException):
            await user_service.create_user(dto)

    @pytest.mark.asyncio
    async def test_create_user_username_conflict(self, user_service, mock_repository, sample_user):
        """Test user creation fails when username exists"""
        # Arrange
        dto = UserCreateDTO(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        mock_repository.get_by_email.return_value = None
        mock_repository.get_by_username.return_value = sample_user

        # Act & Assert
        with pytest.raises(ConflictException):
            await user_service.create_user(dto)

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, mock_repository, sample_user):
        """Test successful user retrieval"""
        # Arrange
        user_id = sample_user.id
        mock_repository.get_by_id.return_value = sample_user

        # Act
        result = await user_service.get_user(user_id)

        # Assert
        assert result.id == user_id
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_repository):
        """Test user retrieval fails when user not found"""
        # Arrange
        user_id = uuid4()
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(NotFoundException):
            await user_service.get_user(user_id)

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, mock_repository, sample_user):
        """Test successful user update"""
        # Arrange
        dto = UserUpdateDTO(first_name="NewFirst", last_name="NewLast")
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.update.return_value = sample_user

        # Act
        result = await user_service.update_user(sample_user.id, dto)

        # Assert
        assert result is not None
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_service, mock_repository):
        """Test successful user deletion"""
        # Arrange
        user_id = uuid4()
        mock_repository.exists.return_value = True

        # Act
        await user_service.delete_user(user_id)

        # Assert
        mock_repository.delete.assert_called_once_with(user_id, soft=True)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_service, mock_repository):
        """Test user deletion fails when user not found"""
        # Arrange
        user_id = uuid4()
        mock_repository.exists.return_value = False

        # Act & Assert
        with pytest.raises(NotFoundException):
            await user_service.delete_user(user_id)
