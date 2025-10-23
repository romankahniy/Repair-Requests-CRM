from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pydantic import BaseModel, Field

from src.core.config import settings


class TokenPayload(BaseModel):
    sub: str = Field(..., description="Subject (user email)")
    user_id: int = Field(..., description="User ID")
    role: str = Field(..., description="User role")
    exp: datetime = Field(..., description="Expiration timestamp")


def create_access_token(subject: str, user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS)

    payload = TokenPayload(sub=subject, user_id=user_id, role=role, exp=expire)

    encoded_jwt = jwt.encode(
        payload.model_dump(mode="json"),
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise JWTError("Could not validate credentials") from e
