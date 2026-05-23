"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1 import health
from app.modules.ai_monitoring.router import router as ai_monitoring_router
from app.modules.alerts.router import router as alerts_router
from app.modules.auth.router import router as auth_router
from app.modules.dashboards.router import router as dashboards_router
from app.modules.jobs.router import router as jobs_router
from app.modules.logs.router import router as logs_router
from app.modules.orchestrator_connector.router import router as orchestrator_router
from app.modules.queues.router import router as queues_router
from app.modules.robots.router import router as robots_router

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(queues_router, prefix="/queues", tags=["Queues"])
api_router.include_router(robots_router, prefix="/robots", tags=["Robots"])
api_router.include_router(logs_router, prefix="/logs", tags=["Logs"])
api_router.include_router(ai_monitoring_router, prefix="/ai-monitoring", tags=["AI Monitoring"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(dashboards_router, prefix="/dashboards", tags=["Dashboards"])
api_router.include_router(orchestrator_router, prefix="/orchestrator", tags=["Orchestrator Connector"])
