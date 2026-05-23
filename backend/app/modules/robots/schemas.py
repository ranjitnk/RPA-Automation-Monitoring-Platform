from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RobotResponse(BaseModel):
    id: UUID
    environment_id: UUID
    orchestrator_robot_id: int
    name: str
    machine_name: str | None
    status: str
    is_online: bool
    last_synced_at: datetime

    model_config = {"from_attributes": True}
