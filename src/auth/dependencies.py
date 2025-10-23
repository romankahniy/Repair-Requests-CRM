from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import PermissionDeniedError
from src.core.dependencies import get_db
from src.core.security import decode_token
from src.users.exceptions import UserInactiveError, UserNotFoundError
from src.users.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(token)

        user = await db.get(User, payload.user_id)
        if not user:
            raise UserNotFoundError(payload.user_id)

        if not user.is_active:
            raise UserInactiveError()

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedError("Admin access required")

    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin_user)]
