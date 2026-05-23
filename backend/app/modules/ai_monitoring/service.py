from uuid import UUID

from app.models.ai_monitoring import AIWorkflowRun
from app.modules.ai_monitoring.repository import AIMonitoringRepository
from app.modules.ai_monitoring.schemas import AIWorkflowRunCreate, AIWorkflowRunResponse
from app.schemas.common import PaginatedResponse, PaginationParams


class AIMonitoringService:
    def __init__(self, repository: AIMonitoringRepository) -> None:
        self._repo = repository

    async def list_runs(
        self, environment_id: UUID, pagination: PaginationParams
    ) -> PaginatedResponse[AIWorkflowRunResponse]:
        items, total = await self._repo.list_by_environment(
            environment_id, offset=pagination.offset, limit=pagination.page_size
        )
        return PaginatedResponse[AIWorkflowRunResponse](
            items=[AIWorkflowRunResponse.model_validate(i) for i in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def ingest_run(
        self, environment_id: UUID, data: AIWorkflowRunCreate
    ) -> AIWorkflowRunResponse:
        run = AIWorkflowRun(
            environment_id=environment_id,
            workflow_name=data.workflow_name,
            run_id=data.run_id,
            status=data.status,
            agent_steps=data.agent_steps,
            llm_latency_ms=data.llm_latency_ms,
            token_count=data.token_count,
            run_metadata=data.run_metadata,
        )
        created = await self._repo.create(run)
        return AIWorkflowRunResponse.model_validate(created)
