from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.environment import OrchestratorEnvironment


class OrchestratorEnvironmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[OrchestratorEnvironment]:
        result = await self._session.execute(
            select(OrchestratorEnvironment).where(OrchestratorEnvironment.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def list_active(self) -> list[OrchestratorEnvironment]:
        result = await self._session.execute(
            select(OrchestratorEnvironment).where(
                OrchestratorEnvironment.is_active.is_(True),
                OrchestratorEnvironment.sync_enabled.is_(True),
            )
        )
        return list(result.scalars().all())

    async def get_by_id(self, environment_id: UUID) -> OrchestratorEnvironment | None:
        result = await self._session.execute(
            select(OrchestratorEnvironment).where(OrchestratorEnvironment.id == environment_id)
        )
        return result.scalar_one_or_none()

    async def create(self, env: OrchestratorEnvironment) -> OrchestratorEnvironment:
        self._session.add(env)
        await self._session.flush()
        await self._session.refresh(env)
        return env
