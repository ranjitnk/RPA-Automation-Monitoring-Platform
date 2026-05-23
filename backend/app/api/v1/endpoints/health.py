"""
Health check endpoint.
Provides application and service health status.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.schemas.common import HealthCheckSchema
import asyncio

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


async def check_database(db: AsyncSession) -> str:
    """Check database connection."""
    try:
        await db.execute("SELECT 1")
        return "healthy"
    except Exception as e:
        logger.error(f"Database check failed: {str(e)}")
        return "unhealthy"


async def check_elasticsearch() -> str:
    """Check Elasticsearch connection."""
    try:
        from app.core.elasticsearch_client import get_elasticsearch_client

        client = get_elasticsearch_client()
        client.info()
        return "healthy"
    except Exception as e:
        logger.warning(f"Elasticsearch check failed: {str(e)}")
        return "degraded"


async def check_redis() -> str:
    """Check Redis connection."""
    try:
        from app.core.cache import get_redis_client

        client = await get_redis_client()
        await client.ping()
        return "healthy"
    except Exception as e:
        logger.warning(f"Redis check failed: {str(e)}")
        return "degraded"


@router.get("/health", response_model=HealthCheckSchema)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthCheckSchema:
    """
    Health check endpoint.

    Checks the health of all critical services and returns status.
    """
    settings = get_settings()

    # Run health checks in parallel
    db_status, redis_status, es_status = await asyncio.gather(
        check_database(db),
        check_redis(),
        check_elasticsearch(),
    )

    services = {
        "database": db_status,
        "redis": redis_status,
        "elasticsearch": es_status,
    }

    # Determine overall status
    if all(status == "healthy" for status in services.values()):
        overall_status = "healthy"
    elif any(status == "unhealthy" for status in services.values()):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"

    return HealthCheckSchema(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        version=settings.APP_VERSION,
        services=services,
    )


@router.get("/health/live")
async def liveness_probe():
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get("/health/ready", response_model=HealthCheckSchema)
async def readiness_probe(db: AsyncSession = Depends(get_db)) -> HealthCheckSchema:
    """Kubernetes readiness probe."""
    return await health_check(db)
