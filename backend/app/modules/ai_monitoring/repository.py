from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_monitoring import AIWorkflowRun


class AIMonitoringRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_environment(
        self, environment_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[AIWorkflowRun], int]:
        query = select(AIWorkflowRun).where(AIWorkflowRun.environment_id == environment_id)
        total = (
            await self._session.execute(
                select(func.count())
                .select_from(AIWorkflowRun)
                .where(AIWorkflowRun.environment_id == environment_id)
            )
        ).scalar_one()
        result = await self._session.execute(
            query.order_by(AIWorkflowRun.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def create(self, run: AIWorkflowRun) -> AIWorkflowRun:
        self._session.add(run)
        await self._session.flush()
        await self._session.refresh(run)
        return run
