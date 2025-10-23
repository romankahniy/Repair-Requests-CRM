from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentAdmin, CurrentUser
from src.core.dependencies import get_db
from src.tickets.schemas import (
    TicketAssign,
    TicketCreatePublic,
    TicketFilters,
    TicketListResponse,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
)
from src.tickets.service import TicketService

router = APIRouter()


@router.post(
    "/public",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create repair request (Public)",
    description="Submit a repair request. No authentication required.",
)
async def create_ticket_public(
    data: TicketCreatePublic,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketResponse:
    service = TicketService(db)
    return await service.create_ticket_public(data)


@router.get(
    "",
    response_model=TicketListResponse,
    summary="List all tickets",
    description="Get list of tickets. Admin sees all, worker sees only assigned tickets.",
)
async def list_tickets(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 10,
    status: str | None = None,
    title: str | None = None,
    assigned_worker_id: int | None = None,
) -> TicketListResponse:
    service = TicketService(db)

    filters = TicketFilters(
        status=status,
        title=title,
        assigned_worker_id=assigned_worker_id,
    )

    tickets, total, total_pages = await service.get_tickets(
        current_user=current_user,
        page=page,
        per_page=per_page,
        filters=filters,
    )

    return TicketListResponse(
        tickets=tickets,
        total_count=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Get ticket by ID",
    description="Get ticket details. Admin sees all, worker sees only their tickets.",
)
async def get_ticket(
    ticket_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketResponse:
    service = TicketService(db)
    return await service.get_ticket(ticket_id, current_user)


@router.patch(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Update ticket",
    description="Update ticket information. Only admin can access.",
)
async def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    current_admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketResponse:
    service = TicketService(db)
    return await service.update_ticket(ticket_id, data, current_admin)


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    summary="Update ticket status",
    description="Update ticket status. Worker can update their assigned tickets.",
)
async def update_ticket_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketResponse:
    service = TicketService(db)
    return await service.update_ticket_status(ticket_id, data, current_user)


@router.post(
    "/{ticket_id}/assign",
    response_model=TicketResponse,
    summary="Assign ticket to worker",
    description="Assign ticket to a worker. Only admin can access.",
)
async def assign_ticket(
    ticket_id: int,
    data: TicketAssign,
    current_admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketResponse:
    service = TicketService(db)
    return await service.assign_ticket(ticket_id, data.worker_id)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete ticket",
    description="Delete a ticket. Only admin can access.",
)
async def delete_ticket(
    ticket_id: int,
    current_admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = TicketService(db)
    await service.delete_ticket(ticket_id)
