from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.booking import BookingCRUD
from app.schemas.user import UserResponse
from app.schemas.booking import BookingResponse, BookingCreate
from app.core.security import get_current_user
from app.db.session import get_db

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create new booking"""
    try:
        return await BookingCRUD.create_with_payment(
            db, booking_data, current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=list[BookingResponse])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user's bookings"""
    return await BookingCRUD.get_user_bookings(db, current_user.id)
