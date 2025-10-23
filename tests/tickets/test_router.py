import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.models import Client
from src.tickets.models import Ticket, TicketStatus
from src.users.models import User


@pytest.fixture
async def test_client(db_session: AsyncSession) -> Client:
    client = Client(
        full_name="Test Client",
        email="client@test.com",
        phone="+1234567890",
        address="123 Test St",
    )
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    return client


@pytest.fixture
async def test_ticket(db_session: AsyncSession, test_client: Client, worker_user: User) -> Ticket:
    ticket = Ticket(
        title="Test Repair",
        description="Test description",
        status=TicketStatus.NEW,
        client_id=test_client.id,
        assigned_worker_id=worker_user.id,
    )
    db_session.add(ticket)
    await db_session.commit()
    await db_session.refresh(ticket)
    return ticket


@pytest.mark.asyncio
class TestTicketsRouter:
    async def test_create_ticket_public_success(self, client: AsyncClient):
        response = await client.post(
            "/tickets/public",
            json={
                "title": "Broken Phone Screen",
                "description": "The screen is cracked and needs replacement",
                "client_full_name": "John Doe",
                "client_email": "john@example.com",
                "client_phone": "+1234567890",
                "client_address": "123 Main St",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Broken Phone Screen"
        assert data["status"] == "new"
        assert data["client"]["email"] == "john@example.com"

    async def test_list_tickets_admin(self, client: AsyncClient, admin_headers: dict[str, str], test_ticket: Ticket):
        response = await client.get("/tickets", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert data["total_count"] >= 1

    async def test_list_tickets_worker(self, client: AsyncClient, worker_headers: dict[str, str], test_ticket: Ticket):
        response = await client.get("/tickets", headers=worker_headers)

        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        for ticket in data["tickets"]:
            assert ticket["assigned_worker_full_name"] is not None

    async def test_get_ticket_success(self, client: AsyncClient, admin_headers: dict[str, str], test_ticket: Ticket):
        response = await client.get(f"/tickets/{test_ticket.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_ticket.id
        assert data["title"] == test_ticket.title

    async def test_worker_cannot_see_unassigned_ticket(
        self, client: AsyncClient, worker_headers: dict[str, str], db_session: AsyncSession, test_client: Client
    ):
        unassigned_ticket = Ticket(
            title="Unassigned Ticket",
            description="Description",
            status=TicketStatus.NEW,
            client_id=test_client.id,
            assigned_worker_id=None,
        )
        db_session.add(unassigned_ticket)
        await db_session.commit()
        await db_session.refresh(unassigned_ticket)

        response = await client.get(f"/tickets/{unassigned_ticket.id}", headers=worker_headers)

        assert response.status_code == 403

    async def test_update_ticket_status_worker(
        self, client: AsyncClient, worker_headers: dict[str, str], test_ticket: Ticket
    ):
        response = await client.patch(
            f"/tickets/{test_ticket.id}/status",
            headers=worker_headers,
            json={"status": "in_progress"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    async def test_assign_ticket_admin(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        db_session: AsyncSession,
        test_client: Client,
        worker_user: User,
    ):
        ticket = Ticket(
            title="New Ticket",
            description="Description",
            status=TicketStatus.NEW,
            client_id=test_client.id,
        )
        db_session.add(ticket)
        await db_session.commit()
        await db_session.refresh(ticket)

        response = await client.post(
            f"/tickets/{ticket.id}/assign",
            headers=admin_headers,
            json={"worker_id": worker_user.id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assigned_worker"]["id"] == worker_user.id

    async def test_worker_cannot_assign_ticket(
        self, client: AsyncClient, worker_headers: dict[str, str], test_ticket: Ticket, admin_user: User
    ):
        response = await client.post(
            f"/tickets/{test_ticket.id}/assign",
            headers=worker_headers,
            json={"worker_id": admin_user.id},
        )

        assert response.status_code == 403

    async def test_delete_ticket_admin(self, client: AsyncClient, admin_headers: dict[str, str], test_ticket: Ticket):
        response = await client.delete(f"/tickets/{test_ticket.id}", headers=admin_headers)

        assert response.status_code == 204

        get_response = await client.get(f"/tickets/{test_ticket.id}", headers=admin_headers)
        assert get_response.status_code == 404

    async def test_search_by_title(self, client: AsyncClient, admin_headers: dict[str, str], test_ticket: Ticket):
        response = await client.get(f"/tickets?title={test_ticket.title[:4]}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 1

    async def test_filter_by_status(self, client: AsyncClient, admin_headers: dict[str, str], test_ticket: Ticket):
        response = await client.get("/tickets?status=new", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        for ticket in data["tickets"]:
            assert ticket["status"] == "new"

    async def test_pagination(self, client: AsyncClient, admin_headers: dict[str, str]):
        response = await client.get("/tickets?page=1&per_page=5", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5
        assert len(data["tickets"]) <= 5
