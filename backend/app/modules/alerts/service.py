from datetime import UTC, datetime
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.alert import Alert, AlertRule
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.schemas import (
    AlertAcknowledge,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
)
from app.schemas.common import PaginatedResponse, PaginationParams


class AlertService:
    def __init__(self, repository: AlertRepository) -> None:
        self._repo = repository

    async def list_open_alerts(
        self, environment_id: UUID, pagination: PaginationParams
    ) -> PaginatedResponse[AlertResponse]:
        items, total = await self._repo.list_open_alerts(
            environment_id, offset=pagination.offset, limit=pagination.page_size
        )
        return PaginatedResponse[AlertResponse](
            items=[AlertResponse.model_validate(i) for i in items],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def create_rule(self, environment_id: UUID, data: AlertRuleCreate) -> AlertRuleResponse:
        rule = AlertRule(
            environment_id=environment_id,
            name=data.name,
            metric=data.metric,
            condition=data.condition,
            severity=data.severity,
        )
        created = await self._repo.create_rule(rule)
        return AlertRuleResponse.model_validate(created)

    async def list_rules(self, environment_id: UUID) -> list[AlertRuleResponse]:
        rules = await self._repo.list_rules(environment_id)
        return [AlertRuleResponse.model_validate(r) for r in rules]

    async def acknowledge_alert(
        self, alert_id: UUID, environment_id: UUID, _data: AlertAcknowledge
    ) -> AlertResponse:
        alert = await self._repo.get_alert(alert_id, environment_id)
        if not alert:
            raise NotFoundError("Alert not found")
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.now(UTC)
        updated = await self._repo.save_alert(alert)
        return AlertResponse.model_validate(updated)

    async def evaluate_environment(self, environment_id: UUID) -> int:
        """Placeholder SLA evaluation — extend with metric engines."""
        _ = environment_id
        return 0
