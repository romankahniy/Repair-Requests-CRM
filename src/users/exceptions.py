from src.core.exceptions import AppException


class UserException(AppException):
    pass


class UserNotFoundError(UserException):
    def __init__(self, user_id: int | None = None) -> None:
        message = f"User with ID {user_id} not found" if user_id else "User not found"
        super().__init__(message=message, status_code=404)


class UserAlreadyExistsError(UserException):
    def __init__(self, email: str) -> None:
        super().__init__(message=f"User with email '{email}' already exists", status_code=409)


class UserInactiveError(UserException):
    def __init__(self) -> None:
        super().__init__(message="User account is inactive", status_code=403)
