from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class Client(Base):

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Client(id={self.id}, full_name={self.full_name!r}, email={self.email!r})"
