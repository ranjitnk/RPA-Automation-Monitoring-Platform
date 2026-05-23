from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.robot import Robot


class RobotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_environment(
        self, environment_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[Robot], int]:
        query = select(Robot).where(Robot.environment_id == environment_id)
        total = (
            await self._session.execute(
                select(func.count()).select_from(Robot).where(Robot.environment_id == environment_id)
            )
        ).scalar_one()
        result = await self._session.execute(
            query.order_by(Robot.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def count_online(self, environment_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Robot)
            .where(Robot.environment_id == environment_id, Robot.is_online.is_(True))
        )
        return result.scalar_one()
