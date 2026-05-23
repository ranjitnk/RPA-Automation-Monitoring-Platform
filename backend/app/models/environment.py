from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class OrchestratorEnvironment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "orchestrator_environments"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    tenant_name: Mapped[str | None] = mapped_column(String(128))
    credentials_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
