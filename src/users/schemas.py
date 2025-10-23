from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.users.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    full_name: str = Field(..., min_length=2, max_length=200, description="Full name")
    role: UserRole = Field(..., description="User role (admin or worker)")


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, description="User email address")
    password: str | None = Field(None, min_length=8, max_length=100, description="New password")
    full_name: str | None = Field(None, min_length=2, max_length=200, description="Full name")
    role: UserRole | None = Field(None, description="User role")
    is_active: bool | None = Field(None, description="User active status")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int
