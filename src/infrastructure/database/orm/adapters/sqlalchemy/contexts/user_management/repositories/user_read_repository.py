"""
User Read Repository Implementation.

This is the Query-side repository that returns Read Models directly.
Optimized for read operations with no domain logic.

NOTE: This repository manages its own sessions (short-lived).
It does NOT use UnitOfWork - that's for Write operations only.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from contexts.user_management.application.ports.user_read_repository import IUserReadRepository
from contexts.user_management.application.read_models import UserListItemReadModel, UserReadModel

from ..models.user_model import UserModel


class UserReadRepository(IUserReadRepository):
    """
    Read-only repository for User queries.

    Returns Read Models directly from the database,
    bypassing domain entity construction for better performance.

    Session Management:
    - Each query method creates its own short-lived session
    - No dependency on UnitOfWork (CQRS separation)
    - Sessions are auto-closed after each operation
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize repository with session factory.

        Args:
            session_factory: Factory for creating new sessions
        """
        self._session_factory = session_factory

    async def get_by_id(self, user_id: UUID) -> Optional[UserReadModel]:
        """Get user by ID."""
        async with self._session_factory() as session:
            stmt = select(UserModel).where(
                UserModel.id == user_id,
                UserModel.is_deleted == False,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_read_model(model)

    async def get_by_email(self, email: str) -> Optional[UserReadModel]:
        """Get user by email."""
        async with self._session_factory() as session:
            stmt = select(UserModel).where(
                UserModel.email == email.lower(),
                UserModel.is_deleted == False,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_read_model(model)

    async def get_by_username(self, username: str) -> Optional[UserReadModel]:
        """Get user by username."""
        async with self._session_factory() as session:
            stmt = select(UserModel).where(
                UserModel.username == username.lower(),
                UserModel.is_deleted == False,
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model is None:
                return None

            return self._to_read_model(model)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[UserListItemReadModel]:
        """List users with pagination and optional filtering."""
        async with self._session_factory() as session:
            stmt = select(UserModel).where(UserModel.is_deleted == False)

            if is_active is not None:
                stmt = stmt.where(UserModel.is_active == is_active)

            stmt = stmt.offset(skip).limit(limit).order_by(UserModel.created_at.desc())

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._to_list_item(model) for model in models]

    async def count(self, is_active: Optional[bool] = None) -> int:
        """Count users matching criteria."""
        async with self._session_factory() as session:
            stmt = select(func.count()).select_from(UserModel).where(UserModel.is_deleted == False)

            if is_active is not None:
                stmt = stmt.where(UserModel.is_active == is_active)

            result = await session.execute(stmt)
            return result.scalar_one()

    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[UserListItemReadModel]:
        """Search users by term."""
        async with self._session_factory() as session:
            search_pattern = f"%{search_term}%"

            stmt = (
                select(UserModel)
                .where(
                    UserModel.is_deleted == False,
                    or_(
                        UserModel.username.ilike(search_pattern),
                        UserModel.email.ilike(search_pattern),
                        UserModel.first_name.ilike(search_pattern),
                        UserModel.last_name.ilike(search_pattern),
                    ),
                )
                .offset(skip)
                .limit(limit)
                .order_by(UserModel.username)
            )

            result = await session.execute(stmt)
            models = result.scalars().all()

            return [self._to_list_item(model) for model in models]

    async def exists(self, user_id: UUID) -> bool:
        """Check if user exists."""
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(UserModel)
                .where(
                    UserModel.id == user_id,
                    UserModel.is_deleted == False,
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one() > 0

    async def email_exists(self, email: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if email is already in use."""
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(UserModel)
                .where(
                    UserModel.email == email.lower(),
                    UserModel.is_deleted == False,
                )
            )

            if exclude_user_id is not None:
                stmt = stmt.where(UserModel.id != exclude_user_id)

            result = await session.execute(stmt)
            return result.scalar_one() > 0

    async def username_exists(self, username: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if username is already in use."""
        async with self._session_factory() as session:
            stmt = (
                select(func.count())
                .select_from(UserModel)
                .where(
                    UserModel.username == username.lower(),
                    UserModel.is_deleted == False,
                )
            )

            if exclude_user_id is not None:
                stmt = stmt.where(UserModel.id != exclude_user_id)

            result = await session.execute(stmt)
            return result.scalar_one() > 0

    def _to_read_model(self, model: UserModel) -> UserReadModel:
        """Convert ORM model to read model."""
        return UserReadModel(
            id=model.id,  # type: ignore[arg-type]
            email=str(model.email),
            username=str(model.username),
            first_name=str(model.first_name),
            last_name=str(model.last_name),
            full_name=f"{model.first_name} {model.last_name}",
            is_active=bool(model.is_active),
            created_at=model.created_at,  # type: ignore[arg-type]
            updated_at=model.updated_at,  # type: ignore[arg-type]
        )

    def _to_list_item(self, model: UserModel) -> UserListItemReadModel:
        """Convert ORM model to list item read model."""
        return UserListItemReadModel(
            id=model.id,  # type: ignore[arg-type]
            username=str(model.username),
            full_name=f"{model.first_name} {model.last_name}",
            email=str(model.email),
            is_active=bool(model.is_active),
        )
