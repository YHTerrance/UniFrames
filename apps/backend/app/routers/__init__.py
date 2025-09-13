# Frame Gen API Routers
from fastapi import APIRouter

api_router = APIRouter()

# Import and include routers
from app.routers.frames import router as frames_router
from app.routers.profile_frames import router as profile_frames_router
from app.routers.gemini_frames import router as gemini_frames_router

api_router.include_router(frames_router, prefix="/frames", tags=["frames"])
api_router.include_router(profile_frames_router)
api_router.include_router(gemini_frames_router)