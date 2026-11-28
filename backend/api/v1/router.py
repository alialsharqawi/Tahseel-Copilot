from __future__ import annotations

from fastapi import APIRouter

from api.v1.auth import router as auth_router
from api.v1.configuration import router as configuration_router
from api.v1.customers import router as customers_router
from api.v1.users import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(customers_router)
router.include_router(configuration_router)
