from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import requests
from pathlib import Path
import logging

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["images"],
)

IMAGE_DIR = Path("data/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/thumbnails/{filename}")
async def get_thumbnail(filename: str):
    logger.info(f"Thumbnail request received for: {filename}")
    
    # Sanitize filename to prevent directory traversal
    filename = os.path.basename(filename)
    local_path = IMAGE_DIR / filename
    logger.info(f"Sanitized filename: {filename}, local path: {local_path}")
    
    # If file exists locally, serve it
    if local_path.exists():
        logger.info(f"Cache hit - serving from local storage: {local_path}")
        return FileResponse(local_path, media_type="image/jpeg")
    
    logger.info(f"Cache miss - file not found locally: {local_path}")
    
    # If not, try to download it from Efarmz
    # Expected filename format: v804.jpg
    # Efarmz URL: https://cdn.efarmz.be/cdn-cgi/image/quality=75,f=auto,width=384/https://cdn.efarmz.be/art/v804.jpg
    
    name_without_ext = os.path.splitext(filename)[0]
    cdn_url = f"https://cdn.efarmz.be/cdn-cgi/image/quality=75,f=auto,width=384/https://cdn.efarmz.be/art/{name_without_ext}.jpg"
    logger.info(f"Attempting to download from CDN: {cdn_url}")
    
    try:
        response = requests.get(cdn_url, timeout=10)
        logger.info(f"CDN response status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"Successfully downloaded image, saving to: {local_path}")
            with open(local_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Image saved successfully, size: {len(response.content)} bytes")
            return FileResponse(local_path, media_type="image/jpeg")
        else:
            # If CDN returns 404 or other error, we can't serve the image
            logger.warning(f"CDN returned error status {response.status_code} for {cdn_url}")
            raise HTTPException(status_code=404, detail="Image not found on CDN")
    except requests.RequestException as e:
        logger.error(f"Network error downloading image from {cdn_url}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download image")
    except Exception as e:
        logger.error(f"Unexpected error processing thumbnail {filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process image")
