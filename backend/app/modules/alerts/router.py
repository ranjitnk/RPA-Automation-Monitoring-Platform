from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_alert_service, get_environment_id, require_active_user
from app.modules.alerts.schemas import (
    AlertAcknowledge,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
)
from app.modules.alerts.service import AlertService
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: AlertService = Depends(get_alert_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[AlertResponse]:
    return await service.list_open_alerts(
        environment_id, PaginationParams(page=page, page_size=page_size)
    )


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_rule(
    body: AlertRuleCreate,
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: AlertService = Depends(get_alert_service),
) -> AlertRuleResponse:
    return await service.create_rule(environment_id, body)


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_rules(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: AlertService = Depends(get_alert_service),
) -> list[AlertRuleResponse]:
    return await service.list_rules(environment_id)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: UUID,
    body: AlertAcknowledge,
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: AlertService = Depends(get_alert_service),
) -> AlertResponse:
    return await service.acknowledge_alert(alert_id, environment_id, body)
