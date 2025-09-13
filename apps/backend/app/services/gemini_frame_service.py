import os
import uuid
import base64
import requests
import json
from typing import Optional
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

class GeminiAPIError(Exception):
    """Raised when the Gemini API returns a non-success response."""
    def __init__(self, code: int, status: Optional[str], message: str, raw: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.status = status
        self.message = message
        self.raw = raw

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

    def _detect_mime_type(self, image_path: str) -> str:
        """Best-effort detection of image mime type from contents.

        Defaults to image/jpeg if not detectable.
        """
        try:
            with Image.open(image_path) as img:
                fmt = (img.format or "JPEG").upper()
                if fmt == "PNG":
                    return "image/png"
                if fmt == "WEBP":
                    return "image/webp"
                if fmt == "GIF":
                    return "image/gif"
                # Default to JPEG for others (including JPEG/JPG)
                return "image/jpeg"
        except Exception:
            return "image/jpeg"

    def create_frame_with_gemini(self, image_path: str, university_name: str, university_mascot: str) -> Optional[str]:
        """Create a profile picture frame using Gemini API"""
        try:
            # Read the image and convert to base64
            image_base64 = self.image_to_base64(image_path)
            mime_type = self._detect_mime_type(image_path)
            
            # Construct the prompt
            prompt = f"""Create a circular banner frame around the face in this photo to make it suitable as a social media profile picture.
            Use the official colors and mascot of {university_name} University in the design.
            The mascot is {university_mascot}.
            Ensure the frame highlights the school spirit but does not obstruct or crop the face.
            The final frame should look professional, centered, and optimized so nothing important is cut off when uploaded as a profile photo.
            Make sure the frame is circular and the university name and mascot are visible.

            Output format requirement: Return only the final image as a PNG data URI in the response text (for example: data:image/png;base64,<BASE64>). Do not include any additional commentary or markdown.
            """
            
            # Prepare the request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                # Use camelCase per Gemini REST API
                                "inlineData": {
                                    "mimeType": mime_type,
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
                # Try to extract structured error from Gemini
                err_text = response.text
                err_code = response.status_code
                err_status = None
                err_msg = f"Gemini API returned HTTP {response.status_code}"
                try:
                    err_json = response.json()
                    if isinstance(err_json, dict) and "error" in err_json:
                        err_obj = err_json["error"] or {}
                        err_code = err_obj.get("code", err_code)
                        err_status = err_obj.get("status")
                        err_msg = err_obj.get("message", err_msg)
                except Exception:
                    # Keep defaults; include raw text
                    pass

                raise GeminiAPIError(code=int(err_code), status=err_status, message=err_msg, raw=err_text)
            
            # Parse the response
            response_data = response.json()
            
            # Extract the generated image data
            for candidate in response_data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    # Case 1: Proper inline image under either inline_data or inlineData
                    if isinstance(part, dict) and ("inline_data" in part or "inlineData" in part):
                        inline = part.get("inline_data") or part.get("inlineData") or {}
                        data_b64 = inline.get("data")
                        if data_b64:
                            generated_image_data = base64.b64decode(data_b64)
                            mime = inline.get("mime_type") or inline.get("mimeType") or "image/jpeg"
                            ext = "png" if mime.endswith("png") else ("webp" if mime.endswith("webp") else ("gif" if mime.endswith("gif") else "jpg"))
                            result_filename = f"{uuid.uuid4()}.{ext}"
                            result_path = os.path.join(self.output_dir, result_filename)
                            with open(result_path, "wb") as f:
                                f.write(generated_image_data)
                            return result_path

                    # Case 2: Some previews return a data-URI in text
                    if isinstance(part, dict) and "text" in part and isinstance(part["text"], str):
                        txt = part["text"]
                        if "data:image/" in txt and ";base64," in txt:
                            try:
                                prefix, b64 = txt.split(",", 1)
                                generated_image_data = base64.b64decode(b64)
                                ext = "png" if "image/png" in prefix else "jpg"
                                result_filename = f"{uuid.uuid4()}.{ext}"
                                result_path = os.path.join(self.output_dir, result_filename)
                                with open(result_path, "wb") as f:
                                    f.write(generated_image_data)
                                return result_path
                            except Exception:
                                pass

            # No usable image content detected; print small snippet for debugging
            try:
                snippet = json.dumps(response_data)[:500]
                print("No image data found in the response. Snippet:", snippet)
            except Exception:
                print("No image data found in the response (could not serialize).")
            return None
            
        except Exception as e:
            # Let the caller decide how to map errors; don't swallow details
            raise

# Create a singleton instance
gemini_frame_service = GeminiFrameService()
