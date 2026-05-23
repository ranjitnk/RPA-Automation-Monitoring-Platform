from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QueueResponse(BaseModel):
    id: UUID
    environment_id: UUID
    orchestrator_queue_id: int
    name: str
    items_in_queue: int
    items_processing: int
    items_failed: int
    last_synced_at: datetime

    model_config = {"from_attributes": True}
