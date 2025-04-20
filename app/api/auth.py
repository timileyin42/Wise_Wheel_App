from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    create_access_token, 
    oauth, 
    get_password_hash,
    decode_access_token,
    verify_access_token
)
from app.core.email import send_mailjet_email
from app.crud.user import UserCRUD
from app.schemas.user import UserResponse, UserCreate, UserGoogleCreate
from app.schemas.token import Token
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm
from app.db.session import get_db
from datetime import timedelta

router = APIRouter(tags=["Authentication"])

@router.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Register new user with email/password"""
    if await UserCRUD.get_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await UserCRUD.create(db, {
        **user_data.dict(exclude={"password"}),
        "hashed_password": get_password_hash(user_data.password)
    })

    # Create verification token
    verification_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(days=1)
    )
    
    # In production, send email instead of returning token
    return {
        "user": user,
        "verification_token": verification_token
    }

@router.post("/auth/token", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Email/password login"""
    user = await UserCRUD.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    access_token = create_access_token(data={"sub": user.email})

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        secure=not settings.DEBUG,  # Secure in production
        samesite='lax'
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/auth/google")
async def google_auth(request: Request):
    """Initiate Google OAuth flow"""
    redirect_uri = request.url_for("google_auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback", response_model=Token)
async def google_auth_callback(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo")
        
        if not userinfo or not userinfo.get("email"):
            raise HTTPException(status_code=400, detail="Invalid OAuth response")

        user = await UserCRUD.get_or_create_google_user(db, userinfo)
        access_token = create_access_token(data={"sub": user.email})

        # Set cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=1800,
            secure=not settings.DEBUG,
            samesite='lax'
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/auth/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify email with token"""
    payload = verify_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=400, detail="Invalid token")

    user = await UserCRUD.verify_email(db, payload["sub"])
    return {"message": "Email verified successfully"}


@router.post("/auth/forgot-password")
async def forgot_password(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Initiate password reset process"""
    user = await UserCRUD.get_by_email(db, request_data.email)
    if not user:
        # Don't reveal if user doesn't exist
        return {"message": "If this email exists, a reset link has been sent"}

    reset_token = create_password_reset_token(user.email)

    # In production, send email in background
    if not settings.DEBUG:
        background_tasks.add_task(
            send_password_reset_email,
            email=user.email,
            token=reset_token
        )
    else:
        # For development, return the token
        return {"reset_token": reset_token}

    return {"message": "If this email exists, a reset link has been sent"}

@router.post("/auth/reset-password")
async def reset_password(
    request_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Complete password reset process"""
    email = verify_password_reset_token(request_data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = await UserCRUD.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password
    hashed_password = get_password_hash(request_data.new_password)
    await UserCRUD.update(db, user.id, {"hashed_password": hashed_password})

    return {"message": "Password updated successfully"}
