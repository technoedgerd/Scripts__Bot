from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import requests

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
VIDEO_API_KEY = os.getenv("VIDEO_API_KEY")

if not PEXELS_API_KEY:
    raise RuntimeError("PEXELS_API_KEY missing in .env")

# --------------------------------------------------
# Disable OpenAPI / Docs
# --------------------------------------------------
app = FastAPI(
    title="Media Backend API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# --------------------------------------------------
# Request Models
# --------------------------------------------------
class MediaRequest(BaseModel):
    type: str
    prompt: str
    orientation: str = "landscape"

# --------------------------------------------------
# Health Check
# --------------------------------------------------
@app.get("/")
def home():
    return {"status": "Backend running without RAG"}

# --------------------------------------------------
# IMAGE GENERATION (Pexels)
# --------------------------------------------------
@app.post("/media-generate")
def generate_image(payload: dict):
    """
    Expected payload:
    {
      "type": "image",
      "prompt": "NEET students studying online",
      "orientation": "landscape"
    }
    """

    media_type = payload.get("type")
    prompt = payload.get("prompt")

    if media_type != "image":
        return {"error": "Only image generation supported"}

    if not prompt:
        return {"error": "prompt is required"}

    headers = {
        "Authorization": os.getenv("PEXELS_API_KEY")
    }

    params = {
        "query": prompt,
        "per_page": 1,
        "orientation": payload.get("orientation", "landscape")
    }

    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params=params,
        timeout=10
    )

    if response.status_code != 200:
        return {"error": "Failed to fetch image from Pexels"}

    data = response.json()

    if not data.get("photos"):
        return {"error": "No images found"}

    photo = data["photos"][0]

    return {
        "media_type": "image",
        "image_url": photo["src"]["large"],
        "photographer": photo["photographer"],
        "source": "pexels"
    }

# --------------------------------------------------
# VIDEO GENERATION (Example Structure)
# Replace URL with your real video API
# --------------------------------------------------
# @app.post("/generate-video")
# def generate_video(payload: MediaRequest):

#     if payload.type != "video":
#         raise HTTPException(status_code=400, detail="Only video type supported")

#     headers = {
#         "Authorization": f"Bearer {VIDEO_API_KEY}"
#     }

#     body = {
#         "prompt": payload.prompt
#     }

#     response = requests.post(
#         "https://your-video-api.com/generate",
#         headers=headers,
#         json=body,
#         timeout=20
#     )

#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="Video API failed")

#     return response.json()

