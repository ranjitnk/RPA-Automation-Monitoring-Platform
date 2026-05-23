"""UiPath Orchestrator OData HTTP client."""

import time
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OrchestratorHttpClient:
    def __init__(self, base_url: str, access_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {access_token}"}
        self._timeout = settings.orch_http_timeout_seconds

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def get(self, odata_path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}/odata/{odata_path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers, params=params)
            if response.status_code >= 400:
                logger.warning("orchestrator_request_failed", status=response.status_code, path=odata_path)
                raise ExternalServiceError(
                    f"Orchestrator request failed: {response.status_code}",
                    details={"path": odata_path},
                )
            return response.json()

    async def ping(self) -> float:
        start = time.perf_counter()
        await self.get("Jobs", params={"$top": 1})
        return (time.perf_counter() - start) * 1000

    async def fetch_jobs(self, top: int = 100) -> list[dict[str, Any]]:
        data = await self.get("Jobs", params={"$top": top, "$orderby": "CreationTime desc"})
        return data.get("value", [])

    async def fetch_queues(self) -> list[dict[str, Any]]:
        data = await self.get("QueueDefinitions")
        return data.get("value", [])

    async def fetch_robots(self) -> list[dict[str, Any]]:
        data = await self.get("Robots")
        return data.get("value", [])
