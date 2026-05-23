from fastapi import APIRouter

from app.core.cache import cache
from app.core.config import settings
from app.core.database import check_database
from app.core.elasticsearch_client import es_client

router = APIRouter()


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready")
async def readiness() -> dict[str, object]:
    checks: dict[str, object] = {"database": False, "redis": False, "elasticsearch": False}

    try:
        checks["database"] = await check_database()
    except Exception:
        checks["database"] = False

    if settings.redis_enabled:
        try:
            checks["redis"] = await cache.ping()
        except Exception:
            checks["redis"] = False
    else:
        checks["redis"] = "disabled"

    if settings.es_enabled:
        try:
            checks["elasticsearch"] = await es_client.ping()
        except Exception:
            checks["elasticsearch"] = False
    else:
        checks["elasticsearch"] = "disabled"

    all_ok = checks["database"] is True and checks["redis"] in (True, "disabled")
    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
        "version": settings.app_version,
        "environment": settings.app_env,
    }
