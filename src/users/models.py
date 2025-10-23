from enum import StrEnum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class UserRole(StrEnum):
    ADMIN = "admin"
    WORKER = "worker"


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="assigned_worker", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r}, role={self.role})"
