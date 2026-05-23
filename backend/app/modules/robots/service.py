from uuid import UUID

from app.modules.robots.repository import RobotRepository
from app.modules.robots.schemas import RobotResponse
from app.schemas.common import PaginatedResponse, PaginationParams


class RobotService:
    def __init__(self, repository: RobotRepository) -> None:
        self._repo = repository

    async def list_robots(
        self, environment_id: UUID, pagination: PaginationParams
    ) -> PaginatedResponse[RobotResponse]:
        items, total = await self._repo.list_by_environment(
            environment_id, offset=pagination.offset, limit=pagination.page_size
        )
        return PaginatedResponse[RobotResponse](
            items=[RobotResponse.model_validate(i) for i in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )
