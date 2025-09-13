from fastapi import Depends, HTTPException, status
from app.services.frame_service import frame_service

# Example dependency to get the frame service
def get_frame_service():
    return frame_service

# Add more dependencies as needed