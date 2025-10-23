from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.exceptions import ClientNotFoundError
from src.clients.repository import ClientRepository
from src.clients.schemas import ClientCreate, ClientResponse, ClientUpdate


class ClientService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ClientRepository(db)

    async def create_client(self, data: ClientCreate) -> ClientResponse:
        client = await self.repo.create(**data.model_dump())
        return ClientResponse.model_validate(client)

    async def get_client(self, client_id: int) -> ClientResponse:
        client = await self.repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)

        return ClientResponse.model_validate(client)

    async def get_clients(self, page: int = 1, per_page: int = 10) -> tuple[list[ClientResponse], int, int]:
        skip = (page - 1) * per_page
        clients, total = await self.repo.get_all(skip=skip, limit=per_page)

        client_responses = [ClientResponse.model_validate(client) for client in clients]
        total_pages = (total + per_page - 1) // per_page

        return client_responses, total, total_pages

    async def update_client(self, client_id: int, data: ClientUpdate) -> ClientResponse:
        client = await self.repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)

        update_data = data.model_dump(exclude_unset=True)
        updated_client = await self.repo.update(client, **update_data)

        return ClientResponse.model_validate(updated_client)

    async def delete_client(self, client_id: int) -> None:
        client = await self.repo.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id)

        await self.repo.delete(client)
