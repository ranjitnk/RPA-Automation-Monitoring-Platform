from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AlertRuleCreate(BaseModel):
    name: str
    metric: str
    condition: dict[str, Any]
    severity: str = "warning"


class AlertRuleResponse(BaseModel):
    id: UUID
    environment_id: UUID
    name: str
    metric: str
    condition: dict[str, Any]
    severity: str
    is_enabled: bool

    model_config = {"from_attributes": True}


class AlertResponse(BaseModel):
    id: UUID
    environment_id: UUID
    rule_id: UUID
    status: str
    message: str
    created_at: datetime
    acknowledged_at: datetime | None

    model_config = {"from_attributes": True}


class AlertAcknowledge(BaseModel):
    note: str | None = Field(None, max_length=500)
