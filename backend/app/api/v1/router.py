from fastapi import APIRouter

from app.api.v1.endpoints.health import health_check_router
from app.api.v1.endpoints.project import projects_router

api_router = APIRouter()


api_router.include_router(health_check_router)
api_router.include_router(projects_router)
