import pytest
from httpx import AsyncClient

from src.users.models import User


@pytest.mark.asyncio
class TestUsersRouter:
    async def test_create_user_success(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.post(
            "/users",
            headers=admin_headers,
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "full_name": "New User",
                "role": "worker",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["role"] == "worker"
        assert "password" not in data

    async def test_create_user_duplicate_email(
        self, client: AsyncClient, admin_headers: dict[str, str], worker_user: User
    ):
        response = await client.post(
            "/users",
            headers=admin_headers,
            json={
                "email": worker_user.email,
                "password": "password123",
                "full_name": "Duplicate User",
                "role": "worker",
            },
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    async def test_create_user_worker_forbidden(self, client: AsyncClient, worker_headers: dict[str, str]):
        response = await client.post(
            "/users",
            headers=worker_headers,
            json={
                "email": "newuser@test.com",
                "password": "password123",
                "full_name": "New User",
                "role": "worker",
            },
        )

        assert response.status_code == 403

    async def test_list_users(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.get("/users", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total_count" in data
        assert data["total_count"] >= 2

    async def test_get_user_by_id(self, client: AsyncClient, admin_headers: dict[str, str], worker_user: User):
        response = await client.get(f"/users/{worker_user.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == worker_user.id
        assert data["email"] == worker_user.email

    async def test_update_user(self, client: AsyncClient, admin_headers: dict[str, str], worker_user: User):
        response = await client.patch(
            f"/users/{worker_user.id}",
            headers=admin_headers,
            json={"full_name": "Updated Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    async def test_delete_user(self, client: AsyncClient, admin_headers: dict[str, str], worker_user: User):
        response = await client.delete(f"/users/{worker_user.id}", headers=admin_headers)

        assert response.status_code == 204

        get_response = await client.get(f"/users/{worker_user.id}", headers=admin_headers)
        assert get_response.status_code == 404
