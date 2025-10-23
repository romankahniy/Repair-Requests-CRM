from src.tickets.models import Ticket
from src.users.models import User, UserRole


def can_view_ticket(user: User, ticket: Ticket) -> bool:
    if user.role == UserRole.ADMIN:
        return True

    if user.role == UserRole.WORKER:
        return ticket.assigned_worker_id == user.id

    return False


def can_modify_ticket(user: User, ticket: Ticket) -> bool:
    if user.role == UserRole.ADMIN:
        return True

    if user.role == UserRole.WORKER:
        return ticket.assigned_worker_id == user.id

    return False


def can_assign_ticket(user: User) -> bool:
    return user.role == UserRole.ADMIN


def can_view_all_tickets(user: User) -> bool:
    return user.role == UserRole.ADMIN
