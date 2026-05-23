"""APScheduler background job scheduler."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler(timezone="UTC")


def register_scheduled_jobs() -> None:
    from app.modules.orchestrator_connector.tasks import run_sync_all_environments
    from app.modules.alerts.tasks import run_evaluate_all_alerts

    scheduler.add_job(
        run_sync_all_environments,
        trigger=IntervalTrigger(seconds=settings.scheduler_sync_interval_seconds),
        id="sync_orchestrator_all",
        replace_existing=True,
    )
    scheduler.add_job(
        run_evaluate_all_alerts,
        trigger=IntervalTrigger(seconds=settings.scheduler_sla_interval_seconds),
        id="evaluate_alerts_all",
        replace_existing=True,
    )
    logger.info("scheduler_jobs_registered")


def start_scheduler() -> None:
    if not settings.scheduler_enabled:
        return
    register_scheduled_jobs()
    if not scheduler.running:
        scheduler.start()
        logger.info("scheduler_started")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("scheduler_stopped")
