from fastapi import APIRouter

from app.api.v1.endpoints.browser_config import browser_configs_router
from app.api.v1.endpoints.document import documents_router
from app.api.v1.endpoints.health import health_check_router
from app.api.v1.endpoints.project import projects_router
from app.api.v1.endpoints.secret_value import secret_values_router
from app.api.v1.endpoints.test_case import test_cases_router
from app.api.v1.endpoints.test_run import test_runs_router
from app.api.v1.endpoints.test_traversal import test_traversals_router

api_router = APIRouter()


api_router.include_router(health_check_router)
api_router.include_router(projects_router)
api_router.include_router(documents_router)
api_router.include_router(secret_values_router)
api_router.include_router(browser_configs_router)
api_router.include_router(test_cases_router)
api_router.include_router(test_runs_router)
api_router.include_router(test_traversals_router)
