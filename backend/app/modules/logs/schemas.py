from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogSearchRequest(BaseModel):
    query: str = Field(default="*", description="Lucene query string")
    level: str | None = None
    from_minutes_ago: int = Field(60, ge=1, le=10080)


class LogEntryResponse(BaseModel):
    id: str | None
    timestamp: datetime | None
    level: str | None
    message: str | None
    source: str | None
    extra: dict[str, Any] = Field(default_factory=dict)
