from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_ai_monitoring_service, get_environment_id, require_active_user
from app.modules.ai_monitoring.schemas import AIWorkflowRunCreate, AIWorkflowRunResponse
from app.modules.ai_monitoring.service import AIMonitoringService
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("/runs", response_model=PaginatedResponse[AIWorkflowRunResponse])
async def list_runs(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: AIMonitoringService = Depends(get_ai_monitoring_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[AIWorkflowRunResponse]:
    return await service.list_runs(
        environment_id, PaginationParams(page=page, page_size=page_size)
    )


@router.post("/runs", response_model=AIWorkflowRunResponse, status_code=201)
async def ingest_run(
    body: AIWorkflowRunCreate,
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: AIMonitoringService = Depends(get_ai_monitoring_service),
) -> AIWorkflowRunResponse:
    return await service.ingest_run(environment_id, body)
