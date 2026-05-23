from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: UUID
    environment_id: UUID
    orchestrator_job_id: int
    state: str
    process_name: str | None
    robot_name: str | None
    started_at: datetime | None
    ended_at: datetime | None
    last_synced_at: datetime

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    orchestrator_job_id: int
    state: str
    process_name: str | None = None
    robot_name: str | None = None
