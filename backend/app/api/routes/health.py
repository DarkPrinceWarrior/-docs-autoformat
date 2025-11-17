"""Health check endpoints."""
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from pydantic import BaseModel
from typing import Dict, Any
import aiohttp
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str
    version: str
    checks: Dict[str, Any]


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.

    Checks:
    - API is running
    - Database connectivity
    - Redis connectivity (for Celery)
    - Disk space for uploads

    Returns:
        Health status with details of all checks
    """
    checks = {}

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = {"status": "unhealthy", "message": str(e)}

    # Check Redis (Celery broker)
    try:
        async with aiohttp.ClientSession() as session:
            # Simple check if Redis is accessible (this is basic, ideally use redis-py)
            # For now, we'll mark it as unknown since we don't have direct Redis client
            checks["redis"] = {"status": "unknown", "message": "Redis check not implemented"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        checks["redis"] = {"status": "unhealthy", "message": str(e)}

    # Check disk space for uploads
    try:
        import shutil
        stat = shutil.disk_usage(settings.UPLOAD_DIR)
        free_gb = stat.free / (1024**3)
        total_gb = stat.total / (1024**3)
        percent_free = (stat.free / stat.total) * 100

        disk_status = "healthy" if percent_free > 10 else "warning" if percent_free > 5 else "critical"

        checks["disk_space"] = {
            "status": disk_status,
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "percent_free": round(percent_free, 2)
        }
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
        checks["disk_space"] = {"status": "unknown", "message": str(e)}

    # Determine overall status
    overall_status = "healthy"
    for check_name, check_result in checks.items():
        if check_result.get("status") == "unhealthy":
            overall_status = "unhealthy"
            break
        elif check_result.get("status") in ["warning", "critical"]:
            overall_status = "degraded"

    return HealthStatus(
        status=overall_status,
        version=settings.VERSION,
        checks=checks
    )


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_probe():
    """
    Kubernetes liveness probe.

    Simple check that the application is running.
    Returns 200 if the app is alive, otherwise Kubernetes will restart the pod.

    Returns:
        Simple alive status
    """
    return {"status": "alive"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """
    Kubernetes readiness probe.

    Checks if the application is ready to serve traffic.
    Verifies critical dependencies (database) are accessible.

    Returns:
        Ready status

    Raises:
        HTTPException: If critical dependencies are not available
    """
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        # Return 503 Service Unavailable if not ready
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@router.get("/health/metrics", status_code=status.HTTP_200_OK)
async def metrics_endpoint(db: AsyncSession = Depends(get_db)):
    """
    Basic metrics endpoint.

    Provides simple application metrics.

    Returns:
        Application metrics
    """
    try:
        # Count documents in database
        from sqlalchemy import select, func
        from app.models.document import Document

        result = await db.execute(select(func.count(Document.id)))
        total_documents = result.scalar()

        # Count by status
        from app.models.document import DocumentStatus
        status_counts = {}

        for doc_status in DocumentStatus:
            result = await db.execute(
                select(func.count(Document.id)).where(Document.status == doc_status)
            )
            status_counts[doc_status.value] = result.scalar()

        return {
            "total_documents": total_documents,
            "documents_by_status": status_counts,
            "version": settings.VERSION
        }
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return {"error": str(e)}
