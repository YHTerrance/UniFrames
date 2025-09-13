from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

# Sample Frame model
class FrameBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class FrameCreate(FrameBase):
    pass

class Frame(FrameBase):
    id: int
    
    class Config:
        orm_mode = True


@router.get("/", response_model=List[Frame])
async def get_frames():
    """Get all frames"""
    return frames_db

@router.get("/{frame_id}", response_model=Frame)
async def get_frame(frame_id: int):
    """Get a specific frame by ID"""
    for frame in frames_db:
        if frame["id"] == frame_id:
            return frame
    raise HTTPException(status_code=404, detail="Frame not found")

@router.post("/", response_model=Frame, status_code=status.HTTP_201_CREATED)
async def create_frame(frame: FrameCreate):
    """Create a new frame"""
    new_frame = frame.dict()
    new_frame["id"] = len(frames_db) + 1
    frames_db.append(new_frame)
    return new_frame

@router.put("/{frame_id}", response_model=Frame)
async def update_frame(frame_id: int, frame: FrameBase):
    """Update an existing frame"""
    for i, existing_frame in enumerate(frames_db):
        if existing_frame["id"] == frame_id:
            updated_frame = frame.dict()
            updated_frame["id"] = frame_id
            frames_db[i] = updated_frame
            return updated_frame
    raise HTTPException(status_code=404, detail="Frame not found")

@router.delete("/{frame_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_frame(frame_id: int):
    """Delete a frame"""
    for i, frame in enumerate(frames_db):
        if frame["id"] == frame_id:
            frames_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Frame not found")