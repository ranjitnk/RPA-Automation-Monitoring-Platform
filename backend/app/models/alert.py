import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AlertRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric: Mapped[str] = mapped_column(String(64), nullable=False)
    condition: Mapped[dict] = mapped_column(JSONB, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="warning", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    environment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orchestrator_environments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class Alert(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "alerts"

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alert_rules.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(16), default="open", nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    environment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orchestrator_environments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
