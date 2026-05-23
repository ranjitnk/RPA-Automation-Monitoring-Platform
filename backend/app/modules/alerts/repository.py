from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertRule


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_open_alerts(
        self, environment_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[Alert], int]:
        query = select(Alert).where(
            Alert.environment_id == environment_id,
            Alert.status == "open",
        )
        total = (
            await self._session.execute(
                select(func.count())
                .select_from(Alert)
                .where(Alert.environment_id == environment_id, Alert.status == "open")
            )
        ).scalar_one()
        result = await self._session.execute(
            query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def count_open(self, environment_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(Alert)
            .where(Alert.environment_id == environment_id, Alert.status == "open")
        )
        return result.scalar_one()

    async def get_alert(self, alert_id: UUID, environment_id: UUID) -> Alert | None:
        result = await self._session.execute(
            select(Alert).where(Alert.id == alert_id, Alert.environment_id == environment_id)
        )
        return result.scalar_one_or_none()

    async def create_rule(self, rule: AlertRule) -> AlertRule:
        self._session.add(rule)
        await self._session.flush()
        await self._session.refresh(rule)
        return rule

    async def list_rules(self, environment_id: UUID) -> list[AlertRule]:
        result = await self._session.execute(
            select(AlertRule).where(AlertRule.environment_id == environment_id)
        )
        return list(result.scalars().all())

    async def save_alert(self, alert: Alert) -> Alert:
        self._session.add(alert)
        await self._session.flush()
        await self._session.refresh(alert)
        return alert
