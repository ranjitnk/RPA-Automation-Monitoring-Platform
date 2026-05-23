from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class EnvironmentCreate(BaseModel):
    name: str
    base_url: HttpUrl
    tenant_name: str | None = None
    client_id: str
    client_secret: str


class EnvironmentResponse(BaseModel):
    id: UUID
    name: str
    base_url: str
    tenant_name: str | None
    is_active: bool
    sync_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConnectionTestResponse(BaseModel):
    environment_id: UUID
    success: bool
    message: str
    latency_ms: float | None = None


class SyncTriggerResponse(BaseModel):
    environment_id: UUID
    status: str
    synced: dict[str, int]
