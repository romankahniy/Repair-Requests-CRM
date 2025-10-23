import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.models import Client


@pytest.fixture
async def test_client(db_session: AsyncSession) -> Client:
    client = Client(
        full_name="Test Client",
        email="testclient@example.com",
        phone="+1234567890",
        address="123 Test Street",
    )
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    return client


@pytest.mark.asyncio
class TestClientsRouter:
    async def test_create_client_success(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.post(
            "/clients",
            headers=admin_headers,
            json={
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1987654321",
                "address": "456 Main Street",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone"] == "+1987654321"
        assert data["address"] == "456 Main Street"
        assert "id" in data

    async def test_create_client_worker_can_create(self, client: AsyncClient, worker_headers: dict[str, str]):
        response = await client.post(
            "/clients",
            headers=worker_headers,
            json={
                "full_name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "+1555555555",
                "address": "789 Oak Avenue",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Jane Smith"

    async def test_create_client_without_auth(self, client: AsyncClient):
        response = await client.post(
            "/clients",
            json={
                "full_name": "Test User",
                "email": "test@example.com",
                "phone": "+1234567890",
            },
        )

        assert response.status_code == 401

    async def test_create_client_invalid_email(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.post(
            "/clients",
            headers=admin_headers,
            json={
                "full_name": "Invalid Email User",
                "email": "invalid-email",
                "phone": "+1234567890",
            },
        )

        assert response.status_code == 422

    async def test_create_client_missing_required_fields(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.post(
            "/clients",
            headers=admin_headers,
            json={
                "full_name": "Missing Fields",
            },
        )

        assert response.status_code == 422

    async def test_list_clients_admin(self, client: AsyncClient, admin_headers: dict[str, str], test_client: Client):
        response = await client.get("/clients", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert "clients" in data
        assert "total_count" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
        assert data["total_count"] >= 1
        assert len(data["clients"]) >= 1

    async def test_list_clients_worker(self, client: AsyncClient, worker_headers: dict[str, str], test_client: Client):
        response = await client.get("/clients", headers=worker_headers)

        assert response.status_code == 200
        data = response.json()
        assert "clients" in data

    async def test_list_clients_pagination(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.get("/clients?page=1&per_page=5", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5
        assert len(data["clients"]) <= 5

    async def test_list_clients_without_auth(self, client: AsyncClient):
        response = await client.get("/clients")

        assert response.status_code == 401

    async def test_get_client_by_id_admin(
        self, client: AsyncClient, admin_headers: dict[str, str], test_client: Client
    ):
        response = await client.get(f"/clients/{test_client.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_client.id
        assert data["full_name"] == test_client.full_name
        assert data["email"] == test_client.email
        assert data["phone"] == test_client.phone
        assert data["address"] == test_client.address

    async def test_get_client_by_id_worker(
        self, client: AsyncClient, worker_headers: dict[str, str], test_client: Client
    ):
        response = await client.get(f"/clients/{test_client.id}", headers=worker_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_client.id

    async def test_get_client_not_found(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.get("/clients/99999", headers=admin_headers)

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    async def test_update_client_admin(self, client: AsyncClient, admin_headers: dict[str, str], test_client: Client):
        response = await client.patch(
            f"/clients/{test_client.id}",
            headers=admin_headers,
            json={
                "full_name": "Updated Name",
                "phone": "+1999999999",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["phone"] == "+1999999999"
        assert data["email"] == test_client.email

    async def test_update_client_email(self, client: AsyncClient, admin_headers: dict[str, str], test_client: Client):
        response = await client.patch(
            f"/clients/{test_client.id}",
            headers=admin_headers,
            json={
                "email": "newemail@example.com",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"

    async def test_update_client_worker_forbidden(
        self, client: AsyncClient, worker_headers: dict[str, str], test_client: Client
    ):
        response = await client.patch(
            f"/clients/{test_client.id}",
            headers=worker_headers,
            json={
                "full_name": "Should Not Update",
            },
        )

        assert response.status_code == 403

    async def test_update_client_partial(self, client: AsyncClient, admin_headers: dict[str, str], test_client: Client):
        response = await client.patch(
            f"/clients/{test_client.id}",
            headers=admin_headers,
            json={
                "address": "New Address 123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["address"] == "New Address 123"
        assert data["full_name"] == test_client.full_name

    async def test_update_client_not_found(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.patch(
            "/clients/99999",
            headers=admin_headers,
            json={
                "full_name": "Does Not Exist",
            },
        )

        assert response.status_code == 404

    async def test_delete_client_admin(self, client: AsyncClient, admin_headers: dict[str, str], test_client: Client):
        response = await client.delete(f"/clients/{test_client.id}", headers=admin_headers)

        assert response.status_code == 204

        get_response = await client.get(f"/clients/{test_client.id}", headers=admin_headers)
        assert get_response.status_code == 404

    async def test_delete_client_worker_forbidden(
        self, client: AsyncClient, worker_headers: dict[str, str], test_client: Client
    ):
        response = await client.delete(f"/clients/{test_client.id}", headers=worker_headers)

        assert response.status_code == 403

    async def test_delete_client_not_found(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.delete("/clients/99999", headers=admin_headers)

        assert response.status_code == 404

    async def test_create_client_without_address(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.post(
            "/clients",
            headers=admin_headers,
            json={
                "full_name": "No Address User",
                "email": "noaddress@example.com",
                "phone": "+1234567890",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["address"] is None

    async def test_list_clients_empty_database(
        self, client: AsyncClient, admin_headers: dict[str, str], db_session: AsyncSession
    ):

        await db_session.execute("DELETE FROM clients")
        await db_session.commit()

        response = await client.get("/clients", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert len(data["clients"]) == 0

    async def test_create_multiple_clients_same_email_allowed(self, client: AsyncClient, admin_headers: dict[str, str]):
        client_data = {
            "full_name": "Duplicate Email User",
            "email": "duplicate@example.com",
            "phone": "+1234567890",
        }

        response1 = await client.post("/clients", headers=admin_headers, json=client_data)
        assert response1.status_code == 201

        response2 = await client.post("/clients", headers=admin_headers, json=client_data)
        assert response2.status_code == 201

        assert response1.json()["id"] != response2.json()["id"]
