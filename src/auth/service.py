from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import InvalidCredentialsError
from src.auth.schemas import TokenResponse
from src.auth.utils import verify_password
from src.core.security import create_access_token
from src.users.exceptions import UserInactiveError
from src.users.models import User


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.db.scalar(select(User).where(User.email == email))

        if not user or not verify_password(password, user.password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError()

        access_token = create_access_token(subject=user.email, user_id=user.id, role=user.role)

        return TokenResponse(access_token=access_token)
