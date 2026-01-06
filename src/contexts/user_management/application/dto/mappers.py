"""User entity to DTO mappers"""

from typing import List

from contexts.user_management.domain.entities.user import User

from ..read_models import UserListItemReadModel, UserReadModel
from .user_dto import UserListResponseDTO, UserResponseDTO


class UserMapper:
    """User domain entity to DTO mapper"""

    @staticmethod
    def to_read_model(user: User) -> UserReadModel:
        """
        Convert user entity to read model.

        Used by command handlers to return consistent read models.

        Args:
            user: User domain entity

        Returns:
            UserReadModel
        """
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

    @staticmethod
    def to_list_item_read_model(user: User) -> UserListItemReadModel:
        """
        Convert user entity to list item read model.

        Args:
            user: User domain entity

        Returns:
            UserListItemReadModel
        """
        return UserListItemReadModel(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email.value,
            is_active=user.is_active,
        )

    @staticmethod
    def to_response_dto(user: User) -> UserResponseDTO:
        """
        Convert user entity to response DTO.

        Args:
            user: User domain entity

        Returns:
            UserResponseDTO
        """
        return UserResponseDTO(
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

    @staticmethod
    def to_list_dto(user: User) -> UserListResponseDTO:
        """
        Convert user entity to list DTO.

        Args:
            user: User domain entity

        Returns:
            UserListResponseDTO
        """
        return UserListResponseDTO(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email.value,
            is_active=user.is_active,
        )

    @staticmethod
    def to_list_dtos(users: List[User]) -> List[UserListResponseDTO]:
        """
        Convert list of user entities to list DTOs.

        Args:
            users: List of user entities

        Returns:
            List of UserListResponseDTO
        """
        return [UserMapper.to_list_dto(user) for user in users]
