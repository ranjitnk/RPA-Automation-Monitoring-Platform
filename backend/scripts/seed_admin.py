"""Create initial superuser. Usage: python -m scripts.seed_admin"""

import asyncio

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.modules.auth.repository import AuthRepository


async def main() -> None:
    email = "admin@example.com"
    password = "ChangeMe123!"
    async with AsyncSessionLocal() as session:
        repo = AuthRepository(session)
        if await repo.get_user_by_email(email):
            print(f"User {email} already exists")
            return
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name="System Admin",
            is_superuser=True,
        )
        await repo.create_user(user)
        await session.commit()
        print(f"Created superuser: {email}")


if __name__ == "__main__":
    asyncio.run(main())
