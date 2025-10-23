import pytest
from httpx import AsyncClient

from src.users.models import User


@pytest.mark.asyncio
class TestAuthRouter:
    async def test_login_success(self, client: AsyncClient, admin_user: User):
        response = await client.post(
            "/auth/login",
            data={
                "username": admin_user.email,
                "password": "admin123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, admin_user: User):
        response = await client.post(
            "/auth/login",
            data={
                "username": admin_user.email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistent@test.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401

    async def test_get_me_success(self, client: AsyncClient, admin_headers: dict[str, str], admin_user: User):
        response = await client.get("/auth/me", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == admin_user.email
        assert data["full_name"] == admin_user.full_name
        assert data["role"] == admin_user.role

    async def test_get_me_without_token(self, client: AsyncClient):
        response = await client.get("/auth/me")

        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        response = await client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401
