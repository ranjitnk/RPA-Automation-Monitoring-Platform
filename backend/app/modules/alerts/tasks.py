"""Scheduled alert evaluation tasks."""

from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_evaluate_all_alerts() -> None:
    logger.info("evaluate_alerts_started")
    # TODO: load active environments and call AlertService.evaluate_environment
    logger.info("evaluate_alerts_completed")
