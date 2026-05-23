from datetime import UTC, datetime
from uuid import UUID

from app.core.cache import cache
from app.core.exceptions import NotFoundError
from app.models.job import Job
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.schemas import JobCreate, JobResponse
from app.schemas.common import PaginatedResponse, PaginationParams


class JobService:
    def __init__(self, repository: JobRepository) -> None:
        self._repo = repository

    async def list_jobs(
        self,
        environment_id: UUID,
        pagination: PaginationParams,
        state: str | None = None,
    ) -> PaginatedResponse[JobResponse]:
        cache_key = f"jobs:{environment_id}:{pagination.page}:{pagination.page_size}:{state}"
        cached = await cache.get(cache_key)
        if cached:
            return PaginatedResponse[JobResponse](**cached)

        items, total = await self._repo.list_by_environment(
            environment_id,
            offset=pagination.offset,
            limit=pagination.page_size,
            state=state,
        )
        response = PaginatedResponse[JobResponse](
            items=[JobResponse.model_validate(i) for i in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )
        await cache.set(cache_key, response.model_dump(mode="json"))
        return response

    async def get_job(self, job_id: UUID, environment_id: UUID) -> JobResponse:
        job = await self._repo.get_by_id(job_id, environment_id)
        if not job:
            raise NotFoundError("Job not found")
        return JobResponse.model_validate(job)

    async def create_job(self, environment_id: UUID, data: JobCreate) -> JobResponse:
        job = Job(
            environment_id=environment_id,
            orchestrator_job_id=data.orchestrator_job_id,
            state=data.state,
            process_name=data.process_name,
            robot_name=data.robot_name,
            last_synced_at=datetime.now(UTC),
        )
        created = await self._repo.create(job)
        await cache.delete_pattern(f"jobs:{environment_id}:*")
        return JobResponse.model_validate(created)
