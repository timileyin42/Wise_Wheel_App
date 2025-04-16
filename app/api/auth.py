from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, oauth, get_current_user
from app.core.email import send_mailjet_email
from app.crud.user import UserCRUD
from app.schemas.user import UserResponse, UserCreate, UserGoogleCreate
from app.schemas.token import Token, TokenPayload
from app.db.session import get_db

router = APIRouter(tags=["Authentication"])

@router.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Register new user with email/password"""
    if await UserCRUD.get_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    db_user = await UserCRUD.create(db, {
        **user_data.dict(exclude={"password"}),
        "hashed_password": hashed_password
    })
    
    # Send verification email
    verification_token = create_access_token({"sub": db_user.email})
    await send_mailjet_email(
        to_email=db_user.email,
        subject="Verify Your Email",
        template_name="email/verify_email.html",
        context={"verification_url": f"/auth/verify-email/{verification_token}"},
        background_tasks=background_tasks
    )
    
    return db_user

@router.post("/auth/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Email/password login"""
    user = await UserCRUD.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )
    return {
        "access_token": create_access_token({"sub": user.email}),
        "token_type": "bearer"
    }

@router.get("/auth/google")
async def google_auth(request: Request):
    """Initiate Google OAuth2 flow"""
    redirect_uri = request.url_for("google_auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/google/callback", response_model=Token)
async def google_auth_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Google OAuth2 callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        
        if not user_info or not user_info.get("email"):
            raise HTTPException(status_code=400, detail="Invalid OAuth response")
        
        user = await UserCRUD.get_by_google_id(db, user_info["sub"]) or \
               await UserCRUD.create_with_google(db, UserGoogleCreate(**user_info))
        
        return {
            "access_token": create_access_token({"sub": user.email}),
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/auth/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify email address"""
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user = await UserCRUD.get_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await UserCRUD.mark_verified(db, user)
    return {"message": "Email verified successfully"}
