from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AIWorkflowRunResponse(BaseModel):
    id: UUID
    environment_id: UUID
    workflow_name: str
    run_id: str
    status: str
    agent_steps: int
    llm_latency_ms: float | None
    token_count: int | None
    started_at: datetime | None
    ended_at: datetime | None

    model_config = {"from_attributes": True}


class AIWorkflowRunCreate(BaseModel):
    workflow_name: str
    run_id: str
    status: str = "running"
    agent_steps: int = 0
    llm_latency_ms: float | None = None
    token_count: int | None = None
    run_metadata: dict[str, Any] = Field(default_factory=dict)
