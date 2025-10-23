from sqlalchemy.ext.asyncio import AsyncSession

from src.clients.repository import ClientRepository
from src.clients.schemas import ClientCreate
from src.tickets.exceptions import TicketAccessDeniedError, TicketNotFoundError, WorkerNotFoundError
from src.tickets.models import Ticket, TicketStatus
from src.tickets.permissions import can_view_ticket
from src.tickets.repository import TicketRepository
from src.tickets.schemas import (
    ClientInfo,
    TicketCreate,
    TicketCreatePublic,
    TicketFilters,
    TicketListItem,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
    WorkerInfo,
)
from src.users.models import User, UserRole
from src.users.repository import UserRepository


class TicketService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = TicketRepository(db)
        self.client_repo = ClientRepository(db)
        self.user_repo = UserRepository(db)

    async def create_ticket_public(self, data: TicketCreatePublic) -> TicketResponse:
        client = await self.client_repo.get_by_email(data.client_email)

        if not client:
            client_data = ClientCreate(
                full_name=data.client_full_name,
                email=data.client_email,
                phone=data.client_phone,
                address=data.client_address,
            )
            client = await self.client_repo.create(**client_data.model_dump())

        ticket = await self.repo.create(
            title=data.title,
            description=data.description,
            client_id=client.id,
            status=TicketStatus.NEW,
        )

        return self._to_response(ticket)

    async def create_ticket(self, data: TicketCreate) -> TicketResponse:
        client = await self.client_repo.get_by_id(data.client_id)
        if not client:
            raise ValueError(f"Client with ID {data.client_id} not found")

        if data.assigned_worker_id:
            worker = await self.user_repo.get_by_id(data.assigned_worker_id)
            if not worker or worker.role != UserRole.WORKER:
                raise WorkerNotFoundError(data.assigned_worker_id)

        ticket = await self.repo.create(**data.model_dump())
        return self._to_response(ticket)

    async def get_ticket(self, ticket_id: int, current_user: User) -> TicketResponse:
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        if not can_view_ticket(current_user, ticket):
            raise TicketAccessDeniedError()

        return self._to_response(ticket)

    async def get_tickets(
        self,
        current_user: User,
        page: int = 1,
        per_page: int = 10,
        filters: TicketFilters | None = None,
    ) -> tuple[list[TicketListItem], int, int]:
        skip = (page - 1) * per_page

        tickets, total = await self.repo.get_all(
            skip=skip,
            limit=per_page,
            status=filters.status if filters else None,
            title_search=filters.title if filters else None,
            assigned_worker_id=filters.assigned_worker_id if filters else None,
            user=current_user,
        )

        ticket_items = [self._to_list_item(ticket) for ticket in tickets]
        total_pages = (total + per_page - 1) // per_page

        return ticket_items, total, total_pages

    async def update_ticket(self, ticket_id: int, data: TicketUpdate, current_user: User) -> TicketResponse:
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        if data.assigned_worker_id is not None:
            worker = await self.user_repo.get_by_id(data.assigned_worker_id)
            if not worker or worker.role != UserRole.WORKER:
                raise WorkerNotFoundError(data.assigned_worker_id)

        update_data = data.model_dump(exclude_unset=True)
        updated_ticket = await self.repo.update(ticket, **update_data)

        return self._to_response(updated_ticket)

    async def update_ticket_status(
        self, ticket_id: int, data: TicketStatusUpdate, current_user: User
    ) -> TicketResponse:
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        if not can_view_ticket(current_user, ticket):
            raise TicketAccessDeniedError()

        updated_ticket = await self.repo.update(ticket, status=data.status)
        return self._to_response(updated_ticket)

    async def assign_ticket(self, ticket_id: int, worker_id: int) -> TicketResponse:
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        worker = await self.user_repo.get_by_id(worker_id)
        if not worker or worker.role != UserRole.WORKER:
            raise WorkerNotFoundError(worker_id)

        updated_ticket = await self.repo.update(ticket, assigned_worker_id=worker_id)
        return self._to_response(updated_ticket)

    async def delete_ticket(self, ticket_id: int) -> None:
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise TicketNotFoundError(ticket_id)

        await self.repo.delete(ticket)

    def _to_response(self, ticket: Ticket) -> TicketResponse:
        return TicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            client=ClientInfo.model_validate(ticket.client),
            assigned_worker=WorkerInfo.model_validate(ticket.assigned_worker) if ticket.assigned_worker else None,
        )

    def _to_list_item(self, ticket: Ticket) -> TicketListItem:
        return TicketListItem(
            id=ticket.id,
            title=ticket.title,
            status=ticket.status,
            created_at=ticket.created_at,
            client_full_name=ticket.client.full_name,
            assigned_worker_full_name=ticket.assigned_worker.full_name if ticket.assigned_worker else None,
        )
