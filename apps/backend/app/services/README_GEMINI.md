# Gemini Frame Service

This service uses Google's Gemini API to generate custom profile picture frames with university colors and mascots.

## Setup

1. Make sure you have the required dependencies installed:
   ```
   pip install -r requirements.txt
   ```

2. Set up your Gemini API key as an environment variable:
   ```
   export GEMINI_API_KEY="your_api_key_here"
   ```
   
   Or add it to your `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

The service can be used through the FastAPI endpoint:

```
POST /api/v1/gemini-frames/
```

Parameters (form data):
- `university_name`: The name of the university for colors and branding
- `university_mascot`: The university mascot to incorporate in the design
- `image`: The profile image file to add the frame to

Example curl request:
```bash
curl -X POST "http://localhost:8000/api/v1/gemini-frames/" \
  -F "university_name=Harvard" \
  -F "university_mascot=Crimson" \
  -F "image=@/path/to/your/profile.jpg"
```

Response:
```json
{
  "status": "success",
  "message": "Profile frame created successfully with Gemini",
  "data": {
    "university_name": "Harvard",
    "university_mascot": "Crimson",
    "image_path": "uploads/12345.jpg",
    "result_path": "outputs/67890.jpg",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
}
```

## How It Works

1. The service takes the uploaded profile picture and sends it to the Gemini API
2. It provides a detailed prompt specifying:
   - The circular banner frame requirement
   - University name and mascot to incorporate
   - Design constraints (not obstructing the face, professional look)
3. Gemini generates the image with the custom frame
4. The service returns the processed image as a base64 string for immediate display

## Notes

- The Gemini API requires an API key from Google
- Image generation may take a few seconds to complete
- The service stores both the original and processed images on the server