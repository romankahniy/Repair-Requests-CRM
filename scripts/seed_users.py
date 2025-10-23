import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from src.auth.utils import hash_password
from src.core.config import settings
from src.database.session import async_session, engine

from src.users.models import User, UserRole
from src.clients.models import Client  # noqa: F401
from src.tickets.models import Ticket  # noqa: F401


async def seed_users():
    print("🌱 Seeding users...")

    async with async_session() as session:
        existing_admin = await session.scalar(
            select(User).where(User.email == "admin@example.com")
        )

        if existing_admin:
            print("⚠️  Admin user already exists")
        else:
            admin = User(
                email="admin@example.com",
                password=hash_password("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin)
            print("✅ Created admin user: admin@example.com / admin123")

        existing_worker = await session.scalar(
            select(User).where(User.email == "worker@example.com")
        )

        if existing_worker:
            print("⚠️  Worker user already exists")
        else:
            worker = User(
                email="worker@example.com",
                password=hash_password("worker123"),
                full_name="Worker User",
                role=UserRole.WORKER,
                is_active=True,
            )
            session.add(worker)
            print("✅ Created worker user: worker@example.com / worker123")

        await session.commit()

    print("\n📋 Test Accounts:")
    print("=" * 50)
    print("Admin:  admin@example.com  / admin123")
    print("Worker: worker@example.com / worker123")
    print("=" * 50)
    print("\n⚠️  Remember to change these passwords in production!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_users())
