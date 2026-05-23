from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.queue import Queue


class QueueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_environment(
        self, environment_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[Queue], int]:
        query = select(Queue).where(Queue.environment_id == environment_id)
        total = (
            await self._session.execute(
                select(func.count()).select_from(Queue).where(Queue.environment_id == environment_id)
            )
        ).scalar_one()
        result = await self._session.execute(
            query.order_by(Queue.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def total_backlog(self, environment_id: UUID) -> int:
        result = await self._session.execute(
            select(func.coalesce(func.sum(Queue.items_in_queue), 0)).where(
                Queue.environment_id == environment_id
            )
        )
        return int(result.scalar_one())
