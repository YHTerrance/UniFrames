import os
import uuid
import base64
import requests
import json
from typing import Optional
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

class GeminiFrameService:
    def __init__(self, upload_dir: str = "uploads", output_dir: str = "outputs"):
        # Create directories if they don't exist
        self.upload_dir = upload_dir
        self.output_dir = output_dir
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Gemini API endpoint
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
    
    def save_uploaded_image(self, image_data: bytes) -> str:
        """Save the uploaded image and return the file path"""
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(self.upload_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        return file_path
    
    def image_to_base64(self, image_path: str) -> str:
        """Convert an image to base64 string"""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def create_frame_with_gemini(self, image_path: str, university_name: str, university_mascot: str) -> Optional[str]:
        """Create a profile picture frame using Gemini API"""
        try:
            # Read the image and convert to base64
            image_base64 = self.image_to_base64(image_path)
            
            # Construct the prompt
            prompt = f"""Create a circular banner frame around the face in this photo to make it suitable as a social media profile picture. 
            Use the official colors and mascot of {university_name} University in the design. 
            The mascot is {university_mascot}.
            Ensure the frame highlights the school spirit but does not obstruct or crop the face. 
            The final frame should look professional, centered, and optimized so nothing important is cut off when uploaded as a profile photo.
            Make sure the frame is circular and the university name and mascot are visible.
            """
            
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ],
                "generation_config": {
                    "temperature": 0.4,
                    "top_p": 0.95,
                    "top_k": 32,
                    "max_output_tokens": 8192,
                }
            }
            
            # Make the API request
            response = requests.post(
                f"{self.api_url}?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                return None
            
            # Parse the response
            response_data = response.json()
            
            # Extract the generated image data
            for candidate in response_data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "inline_data" in part:
                        # Save the generated image
                        generated_image_data = base64.b64decode(part["inline_data"]["data"])
                        result_filename = f"{uuid.uuid4()}.jpg"
                        result_path = os.path.join(self.output_dir, result_filename)
                        
                        with open(result_path, "wb") as f:
                            f.write(generated_image_data)
                        
                        return result_path
            
            print("No image data found in the response")
            return None
            
        except Exception as e:
            print(f"Error creating frame with Gemini: {str(e)}")
            return None

# Create a singleton instance
gemini_frame_service = GeminiFrameService()