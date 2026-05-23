from uuid import UUID

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.environment import OrchestratorEnvironment
from app.modules.orchestrator_connector.client import OrchestratorHttpClient
from app.modules.orchestrator_connector.repository import OrchestratorEnvironmentRepository
from app.modules.orchestrator_connector.schemas import (
    ConnectionTestResponse,
    EnvironmentCreate,
    EnvironmentResponse,
    SyncTriggerResponse,
)

logger = get_logger(__name__)


class OrchestratorConnectorService:
    def __init__(self, repository: OrchestratorEnvironmentRepository) -> None:
        self._repo = repository

    async def list_environments(self) -> list[EnvironmentResponse]:
        envs = await self._repo.list_all()
        return [EnvironmentResponse.model_validate(e) for e in envs]

    async def create_environment(self, data: EnvironmentCreate) -> EnvironmentResponse:
        # Production: encrypt credentials with Fernet/KMS
        encrypted = f"{data.client_id}:{data.client_secret}"
        env = OrchestratorEnvironment(
            name=data.name,
            base_url=str(data.base_url),
            tenant_name=data.tenant_name,
            credentials_encrypted=encrypted,
        )
        created = await self._repo.create(env)
        return EnvironmentResponse.model_validate(created)

    async def _get_client(self, environment_id: UUID) -> OrchestratorHttpClient:
        env = await self._repo.get_by_id(environment_id)
        if not env:
            raise NotFoundError("Environment not found")
        # TODO: decrypt credentials + OAuth token refresh
        token = "placeholder-token"
        return OrchestratorHttpClient(env.base_url, token)

    async def test_connection(self, environment_id: UUID) -> ConnectionTestResponse:
        try:
            client = await self._get_client(environment_id)
            latency = await client.ping()
            return ConnectionTestResponse(
                environment_id=environment_id,
                success=True,
                message="Connection successful",
                latency_ms=latency,
            )
        except Exception as exc:
            logger.warning("connection_test_failed", environment_id=str(environment_id), error=str(exc))
            return ConnectionTestResponse(
                environment_id=environment_id,
                success=False,
                message=str(exc),
            )

    async def sync_environment(self, environment_id: UUID) -> SyncTriggerResponse:
        client = await self._get_client(environment_id)
        jobs = await client.fetch_jobs()
        queues = await client.fetch_queues()
        robots = await client.fetch_robots()
        # TODO: upsert into Job/Queue/Robot repositories
        logger.info(
            "orchestrator_sync_completed",
            environment_id=str(environment_id),
            jobs=len(jobs),
            queues=len(queues),
            robots=len(robots),
        )
        return SyncTriggerResponse(
            environment_id=environment_id,
            status="completed",
            synced={"jobs": len(jobs), "queues": len(queues), "robots": len(robots)},
        )
