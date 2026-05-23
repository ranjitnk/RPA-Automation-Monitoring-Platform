from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_environment_id, get_log_service, require_active_user
from app.modules.logs.schemas import LogEntryResponse, LogSearchRequest
from app.modules.logs.service import LogService

router = APIRouter()


@router.get("/search", response_model=list[LogEntryResponse])
async def search_logs(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: LogService = Depends(get_log_service),
    query: str = Query("*"),
    level: str | None = None,
    from_minutes_ago: int = Query(60, ge=1, le=10080),
    size: int = Query(50, ge=1, le=200),
) -> list[LogEntryResponse]:
    req = LogSearchRequest(query=query, level=level, from_minutes_ago=from_minutes_ago)
    return await service.search_logs(req, environment_id=str(environment_id), size=size)
