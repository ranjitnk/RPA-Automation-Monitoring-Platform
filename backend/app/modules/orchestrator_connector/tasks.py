"""Scheduler tasks for Orchestrator synchronization."""

from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.modules.orchestrator_connector.repository import OrchestratorEnvironmentRepository
from app.modules.orchestrator_connector.service import OrchestratorConnectorService

logger = get_logger(__name__)


async def run_sync_all_environments() -> None:
    logger.info("sync_all_environments_started")
    async with AsyncSessionLocal() as session:
        repo = OrchestratorEnvironmentRepository(session)
        service = OrchestratorConnectorService(repo)
        environments = await repo.list_active()
        for env in environments:
            try:
                await service.sync_environment(env.id)
                await session.commit()
            except Exception as exc:
                await session.rollback()
                logger.error("sync_environment_failed", environment_id=str(env.id), error=str(exc))
    logger.info("sync_all_environments_completed")
