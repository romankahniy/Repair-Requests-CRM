from src.core.exceptions import AppException


class TicketException(AppException):
    pass


class TicketNotFoundError(TicketException):
    def __init__(self, ticket_id: int) -> None:
        super().__init__(message=f"Ticket with ID {ticket_id} not found", status_code=404)


class TicketAccessDeniedError(TicketException):
    def __init__(self) -> None:
        super().__init__(message="You don't have access to this ticket", status_code=403)


class InvalidStatusTransitionError(TicketException):
    def __init__(self, from_status: str, to_status: str) -> None:
        super().__init__(
            message=f"Cannot transition from {from_status} to {to_status}",
            status_code=400,
        )


class WorkerNotFoundError(TicketException):
    def __init__(self, worker_id: int) -> None:
        super().__init__(message=f"Worker with ID {worker_id} not found", status_code=404)
