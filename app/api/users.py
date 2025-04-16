from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from cloudinary.uploader import upload
from app.core.config import settings
from app.crud.user import UserCRUD
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_current_user
from app.db.session import get_db
from app.utils.cloudinary import upload_profile_image

router = APIRouter(prefix="/users", tags=["Users"])

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
    return await UserCRUD.update(db, current_user, user_data)


@router.post("/me/upload-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Upload profile photo to Cloudinary using the utility function"""
    try:
        # Use the user's ID as the public_id
        image_url = await upload_profile_image(file, public_id=f"user_{current_user.id}")
        return JSONResponse(content={"url": image_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
