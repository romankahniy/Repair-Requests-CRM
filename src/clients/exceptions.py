from src.core.exceptions import AppException


class ClientException(AppException):
    pass


class ClientNotFoundError(ClientException):
    def __init__(self, client_id: int) -> None:
        super().__init__(message=f"Client with ID {client_id} not found", status_code=404)
