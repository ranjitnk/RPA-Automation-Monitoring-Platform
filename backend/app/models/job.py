import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Job(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "jobs"

    orchestrator_job_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    process_name: Mapped[str | None] = mapped_column(String(255))
    robot_name: Mapped[str | None] = mapped_column(String(255))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    environment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orchestrator_environments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
