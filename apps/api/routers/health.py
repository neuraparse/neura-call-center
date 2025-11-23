"""Health check endpoints."""

import time
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.core.config import settings
from apps.core.database import get_db
from apps.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ComponentStatus(BaseModel):
    """Component health status."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: float | None = None
    message: str | None = None


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    service: str
    version: str
    environment: str
    components: list[ComponentStatus]


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env.value,
    }


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check including database."""
    try:
        # Check database connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()

        return {
            "status": "ready",
            "database": "connected",
            "cache": "connected" if settings.cache_enabled else "disabled",
        }
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return {
            "status": "not_ready",
            "error": str(e),
        }


@router.get("/health/live")
async def liveness_check():
    """Liveness check."""
    return {"status": "alive"}


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with component status."""
    components = []
    overall_status = "healthy"

    # Check database
    db_start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        db_latency = (time.time() - db_start) * 1000
        components.append(ComponentStatus(
            name="database",
            status="healthy",
            latency_ms=round(db_latency, 2),
            message="PostgreSQL connection OK"
        ))
    except Exception as e:
        components.append(ComponentStatus(
            name="database",
            status="unhealthy",
            message=str(e)
        ))
        overall_status = "unhealthy"

    # Check cache (Redis/Valkey)
    if settings.cache_enabled:
        try:
            import redis.asyncio as redis
            cache_start = time.time()
            r = redis.from_url(str(settings.cache_url))
            await r.ping()
            cache_latency = (time.time() - cache_start) * 1000
            await r.close()
            components.append(ComponentStatus(
                name="cache",
                status="healthy",
                latency_ms=round(cache_latency, 2),
                message="Redis/Valkey connection OK"
            ))
        except Exception as e:
            components.append(ComponentStatus(
                name="cache",
                status="degraded",
                message=str(e)
            ))
            if overall_status == "healthy":
                overall_status = "degraded"
    else:
        components.append(ComponentStatus(
            name="cache",
            status="healthy",
            message="Cache disabled"
        ))

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        service=settings.app_name,
        version="0.1.0",
        environment=settings.app_env.value,
        components=components
    )

