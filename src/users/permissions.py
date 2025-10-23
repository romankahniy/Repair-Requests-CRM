from src.users.models import User, UserRole


def is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


def can_manage_users(user: User) -> bool:
    return is_admin(user)
