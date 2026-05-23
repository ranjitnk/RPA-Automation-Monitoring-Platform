from uuid import UUID

from app.core.cache import cache
from app.modules.alerts.repository import AlertRepository
from app.modules.dashboards.schemas import DashboardSummaryResponse
from app.modules.jobs.repository import JobRepository
from app.modules.queues.repository import QueueRepository
from app.modules.robots.repository import RobotRepository


class DashboardService:
    def __init__(
        self,
        job_repo: JobRepository,
        queue_repo: QueueRepository,
        robot_repo: RobotRepository,
        alert_repo: AlertRepository,
    ) -> None:
        self._jobs = job_repo
        self._queues = queue_repo
        self._robots = robot_repo
        self._alerts = alert_repo

    async def get_summary(self, environment_id: UUID) -> DashboardSummaryResponse:
        cache_key = f"dashboard:summary:{environment_id}"
        cached = await cache.get(cache_key)
        if cached:
            return DashboardSummaryResponse(**cached)

        jobs_running = await self._jobs.count_by_state(environment_id, "Running")
        jobs_failed = await self._jobs.count_by_state(environment_id, "Faulted")
        backlog = await self._queues.total_backlog(environment_id)
        robots_online = await self._robots.count_online(environment_id)
        _, robots_total = await self._robots.list_by_environment(environment_id, offset=0, limit=1)
        open_alerts = await self._alerts.count_open(environment_id)

        summary = DashboardSummaryResponse(
            environment_id=str(environment_id),
            jobs_running=jobs_running,
            jobs_failed=jobs_failed,
            queue_backlog=backlog,
            robots_online=robots_online,
            robots_total=robots_total,
            open_alerts=open_alerts,
            ai_runs_active=0,
        )
        await cache.set(cache_key, summary.model_dump(), ttl=60)
        return summary
