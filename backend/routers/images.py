from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import requests
from pathlib import Path

router = APIRouter(
    prefix="/images",
    tags=["images"],
)

IMAGE_DIR = Path("data/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/thumbnails/{filename}")
async def get_thumbnail(filename: str):
    # Sanitize filename to prevent directory traversal
    filename = os.path.basename(filename)
    local_path = IMAGE_DIR / filename
    
    # If file exists locally, serve it
    if local_path.exists():
        return FileResponse(local_path)
    
    # If not, try to download it from Efarmz
    # Expected filename format: v804.jpg
    # Efarmz URL: https://cdn.efarmz.be/cdn-cgi/image/quality=75,f=auto,width=384/https://cdn.efarmz.be/art/v804.jpg
    
    name_without_ext = os.path.splitext(filename)[0]
    cdn_url = f"https://cdn.efarmz.be/cdn-cgi/image/quality=75,f=auto,width=384/https://cdn.efarmz.be/art/{name_without_ext}.jpg"
    
    try:
        response = requests.get(cdn_url, timeout=10)
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            return FileResponse(local_path)
        else:
            # If CDN returns 404 or other error, we can't serve the image
            raise HTTPException(status_code=404, detail="Image not found on CDN")
    except Exception as e:
        print(f"Error downloading image: {e}")
        raise HTTPException(status_code=500, detail="Failed to download image")
