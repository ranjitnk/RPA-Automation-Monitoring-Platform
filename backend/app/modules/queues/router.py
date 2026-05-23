from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_environment_id, get_queue_service, require_active_user
from app.modules.queues.schemas import QueueResponse
from app.modules.queues.service import QueueService
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[QueueResponse])
async def list_queues(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: QueueService = Depends(get_queue_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[QueueResponse]:
    return await service.list_queues(
        environment_id, PaginationParams(page=page, page_size=page_size)
    )
