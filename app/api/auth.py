from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    create_password_reset_token,
    verify_password_reset_token,
    verify_access_token
)
from app.core.config import settings
from app.core.email import send_password_reset_email
from app.models.user import User
from app.crud.user import UserCRUD
from app.schemas.user import UserResponse, UserCreate
from app.schemas.token import Token
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm
from app.db.session import get_db
from datetime import timedelta

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Register new user with email/password"""
    user_crud = UserCRUD(User)
    if await user_crud.get_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Prepare user data
    user_dict = {
        "email": user_data.email,
        "phone": user_data.phone,
        "hashed_password": get_password_hash(user_data.password),
        "is_verified": False,
        "is_active": True,
        "role": "user"
    }

    user = await user_crud.create(db, user_dict)

    # Create verification token
    verification_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(days=1)
    )

    # Set cookie
    response.set_cookie(
        key="verification_token",
        value=verification_token,
        httponly=True,
        max_age=86400,
        secure=not settings.DEBUG,
        samesite='lax'
    )

    # Always return token in development
    if settings.ENVIRONMENT == "development":
        return {
            "user": UserResponse.model_validate(user),
            "verification_token": verification_token,
            "message": "Development mode: Verification token returned"
        }
    
    # In production: Send email
    await send_mailjet_email(
        to_email=user.email,
        subject="Verify your email",
        template_name="email_verification",
        context={"verification_token": verification_token},
        background_tasks=background_tasks
    )
    
    return {"message": "Registration successful. Check your email for verification."}

@router.post("/token", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Email/password login"""
    user_crud = UserCRUD(User)
    user = await user_crud.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    access_token = create_access_token(data={"sub": user.email})

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        secure=not settings.DEBUG,
        samesite='lax'
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify email with token"""
    try:
        # Verify token and get email
        payload = verify_access_token(token)
        if not payload or not payload.get("sub"):
            raise HTTPException(status_code=400, detail="Invalid token")
        
        email = payload["sub"]
        
        # Get user
        user_crud = UserCRUD(User)
        user = await user_crud.get_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_verified:
            return {"message": "Email already verified"}
        
        # Mark as verified
        await user_crud.mark_verified(db, user)
        
        return {"message": "Email verified successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying email: {str(e)}"
        )

@router.post("/forgot-password")
async def forgot_password(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Initiate password reset process"""
    user_crud = UserCRUD(User)
    user = await user_crud.get_by_email(db, request_data.email)
    if user:
        reset_token = create_password_reset_token(user.email)
        if not settings.DEBUG:
            background_tasks.add_task(
                send_password_reset_email,
                email=user.email,
                token=reset_token
            )
        else:
            return {"reset_token": reset_token}
    
    return {"message": "If this email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    request_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Complete password reset process"""
    email = verify_password_reset_token(request_data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_crud = UserCRUD(User)
    user = await user_crud.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user_crud.update_password(db, user.id, request_data.new_password)
    return {"message": "Password updated successfully"}
