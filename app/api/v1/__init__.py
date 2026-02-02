"""API v1 module initialization."""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.strava import router as strava_router
from app.api.v1.activities import router as activities_router
from app.api.v1.coach import router as coach_router
from app.api.v1.routines import router as routines_router
from app.api.v1.motivation import router as motivation
from app.api.v1.notifications import router as notifications_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(strava_router)
api_router.include_router(activities_router)
api_router.include_router(coach_router)
api_router.include_router(routines_router)
api_router.include_router(motivation)
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])