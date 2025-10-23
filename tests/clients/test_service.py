import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.exceptions import ClientNotFoundError
from src.clients.schemas import ClientCreate, ClientUpdate
from src.clients.service import ClientService


@pytest.mark.asyncio
class TestClientService:
    async def test_create_client_success(self, db_session: AsyncSession):
        service = ClientService(db_session)

        data = ClientCreate(
            full_name="Service Test Client",
            email="service@test.com",
            phone="+1234567890",
            address="Service Test Address",
        )

        client = await service.create_client(data)

        assert client.id is not None
        assert client.full_name == "Service Test Client"
        assert client.email == "service@test.com"

    async def test_get_client_success(self, db_session: AsyncSession):
        service = ClientService(db_session)

        create_data = ClientCreate(
            full_name="Get Test",
            email="get@test.com",
            phone="+1234567890",
        )
        created = await service.create_client(create_data)

        client = await service.get_client(created.id)

        assert client.id == created.id
        assert client.full_name == created.full_name

    async def test_get_client_not_found(self, db_session: AsyncSession):
        service = ClientService(db_session)

        with pytest.raises(ClientNotFoundError):
            await service.get_client(99999)

    async def test_get_clients_pagination(self, db_session: AsyncSession):
        service = ClientService(db_session)

        for i in range(5):
            data = ClientCreate(
                full_name=f"Client {i}",
                email=f"client{i}@test.com",
                phone=f"+123456789{i}",
            )
            await service.create_client(data)

        clients, total, total_pages = await service.get_clients(page=1, per_page=3)

        assert len(clients) == 3
        assert total == 5
        assert total_pages == 2

    async def test_update_client_success(self, db_session: AsyncSession):
        service = ClientService(db_session)

        create_data = ClientCreate(
            full_name="Original Name",
            email="update@test.com",
            phone="+1234567890",
        )
        created = await service.create_client(create_data)

        update_data = ClientUpdate(
            full_name="Updated Name",
            phone="+9999999999",
        )
        updated = await service.update_client(created.id, update_data)

        assert updated.full_name == "Updated Name"
        assert updated.phone == "+9999999999"
        assert updated.email == "update@test.com"

    async def test_update_client_not_found(self, db_session: AsyncSession):
        service = ClientService(db_session)

        update_data = ClientUpdate(full_name="Does Not Exist")

        with pytest.raises(ClientNotFoundError):
            await service.update_client(99999, update_data)

    async def test_delete_client_success(self, db_session: AsyncSession):
        service = ClientService(db_session)

        create_data = ClientCreate(
            full_name="To Delete",
            email="delete@test.com",
            phone="+1234567890",
        )
        created = await service.create_client(create_data)

        await service.delete_client(created.id)

        with pytest.raises(ClientNotFoundError):
            await service.get_client(created.id)

    async def test_delete_client_not_found(self, db_session: AsyncSession):
        service = ClientService(db_session)

        with pytest.raises(ClientNotFoundError):
            await service.delete_client(99999)
