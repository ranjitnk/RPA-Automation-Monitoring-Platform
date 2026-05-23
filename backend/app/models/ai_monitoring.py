import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AIWorkflowRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ai_workflow_runs"

    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    run_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    agent_steps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    llm_latency_ms: Mapped[float | None] = mapped_column(Float)
    token_count: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    run_metadata: Mapped[dict | None] = mapped_column(JSONB)

    environment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orchestrator_environments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
