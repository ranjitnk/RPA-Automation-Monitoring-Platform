"""Async Elasticsearch client wrapper."""

from typing import Any

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ApiError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ElasticsearchClient:
    def __init__(self) -> None:
        self._client: AsyncElasticsearch | None = None

    async def connect(self) -> None:
        if not settings.es_enabled:
            return
        auth = None
        if settings.es_username:
            auth = (settings.es_username, settings.es_password)
        self._client = AsyncElasticsearch(
            settings.es_url,
            basic_auth=auth,
            verify_certs=settings.es_verify_certs,
        )
        if not await self._client.ping():
            raise ConnectionError("Elasticsearch ping failed")
        logger.info("elasticsearch_connected")

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()

    async def ping(self) -> bool:
        if not self._client:
            return False
        return await self._client.ping()

    @property
    def client(self) -> AsyncElasticsearch:
        if not self._client:
            raise RuntimeError("Elasticsearch client is not initialized")
        return self._client

    def index_name(self, suffix: str) -> str:
        return f"{settings.es_index_prefix}-{suffix}"

    async def index_document(self, index_suffix: str, document: dict[str, Any]) -> str | None:
        if not self._client:
            return None
        try:
            response = await self._client.index(
                index=self.index_name(index_suffix),
                document=document,
            )
            return response.get("_id")
        except ApiError as exc:
            logger.error("es_index_failed", error=str(exc))
            return None

    async def search(
        self,
        index_suffix: str,
        query: dict[str, Any],
        *,
        size: int = 50,
        from_: int = 0,
    ) -> dict[str, Any]:
        if not self._client:
            return {"hits": {"hits": [], "total": {"value": 0}}}
        return await self._client.search(
            index=self.index_name(index_suffix),
            query=query.get("query", {"match_all": {}}),
            sort=query.get("sort"),
            size=size,
            from_=from_,
        )


es_client = ElasticsearchClient()
