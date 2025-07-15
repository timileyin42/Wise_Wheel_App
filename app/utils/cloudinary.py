import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from pathlib import Path
import logging
from typing import Optional

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

async def upload_to_folder(file: UploadFile, folder: str, public_id: Optional[str] = None) -> str:
    """Upload file to specific Cloudinary folder with validation"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if file.content_type not in allowed_types:
            raise HTTPException(400, f"Invalid file type: {file.content_type}. Only JPEG/PNG/WEBP allowed")

        # Reset file position to beginning
        await file.seek(0)
        
        # Read file content
        file_content = await file.read()
        
        # Reset file position back to beginning for potential future reads
        await file.seek(0)

        # Upload to Cloudinary with folder organization
        result = cloudinary.uploader.upload(
            file_content,  # Use file content instead of file.file
            folder=f"wisewheels/{folder}",
            public_id=public_id,  # Use the provided public_id
            use_filename=True,
            unique_filename=True if not public_id else False,  # Disable unique_filename if public_id is provided
            overwrite=True if public_id else False,  # Overwrite if public_id is provided
            resource_type="auto"
        )
        return result.get("secure_url")

    except Exception as e:
        logging.error(f"Cloudinary upload error: {str(e)}")
        raise HTTPException(500, "File upload failed") from e

# Specific upload functions
async def upload_car_image(file: UploadFile, public_id: Optional[str] = None) -> str:
    return await upload_to_folder(file, "cars", public_id=public_id)

async def upload_profile_image(file: UploadFile, public_id: Optional[str] = None) -> str:
    return await upload_to_folder(file, "profiles", public_id=public_id)
