from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_orchestrator_connector_service, require_active_user, require_superuser
from app.modules.orchestrator_connector.schemas import (
    ConnectionTestResponse,
    EnvironmentCreate,
    EnvironmentResponse,
    SyncTriggerResponse,
)
from app.modules.orchestrator_connector.service import OrchestratorConnectorService

router = APIRouter()


@router.get("/environments", response_model=list[EnvironmentResponse])
async def list_environments(
    _user=Depends(require_active_user),
    service: OrchestratorConnectorService = Depends(get_orchestrator_connector_service),
) -> list[EnvironmentResponse]:
    return await service.list_environments()


@router.post("/environments", response_model=EnvironmentResponse, status_code=201)
async def create_environment(
    body: EnvironmentCreate,
    _user=Depends(require_superuser),
    service: OrchestratorConnectorService = Depends(get_orchestrator_connector_service),
) -> EnvironmentResponse:
    return await service.create_environment(body)


@router.post("/environments/{environment_id}/test", response_model=ConnectionTestResponse)
async def test_connection(
    environment_id: UUID,
    _user=Depends(require_active_user),
    service: OrchestratorConnectorService = Depends(get_orchestrator_connector_service),
) -> ConnectionTestResponse:
    return await service.test_connection(environment_id)


@router.post("/environments/{environment_id}/sync", response_model=SyncTriggerResponse)
async def trigger_sync(
    environment_id: UUID,
    _user=Depends(require_superuser),
    service: OrchestratorConnectorService = Depends(get_orchestrator_connector_service),
) -> SyncTriggerResponse:
    return await service.sync_environment(environment_id)
