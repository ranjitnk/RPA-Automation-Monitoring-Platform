from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.elasticsearch_client import es_client
from app.modules.logs.schemas import LogEntryResponse, LogSearchRequest


class LogService:
    async def search_logs(
        self,
        request: LogSearchRequest,
        *,
        environment_id: str | None = None,
        size: int = 50,
    ) -> list[LogEntryResponse]:
        if not settings.es_enabled:
            return []

        must: list[dict[str, Any]] = [
            {
                "range": {
                    "@timestamp": {
                        "gte": (datetime.now(UTC) - timedelta(minutes=request.from_minutes_ago)).isoformat()
                    }
                }
            }
        ]
        if environment_id:
            must.append({"term": {"environment_id.keyword": environment_id}})
        if request.level:
            must.append({"term": {"level.keyword": request.level}})

        query = {
            "query": {
                "bool": {
                    "must": must,
                    "should": [{"query_string": {"query": request.query, "default_field": "message"}}],
                    "minimum_should_match": 0 if request.query == "*" else 1,
                }
            },
            "sort": [{"@timestamp": "desc"}],
        }

        try:
            result = await es_client.search("app-logs", query, size=size)
        except Exception:
            return []

        entries: list[LogEntryResponse] = []
        for hit in result.get("hits", {}).get("hits", []):
            source = hit.get("_source", {})
            entries.append(
                LogEntryResponse(
                    id=hit.get("_id"),
                    timestamp=source.get("@timestamp"),
                    level=source.get("level"),
                    message=source.get("message"),
                    source=source.get("source"),
                    extra={k: v for k, v in source.items() if k not in {"@timestamp", "level", "message", "source"}},
                )
            )
        return entries

    async def write_log(
        self,
        level: str,
        message: str,
        **context: Any,
    ) -> str | None:
        document = {
            "@timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "message": message,
            **context,
        }
        return await es_client.index_document("app-logs", document)
