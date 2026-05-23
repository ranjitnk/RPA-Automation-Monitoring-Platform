from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_environment_id, get_job_service, require_active_user
from app.modules.jobs.schemas import JobCreate, JobResponse
from app.modules.jobs.service import JobService
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter()


@router.get("", response_model=PaginatedResponse[JobResponse])
async def list_jobs(
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: JobService = Depends(get_job_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: str | None = None,
) -> PaginatedResponse[JobResponse]:
    return await service.list_jobs(
        environment_id,
        PaginationParams(page=page, page_size=page_size),
        state=state,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    return await service.get_job(job_id, environment_id)


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    body: JobCreate,
    _user=Depends(require_active_user),
    environment_id: UUID = Depends(get_environment_id),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    return await service.create_job(environment_id, body)
