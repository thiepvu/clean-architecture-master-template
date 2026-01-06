"""Test User repository with real database"""

from uuid import uuid4

import pytest

from contexts.user_management.domain.entities.user import User
from infrastructure.database.orm.adapters.sqlalchemy.contexts.user_management.repositories import (
    UserRepository,
)


class TestUserRepository:
    """Test UserRepository with real database"""

    @pytest.mark.asyncio
    async def test_add_user(self, db_session):
        """Test adding user to database"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )

        # Act
        saved_user = await repository.add(user)
        await db_session.commit()

        # Assert
        assert saved_user.id is not None
        assert saved_user.email.value == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session):
        """Test getting user by ID"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        saved_user = await repository.add(user)
        await db_session.commit()

        # Act
        retrieved_user = await repository.get_by_id(saved_user.id)

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == saved_user.id
        assert retrieved_user.email.value == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent user returns None"""
        # Arrange
        repository = UserRepository(db_session)

        # Act
        user = await repository.get_by_id(uuid4())

        # Assert
        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email(self, db_session):
        """Test getting user by email"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        await repository.add(user)
        await db_session.commit()

        # Act
        retrieved_user = await repository.get_by_email("test@example.com")

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.email.value == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_username(self, db_session):
        """Test getting user by username"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        await repository.add(user)
        await db_session.commit()

        # Act
        retrieved_user = await repository.get_by_username("testuser")

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_update_user(self, db_session):
        """Test updating user"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        saved_user = await repository.add(user)
        await db_session.commit()

        # Act
        saved_user.update_profile("NewFirst", "NewLast")
        updated_user = await repository.update(saved_user)
        await db_session.commit()

        # Assert
        assert updated_user.first_name == "NewFirst"
        assert updated_user.last_name == "NewLast"

    @pytest.mark.asyncio
    async def test_delete_user_soft(self, db_session):
        """Test soft deleting user"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="test@example.com", username="testuser", first_name="Test", last_name="User"
        )
        saved_user = await repository.add(user)
        await db_session.commit()

        # Act
        await repository.delete(saved_user.id, soft=True)
        await db_session.commit()

        # Assert
        deleted_user = await repository.get_by_id(saved_user.id)
        assert deleted_user is None  # Soft deleted users not returned by default

    @pytest.mark.asyncio
    async def test_get_all(self, db_session):
        """Test getting all users"""
        # Arrange
        repository = UserRepository(db_session)

        # Create multiple users
        for i in range(3):
            user = User.create(
                email=f"test{i}@example.com",
                username=f"testuser{i}",
                first_name=f"Test{i}",
                last_name=f"User{i}",
            )
            await repository.add(user)
        await db_session.commit()

        # Act
        users = await repository.get_all(skip=0, limit=10)

        # Assert
        assert len(users) >= 3

    @pytest.mark.asyncio
    async def test_count(self, db_session):
        """Test counting users"""
        # Arrange
        repository = UserRepository(db_session)

        # Create users
        for i in range(5):
            user = User.create(
                email=f"count{i}@example.com",
                username=f"countuser{i}",
                first_name=f"Count{i}",
                last_name=f"User{i}",
            )
            await repository.add(user)
        await db_session.commit()

        # Act
        count = await repository.count()

        # Assert
        assert count >= 5

    @pytest.mark.asyncio
    async def test_search_users(self, db_session):
        """Test searching users"""
        # Arrange
        repository = UserRepository(db_session)
        user = User.create(
            email="searchable@example.com",
            username="searchableuser",
            first_name="Searchable",
            last_name="User",
        )
        await repository.add(user)
        await db_session.commit()

        # Act
        results = await repository.search(
            search_term="searchable", search_fields=["username", "first_name", "email"]
        )

        # Assert
        assert len(results) >= 1
        assert any(u.username == "searchableuser" for u in results)
