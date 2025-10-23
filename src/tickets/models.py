from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.clients.models import Client
    from src.users.models import User


class TicketStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(String(20), nullable=False, default=TicketStatus.NEW, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_worker_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    client: Mapped[Client] = relationship("Client", back_populates="tickets")
    assigned_worker: Mapped[User | None] = relationship("User", back_populates="assigned_tickets")

    def __repr__(self) -> str:
        return f"Ticket(id={self.id}, title={self.title!r}, status={self.status})"
