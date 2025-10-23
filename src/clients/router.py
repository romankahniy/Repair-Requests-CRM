from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentAdmin, CurrentUser
from src.clients.schemas import ClientCreate, ClientListResponse, ClientResponse, ClientUpdate
from src.clients.service import ClientService
from src.core.dependencies import get_db

router = APIRouter()


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new client",
    description="Create a new client. Requires authentication.",
)
async def create_client(
    data: ClientCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ClientResponse:
    service = ClientService(db)
    return await service.create_client(data)


@router.get(
    "",
    response_model=ClientListResponse,
    summary="List all clients",
    description="Get list of all clients with pagination. Requires authentication.",
)
async def list_clients(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 10,
) -> ClientListResponse:
    service = ClientService(db)
    clients, total, total_pages = await service.get_clients(page=page, per_page=per_page)

    return ClientListResponse(
        clients=clients,
        total_count=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get client by ID",
    description="Get client details by ID. Requires authentication.",
)
async def get_client(
    client_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ClientResponse:
    service = ClientService(db)
    return await service.get_client(client_id)


@router.patch(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update client",
    description="Update client information. Only admin can access.",
)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    current_admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ClientResponse:
    service = ClientService(db)
    return await service.update_client(client_id, data)


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete client",
    description="Delete a client. Only admin can access.",
)
async def delete_client(
    client_id: int,
    current_admin: CurrentAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = ClientService(db)
    await service.delete_client(client_id)
