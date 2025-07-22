from typing import Any, Dict

from fastapi import APIRouter

health_check_router = APIRouter(prefix="/health", tags=["Health"])


@health_check_router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "bugninja-backend", "version": "0.1.0"}


@health_check_router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status"""
    # TODO: Add database and Redis connectivity checks
    return {
        "status": "healthy",
        "service": "bugninja-backend",
        "version": "0.1.0",
        "checks": {"database": "not_implemented", "redis": "not_implemented"},
    }
