from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import os

from app.dependencies import get_gemini_frame_service
from app.services.gemini_frame_service import GeminiAPIError

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
            # Non-exceptional failure from service; treat as bad gateway to indicate upstream issue
            raise HTTPException(status_code=502, detail="Failed to create frame with Gemini")
        
        # Convert the result to base64 and report accurate mime
        image_base64 = frame_service.image_to_base64(result_path)
        try:
            mime = frame_service._detect_mime_type(result_path)
        except Exception:
            mime = "image/jpeg"
        
        return {
            "status": "success",
            "message": "Profile frame created successfully with Gemini",
            "data": {
                "university_name": university_name,
                "university_mascot": university_mascot,
                "image_path": image_path,
                "result_path": result_path,
                "image_base64": f"data:{mime};base64,{image_base64}"
            }
        }
    
    except HTTPException:
        # Let HTTPExceptions bubble up unchanged
        raise
    except GeminiAPIError as e:
        # Map specific Gemini errors to appropriate HTTP status codes
        if e.code == 429 or (e.status and "RESOURCE_EXHAUSTED" in e.status):
            raise HTTPException(
                status_code=429,
                detail=(e.message or "Google Gemini API quota exceeded. Please try again later.")
            )
        # 4xx from upstream -> 502 Bad Gateway with detail
        status = 502
        if 400 <= (e.code or 0) < 500:
            status = 502
        raise HTTPException(status_code=status, detail=f"Gemini API error: {e.status or e.code}: {e.message}")
    except Exception as e:
        # Generic unexpected error
        raise HTTPException(status_code=500, detail=str(e))
