from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.utils import hash_password
from src.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.users.models import User, UserRole
from src.users.repository import UserRepository
from src.users.schemas import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def create_user(self, data: UserCreate) -> UserResponse:
        existing_user = await self.repo.get_by_email(data.email)
        if existing_user:
            raise UserAlreadyExistsError(data.email)

        user = await self.repo.create(
            email=data.email,
            password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
            is_active=True,
        )

        return UserResponse.model_validate(user)

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        return UserResponse.model_validate(user)

    async def get_users(
        self,
        page: int = 1,
        per_page: int = 10,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[UserResponse], int, int]:
        skip = (page - 1) * per_page
        users, total = await self.repo.get_all(skip=skip, limit=per_page, role=role, is_active=is_active)

        user_responses = [UserResponse.model_validate(user) for user in users]
        total_pages = (total + per_page - 1) // per_page

        return user_responses, total, total_pages

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        if data.email and data.email != user.email:
            existing_user = await self.repo.get_by_email(data.email)
            if existing_user:
                raise UserAlreadyExistsError(data.email)

        update_data = data.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = hash_password(update_data["password"])

        updated_user = await self.repo.update(user, **update_data)
        return UserResponse.model_validate(updated_user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        await self.repo.delete(user)
