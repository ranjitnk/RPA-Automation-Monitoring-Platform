from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    environment_id: str
    jobs_running: int
    jobs_failed: int
    queue_backlog: int
    robots_online: int
    robots_total: int
    open_alerts: int
    ai_runs_active: int
