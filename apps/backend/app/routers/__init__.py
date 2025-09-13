# Frame Gen API Routers
from fastapi import APIRouter

api_router = APIRouter()

# Import and include routers
from app.routers.frames import router as frames_router
from app.routers.gemini_frames import router as gemini_frames_router

api_router.include_router(frames_router, prefix="/frames", tags=["frames"])
api_router.include_router(gemini_frames_router)

# Add Import
from app.routers.db_router import router as db_router
from app.routers.univ_frames import router as univ_frames_router

api_router.include_router(db_router)
api_router.include_router(univ_frames_router)