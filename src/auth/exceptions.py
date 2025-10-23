from src.core.exceptions import AppException


class AuthException(AppException):
    pass


class InvalidCredentialsError(AuthException):
    def __init__(self) -> None:
        super().__init__(message="Invalid email or password", status_code=401)


class InvalidTokenError(AuthException):
    def __init__(self) -> None:
        super().__init__(message="Could not validate credentials", status_code=401)


class PermissionDeniedError(AuthException):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message=message, status_code=403)
