"""Test Unit of Work pattern"""

import pytest

from contexts.user_management.domain.entities.user import User
from infrastructure.database.orm.adapters.sqlalchemy.contexts.user_management.repositories import (
    UserRepository,
)
from infrastructure.database.orm.adapters.sqlalchemy.shared import BaseUnitOfWork


class TestUnitOfWork:
    """Test UnitOfWork transaction management"""

    @pytest.mark.asyncio
    async def test_commit_transaction(self, db_session):
        """Test successful transaction commit"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="uow@example.com", username="uowuser", first_name="UoW", last_name="User"
        )

        # Act
        async with BaseUnitOfWork(db_session) as uow:
            await repository.add(user)
            await uow.commit()

        # Assert
        retrieved = await repository.get_by_email("uow@example.com")
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_rollback_transaction(self, db_session):
        """Test transaction rollback on exception"""
        # Arrange
        repository = UserRepository(db_session)

        # Act & Assert
        with pytest.raises(Exception):
            async with BaseUnitOfWork(db_session):
                user = User.create(
                    email="rollback@example.com",
                    username="rollbackuser",
                    first_name="Rollback",
                    last_name="User",
                )
                await repository.add(user)
                raise Exception("Force rollback")

        # User should not be saved
        retrieved = await repository.get_by_email("rollback@example.com")
        assert retrieved is None
