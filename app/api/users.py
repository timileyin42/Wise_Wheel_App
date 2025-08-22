from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from cloudinary.uploader import upload
from app.core.config import settings
from app.crud.user import UserCRUD
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_current_user
from app.db.session import get_db
from app.utils.cloudinary import upload_profile_image
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

# Create CRUD instance
user_crud = UserCRUD(User)

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user profile"""
    # Get the actual user object from database
    db_user = await user_crud.get_by_email(db, current_user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update the user
    updated_user = await user_crud.update(db, db_user, user_data)
    return UserResponse.model_validate(updated_user)


@router.post("/me/upload-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload profile photo to Cloudinary using the utility function"""
    try:
        print(f" Upload request from user: {current_user.email}")
        print(f" File info: {file.filename}, {file.content_type}, {file.size} bytes")
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type: {file.content_type}. Only JPEG, PNG, and WebP are allowed."
            )
        
        # Validate file size (5MB limit)
        if file.size and file.size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum 5MB allowed."
            )
        
        print(f" Uploading to Cloudinary...")
        # Use the user's ID as the public_id
        image_url = await upload_profile_image(file, public_id=f"user_{current_user.id}")
        print(f" Upload successful: {image_url}")
        
        # Update user's profile image in database
        db_user = await user_crud.get_by_email(db, current_user.email)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f" Updating user profile image in database...")
        # Update the profile image URL
        updated_user = await user_crud.update(db, db_user, {"profile_image": image_url})
        print(f" Database update successful")
        
        return JSONResponse(content={
            "url": image_url,
            "message": "Profile photo uploaded successfully"
        })
    except HTTPException as e:
        print(f" HTTP Exception: {e.detail}")
        raise
    except Exception as e:
        print(f" Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
