from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_environment_id, get_robot_service, require_active_user
from app.modules.robots.schemas import RobotResponse
from app.modules.robots.service import RobotService
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[RobotResponse])
async def list_robots(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: RobotService = Depends(get_robot_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[RobotResponse]:
    return await service.list_robots(
        environment_id, PaginationParams(page=page, page_size=page_size)
    )
