from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_dashboard_service, get_environment_id, require_active_user
from app.modules.dashboards.schemas import DashboardSummaryResponse
from app.modules.dashboards.service import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummaryResponse:
    return await service.get_summary(environment_id)
