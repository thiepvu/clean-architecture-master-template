"""End-to-end tests for User API"""

import pytest
from httpx import AsyncClient


class TestUserAPI:
    """Test User API endpoints"""

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient):
        """Test POST /api/v1/users"""
        # Arrange
        user_data = {
            "email": "api@example.com",
            "username": "apiuser",
            "first_name": "API",
            "last_name": "User",
        }

        # Act
        response = await client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "api@example.com"
        assert data["data"]["username"] == "apiuser"
        assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient):
        """Test creating user with duplicate email fails"""
        # Arrange
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "first_name": "User",
            "last_name": "One",
        }
        await client.post("/api/v1/users", json=user_data)

        # Act - Try to create another user with same email
        duplicate_data = {
            "email": "duplicate@example.com",
            "username": "user2",
            "first_name": "User",
            "last_name": "Two",
        }
        response = await client.post("/api/v1/users", json=duplicate_data)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, client: AsyncClient):
        """Test creating user with invalid email fails"""
        # Arrange
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        }

        # Act
        response = await client.post("/api/v1/users", json=user_data)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user(self, client: AsyncClient):
        """Test GET /api/v1/users/{id}"""
        # Arrange - Create a user first
        user_data = {
            "email": "get@example.com",
            "username": "getuser",
            "first_name": "Get",
            "last_name": "User",
        }
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["data"]["id"]

        # Act
        response = await client.get(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == user_id
        assert data["data"]["email"] == "get@example.com"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        """Test getting non-existent user returns 404"""
        # Arrange
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        # Act
        response = await client.get(f"/api/v1/users/{fake_uuid}")

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient):
        """Test PUT /api/v1/users/{id}"""
        # Arrange - Create a user first
        user_data = {
            "email": "update@example.com",
            "username": "updateuser",
            "first_name": "Update",
            "last_name": "User",
        }
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["data"]["id"]

        # Act
        update_data = {"first_name": "Updated", "last_name": "Name"}
        response = await client.put(f"/api/v1/users/{user_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["first_name"] == "Updated"
        assert data["data"]["last_name"] == "Name"

    @pytest.mark.asyncio
    async def test_update_user_email(self, client: AsyncClient):
        """Test PATCH /api/v1/users/{id}/email"""
        # Arrange - Create a user first
        user_data = {
            "email": "oldemail@example.com",
            "username": "emailuser",
            "first_name": "Email",
            "last_name": "User",
        }
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["data"]["id"]

        # Act
        update_data = {"email": "newemail@example.com"}
        response = await client.patch(f"/api/v1/users/{user_id}/email", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "newemail@example.com"

    @pytest.mark.asyncio
    async def test_activate_user(self, client: AsyncClient):
        """Test POST /api/v1/users/{id}/activate"""
        # Arrange - Create and deactivate a user
        user_data = {
            "email": "activate@example.com",
            "username": "activateuser",
            "first_name": "Activate",
            "last_name": "User",
        }
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["data"]["id"]
        await client.post(f"/api/v1/users/{user_id}/deactivate")

        # Act
        response = await client.post(f"/api/v1/users/{user_id}/activate")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_active"] is True

    @pytest.mark.asyncio
    async def test_deactivate_user(self, client: AsyncClient):
        """Test POST /api/v1/users/{id}/deactivate"""
        # Arrange - Create a user
        user_data = {
            "email": "deactivate@example.com",
            "username": "deactivateuser",
            "first_name": "Deactivate",
            "last_name": "User",
        }
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["data"]["id"]

        # Act
        response = await client.post(f"/api/v1/users/{user_id}/deactivate")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient):
        """Test DELETE /api/v1/users/{id}"""
        # Arrange - Create a user
        user_data = {
            "email": "delete@example.com",
            "username": "deleteuser",
            "first_name": "Delete",
            "last_name": "User",
        }
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["data"]["id"]

        # Act
        response = await client.delete(f"/api/v1/users/{user_id}")

        # Assert
        assert response.status_code == 200

        # Verify user is deleted (soft delete)
        get_response = await client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient):
        """Test GET /api/v1/users"""
        # Arrange - Create some users
        for i in range(3):
            user_data = {
                "email": f"list{i}@example.com",
                "username": f"listuser{i}",
                "first_name": f"List{i}",
                "last_name": f"User{i}",
            }
            await client.post("/api/v1/users", json=user_data)

        # Act
        response = await client.get("/api/v1/users")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert "meta" in data["data"]
        assert len(data["data"]["items"]) >= 3

    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, client: AsyncClient):
        """Test GET /api/v1/users with pagination"""
        # Act
        response = await client.get("/api/v1/users?page=1&page_size=5")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["meta"]["page"] == 1
        assert data["data"]["meta"]["page_size"] == 5

    @pytest.mark.asyncio
    async def test_list_users_filter_active(self, client: AsyncClient):
        """Test GET /api/v1/users?is_active=true"""
        # Arrange - Create active and inactive users
        active_user = {
            "email": "active@example.com",
            "username": "activeuser",
            "first_name": "Active",
            "last_name": "User",
        }
        await client.post("/api/v1/users", json=active_user)

        inactive_user_data = {
            "email": "inactive@example.com",
            "username": "inactiveuser",
            "first_name": "Inactive",
            "last_name": "User",
        }
        inactive_response = await client.post("/api/v1/users", json=inactive_user_data)
        inactive_id = inactive_response.json()["data"]["id"]
        await client.post(f"/api/v1/users/{inactive_id}/deactivate")

        # Act
        response = await client.get("/api/v1/users?is_active=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        users = data["data"]["items"]
        assert all(user["is_active"] is True for user in users)

    @pytest.mark.asyncio
    async def test_search_users(self, client: AsyncClient):
        """Test GET /api/v1/users?search=term"""
        # Arrange - Create a searchable user
        user_data = {
            "email": "searchme@example.com",
            "username": "searchmeuser",
            "first_name": "SearchMe",
            "last_name": "User",
        }
        await client.post("/api/v1/users", json=user_data)

        # Act
        response = await client.get("/api/v1/users?search=searchme")

        # Assert
        assert response.status_code == 200
        data = response.json()
        users = data["data"]["items"]
        assert len(users) >= 1
        assert any("searchme" in user["username"].lower() for user in users)
