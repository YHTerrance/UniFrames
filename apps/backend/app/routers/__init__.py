# Frame Gen API Routers
from fastapi import APIRouter

api_router = APIRouter()

# Import and include routers
from app.routers.frames import router as frames_router

api_router.include_router(frames_router, prefix="/frames", tags=["frames"])