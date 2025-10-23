from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200, description="Client full name")
    email: EmailStr = Field(..., description="Client email address")
    phone: str = Field(..., min_length=5, max_length=20, description="Client phone number")
    address: str | None = Field(None, max_length=500, description="Client address")


class ClientUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=200, description="Client full name")
    email: EmailStr | None = Field(None, description="Client email address")
    phone: str | None = Field(None, min_length=5, max_length=20, description="Client phone number")
    address: str | None = Field(None, max_length=500, description="Client address")


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str
    address: str | None


class ClientListResponse(BaseModel):
    clients: list[ClientResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int
