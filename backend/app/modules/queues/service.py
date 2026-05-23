from uuid import UUID

from app.modules.queues.repository import QueueRepository
from app.modules.queues.schemas import QueueResponse
from app.schemas.common import PaginatedResponse, PaginationParams


class QueueService:
    def __init__(self, repository: QueueRepository) -> None:
        self._repo = repository

    async def list_queues(
        self, environment_id: UUID, pagination: PaginationParams
    ) -> PaginatedResponse[QueueResponse]:
        items, total = await self._repo.list_by_environment(
            environment_id, offset=pagination.offset, limit=pagination.page_size
        )
        return PaginatedResponse[QueueResponse](
            items=[QueueResponse.model_validate(i) for i in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )
