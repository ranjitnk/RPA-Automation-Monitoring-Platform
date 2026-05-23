from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_environment(
        self,
        environment_id: UUID,
        *,
        offset: int,
        limit: int,
        state: str | None = None,
    ) -> tuple[list[Job], int]:
        query = select(Job).where(Job.environment_id == environment_id)
        count_query = select(func.count()).select_from(Job).where(Job.environment_id == environment_id)
        if state:
            query = query.where(Job.state == state)
            count_query = count_query.where(Job.state == state)

        total = (await self._session.execute(count_query)).scalar_one()
        result = await self._session.execute(
            query.order_by(Job.last_synced_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, job_id: UUID, environment_id: UUID) -> Job | None:
        result = await self._session.execute(
            select(Job).where(Job.id == job_id, Job.environment_id == environment_id)
        )
        return result.scalar_one_or_none()

    async def create(self, job: Job) -> Job:
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def count_by_state(self, environment_id: UUID, state: str) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Job)
            .where(Job.environment_id == environment_id, Job.state == state)
        )
        return result.scalar_one()
