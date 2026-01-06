"""User repository implementation"""

from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contexts.user_management.application.ports.user_repository import IUserRepository
from contexts.user_management.domain.entities.user import User
from contexts.user_management.domain.value_objects.email import Email
from infrastructure.database.orm.adapters.sqlalchemy.shared import BaseRepository

from ..models.user_model import UserModel


class UserRepository(BaseRepository[User, UserModel], IUserRepository):
    """
    User repository implementation.

    Receives session from UoW via constructor injection.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository with session.

        Args:
            session: SQLAlchemy async session from UoW
        """
        super().__init__(session, User, UserModel)

    async def save(self, user: User) -> User:
        """
        Persist a user entity. Delegates to add() for new entities (no id)
        or update() for existing ones.
        """
        if getattr(user, "id", None) is None:
            return await self.add(user)
        return await self.update(user)

    async def delete(self, user: User) -> None:  # type: ignore[override]
        """Delete a user (soft delete)."""
        from uuid import UUID as PyUUID

        user_id = user.id
        if isinstance(user_id, PyUUID):
            await super().delete(user_id, soft=True)

    async def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User entity if found, None otherwise
        """
        email_value = email.value if hasattr(email, "value") else str(email)
        stmt = select(UserModel).where(
            UserModel.email == email_value.lower(), UserModel.is_deleted == False
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username

        Returns:
            User entity if found, None otherwise
        """
        stmt = select(UserModel).where(
            UserModel.username == username.lower(), UserModel.is_deleted == False
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def count_by_criteria(self, filters: Dict[str, Any]) -> int:
        """
        Count users matching criteria.

        Args:
            filters: Filter criteria

        Returns:
            Count of matching users
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(UserModel).where(UserModel.is_deleted == False)

        for field, value in filters.items():
            if hasattr(UserModel, field):
                column = getattr(UserModel, field)
                stmt = stmt.where(column == value)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _to_entity(self, model: UserModel) -> User:
        """
        Convert ORM model to domain entity.

        Args:
            model: User ORM model

        Returns:
            User domain entity
        """
        user = User(
            email=Email(str(model.email)),
            username=str(model.username),
            first_name=str(model.first_name),
            last_name=str(model.last_name),
            is_active=bool(model.is_active),
            id=model.id,  # type: ignore[arg-type]
        )

        # Set internal timestamps from model
        user._created_at = model.created_at  # type: ignore[assignment]
        user._updated_at = model.updated_at  # type: ignore[assignment]
        user._is_deleted = model.is_deleted  # type: ignore[assignment]

        return user

    def _to_model(self, entity: User) -> UserModel:
        """
        Convert domain entity to ORM model.

        Args:
            entity: User domain entity

        Returns:
            User ORM model
        """
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            username=entity.username,
            first_name=entity.first_name,
            last_name=entity.last_name,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_deleted=entity.is_deleted,
        )
