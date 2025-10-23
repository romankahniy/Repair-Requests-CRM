from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_admin_user
from src.core.dependencies import get_db
from src.users.models import User, UserRole
from src.users.schemas import UserCreate, UserListResponse, UserResponse, UserUpdate
from src.users.service import UserService

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user (admin or worker). Only admin can access.",
)
async def create_user(
    data: UserCreate,
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    service = UserService(db)
    return await service.create_user(data)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List all users",
    description="Get list of all users with pagination. Only admin can access.",
)
async def list_users(
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 10,
    role: UserRole | None = None,
    is_active: bool | None = None,
) -> UserListResponse:
    service = UserService(db)
    users, total, total_pages = await service.get_users(
        page=page,
        per_page=per_page,
        role=role,
        is_active=is_active,
    )

    return UserListResponse(
        users=users,
        total_count=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get user details by ID. Only admin can access.",
)
async def get_user(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    service = UserService(db)
    return await service.get_user(user_id)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user information. Only admin can access.",
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    service = UserService(db)
    return await service.update_user(user_id, data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user. Only admin can access.",
)
async def delete_user(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = UserService(db)
    await service.delete_user(user_id)
