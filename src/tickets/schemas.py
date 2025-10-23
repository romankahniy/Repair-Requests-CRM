from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.tickets.models import TicketStatus


class TicketCreatePublic(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Ticket title")
    description: str = Field(..., min_length=10, description="Detailed description of the repair request")
    client_full_name: str = Field(..., min_length=2, max_length=200, description="Client full name")
    client_email: EmailStr = Field(..., description="Client email address")
    client_phone: str = Field(..., min_length=5, max_length=20, description="Client phone number")
    client_address: str | None = Field(None, max_length=500, description="Client address")


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Ticket title")
    description: str = Field(..., min_length=10, description="Detailed description")
    client_id: int = Field(..., description="Client ID")
    assigned_worker_id: int | None = Field(None, description="Assigned worker ID")


class TicketUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200, description="Ticket title")
    description: str | None = Field(None, min_length=10, description="Ticket description")
    status: TicketStatus | None = Field(None, description="Ticket status")
    assigned_worker_id: int | None = Field(None, description="Assigned worker ID")


class TicketAssign(BaseModel):
    worker_id: int = Field(..., description="Worker ID to assign ticket to")


class TicketStatusUpdate(BaseModel):
    status: TicketStatus = Field(..., description="New ticket status")


class ClientInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str


class WorkerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    client: ClientInfo
    assigned_worker: WorkerInfo | None


class TicketListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TicketStatus
    created_at: datetime
    client_full_name: str
    assigned_worker_full_name: str | None


class TicketListResponse(BaseModel):
    tickets: list[TicketListItem]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class TicketFilters(BaseModel):
    status: TicketStatus | None = Field(None, description="Filter by status")
    title: str | None = Field(None, min_length=2, description="Search by title (partial match)")
    assigned_worker_id: int | None = Field(None, description="Filter by assigned worker")
