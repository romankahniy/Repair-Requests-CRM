from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUser
from src.auth.schemas import TokenResponse
from src.auth.service import AuthService
from src.core.dependencies import get_db
from src.users.schemas import UserResponse

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user and receive JWT access token",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    service = AuthService(db)
    return await service.login(email=form_data.username, password=form_data.password)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
