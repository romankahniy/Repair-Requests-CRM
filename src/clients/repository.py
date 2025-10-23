from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.models import Client


class ClientRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> Client:
        client = Client(**kwargs)
        self.db.add(client)
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def get_by_id(self, client_id: int) -> Client | None:
        return await self.db.get(Client, client_id)

    async def get_by_email(self, email: str) -> Client | None:
        result = await self.db.scalar(select(Client).where(Client.email == email))
        return result

    async def get_all(self, skip: int = 0, limit: int = 10) -> tuple[list[Client], int]:
        query = select(Client)

        count_query = select(func.count()).select_from(Client)
        total = await self.db.scalar(count_query) or 0

        query = query.order_by(Client.id).offset(skip).limit(limit)
        result = await self.db.scalars(query)
        clients = list(result)

        return clients, total

    async def update(self, client: Client, **kwargs) -> Client:
        for key, value in kwargs.items():
            if value is not None:
                setattr(client, key, value)

        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def delete(self, client: Client) -> None:
        await self.db.delete(client)
        await self.db.commit()
