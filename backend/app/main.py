"""FastAPI application factory."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.core.cache import cache
from app.core.config import settings
from app.core.elasticsearch_client import es_client
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.scheduler import shutdown_scheduler, start_scheduler
from app.middleware.logging import LoggingMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    await cache.connect()
    try:
        await es_client.connect()
    except Exception:
        if settings.es_enabled and settings.is_production:
            raise
    start_scheduler()
    yield
    shutdown_scheduler()
    await cache.disconnect()
    await es_client.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.app_api_prefix)
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    return app


app = create_app()
