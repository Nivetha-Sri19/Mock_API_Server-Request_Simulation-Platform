from fastapi import APIRouter

from app.api.v1 import (
    auth,
    dashboard,
    mock_apis,
    permissions,
    request_logs,
    request_schemas,
    scenarios,
    users,
    versions,
)


router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(mock_apis.router)
router.include_router(versions.router)
router.include_router(scenarios.router)
router.include_router(permissions.router)
router.include_router(request_logs.router)
router.include_router(request_schemas.router)
router.include_router(dashboard.router)