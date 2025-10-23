from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.tickets.models import Ticket, TicketStatus
from src.users.models import User, UserRole


class TicketRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> Ticket:
        ticket = Ticket(**kwargs)
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket, ["client", "assigned_worker"])
        return ticket

    async def get_by_id(self, ticket_id: int) -> Ticket | None:
        result = await self.db.scalar(
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(joinedload(Ticket.client), joinedload(Ticket.assigned_worker))
        )
        return result

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        status: TicketStatus | None = None,
        title_search: str | None = None,
        assigned_worker_id: int | None = None,
        user: User | None = None,
    ) -> tuple[list[Ticket], int]:
        query = select(Ticket).options(joinedload(Ticket.client), joinedload(Ticket.assigned_worker))

        conditions = []

        if status:
            conditions.append(Ticket.status == status)

        if title_search:
            conditions.append(Ticket.title.ilike(f"%{title_search}%"))

        if assigned_worker_id is not None:
            conditions.append(Ticket.assigned_worker_id == assigned_worker_id)

        if user and user.role == UserRole.WORKER:
            conditions.append(Ticket.assigned_worker_id == user.id)

        if conditions:
            query = query.where(and_(*conditions))

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.scalars(query)
        tickets = list(result)

        return tickets, total

    async def update(self, ticket: Ticket, **kwargs) -> Ticket:
        for key, value in kwargs.items():
            if value is not None:
                setattr(ticket, key, value)

        await self.db.commit()
        await self.db.refresh(ticket, ["client", "assigned_worker"])
        return ticket

    async def delete(self, ticket: Ticket) -> None:
        await self.db.delete(ticket)
        await self.db.commit()
