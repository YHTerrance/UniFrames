from fastapi import Depends, HTTPException, status
from app.services.frame_service import frame_service
from app.services.gemini_frame_service import gemini_frame_service

# Example dependency to get the frame service
def get_frame_service():
    return frame_service

# Dependency to get the Gemini frame service
def get_gemini_frame_service():
    return gemini_frame_service

# Add more dependencies as needed