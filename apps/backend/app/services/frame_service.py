from typing import List, Optional
from app.models.frame import Frame

# This is a mock service for demonstration purposes
# In a real application, this would interact with a database
class FrameService:
    def __init__(self):
        # Mock database
        self.frames = [
            {"id": 1, "title": "Sample Frame 1", "description": "This is a sample frame", "image_url": "https://example.com/frame1.jpg"},
            {"id": 2, "title": "Sample Frame 2", "description": "Another sample frame", "image_url": "https://example.com/frame2.jpg"},
        ]
    
    def get_frames(self) -> List[dict]:
        """Get all frames"""
        return self.frames
    
    def get_frame(self, frame_id: int) -> Optional[dict]:
        """Get a specific frame by ID"""
        for frame in self.frames:
            if frame["id"] == frame_id:
                return frame
        return None
    
    def create_frame(self, frame_data: dict) -> dict:
        """Create a new frame"""
        new_frame = frame_data.copy()
        new_frame["id"] = len(self.frames) + 1
        self.frames.append(new_frame)
        return new_frame
    
    def update_frame(self, frame_id: int, frame_data: dict) -> Optional[dict]:
        """Update an existing frame"""
        for i, frame in enumerate(self.frames):
            if frame["id"] == frame_id:
                updated_frame = frame_data.copy()
                updated_frame["id"] = frame_id
                self.frames[i] = updated_frame
                return updated_frame
        return None
    
    def delete_frame(self, frame_id: int) -> bool:
        """Delete a frame"""
        for i, frame in enumerate(self.frames):
            if frame["id"] == frame_id:
                self.frames.pop(i)
                return True
        return False

# Create a singleton instance
frame_service = FrameService()