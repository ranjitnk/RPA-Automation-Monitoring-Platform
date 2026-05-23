"""Dependency injection — session, auth, services, environment scope."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token_safe
from app.models.user import User
from app.modules.ai_monitoring.repository import AIMonitoringRepository
from app.modules.ai_monitoring.service import AIMonitoringService
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.service import AlertService
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService
from app.modules.dashboards.service import DashboardService
from app.modules.jobs.repository import JobRepository
from app.modules.jobs.service import JobService
from app.modules.logs.service import LogService
from app.modules.orchestrator_connector.repository import OrchestratorEnvironmentRepository
from app.modules.orchestrator_connector.service import OrchestratorConnectorService
from app.modules.queues.repository import QueueRepository
from app.modules.queues.service import QueueService
from app.modules.robots.repository import RobotRepository
from app.modules.robots.service import RobotService

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if not credentials:
        raise UnauthorizedError("Not authenticated")
    payload = decode_token_safe(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("Invalid or expired token")
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError("Invalid token subject") from exc

    user = await AuthRepository(db).get_user_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


async def get_environment_id(
    x_environment_id: Annotated[str | None, Header(alias="X-Environment-Id")] = None,
) -> UUID:
    if not x_environment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Environment-Id header is required",
        )
    try:
        return UUID(x_environment_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Environment-Id",
        ) from exc


def require_active_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


def require_superuser(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_superuser:
        raise ForbiddenError("Superuser access required")
    return user


# --- Service providers (DI) ---


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuthService:
    return AuthService(AuthRepository(db))


def get_job_service(db: Annotated[AsyncSession, Depends(get_db)]) -> JobService:
    return JobService(JobRepository(db))


def get_queue_service(db: Annotated[AsyncSession, Depends(get_db)]) -> QueueService:
    return QueueService(QueueRepository(db))


def get_robot_service(db: Annotated[AsyncSession, Depends(get_db)]) -> RobotService:
    return RobotService(RobotRepository(db))


def get_log_service() -> LogService:
    return LogService()


def get_ai_monitoring_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AIMonitoringService:
    return AIMonitoringService(AIMonitoringRepository(db))


def get_alert_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AlertService:
    return AlertService(AlertRepository(db))


def get_dashboard_service(db: Annotated[AsyncSession, Depends(get_db)]) -> DashboardService:
    return DashboardService(
        job_repo=JobRepository(db),
        queue_repo=QueueRepository(db),
        robot_repo=RobotRepository(db),
        alert_repo=AlertRepository(db),
    )


def get_orchestrator_connector_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrchestratorConnectorService:
    return OrchestratorConnectorService(OrchestratorEnvironmentRepository(db))
