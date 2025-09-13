from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import os

from app.dependencies import get_gemini_frame_service

router = APIRouter(prefix="/gemini-frames", tags=["gemini-frames"])

@router.post("/", response_model=dict)
async def create_gemini_frame(
    university_name: str = Form(...),
    university_mascot: str = Form(...),
    image: UploadFile = File(...),
    frame_service = Depends(get_gemini_frame_service)
):
    """Create a profile picture frame with university colors and mascot using Gemini API"""
    try:
        # Read the image data
        image_data = await image.read()
        
        # Save the uploaded image
        image_path = frame_service.save_uploaded_image(image_data)
        
        # Create the frame using Gemini
        result_path = frame_service.create_frame_with_gemini(
            image_path, 
            university_name, 
            university_mascot
        )
        
        if not result_path:
            raise HTTPException(status_code=500, detail="Failed to create frame with Gemini")
        
        # Convert the result to base64
        image_base64 = frame_service.image_to_base64(result_path)
        
        return {
            "status": "success",
            "message": "Profile frame created successfully with Gemini",
            "data": {
                "university_name": university_name,
                "university_mascot": university_mascot,
                "image_path": image_path,
                "result_path": result_path,
                "image_base64": f"data:image/jpeg;base64,{image_base64}"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))