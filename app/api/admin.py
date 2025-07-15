from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_admin
from app.crud.user import UserCRUD
from app.crud.car import CarCRUD
from app.crud.booking import BookingCRUD
from app.models.user import User
from app.models.car import Car
from app.models.booking import Booking
from app.schemas import UserResponse, CarResponse, BookingResponse
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin)
):
    """List all users (Admin only)"""
    user_crud = UserCRUD(User)
    return await user_crud.get_multi(db, skip=skip, limit=limit)

@router.delete("/cars/{car_id}")
async def delete_car(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin)
):
    """Delete a car listing (Admin only)"""
    car_crud = CarCRUD(Car)
    return await car_crud.remove(db, id=car_id)

@router.get("/bookings", response_model=list[BookingResponse])
async def get_all_bookings(
    db: AsyncSession = Depends(get_db),
    admin: UserResponse = Depends(get_current_admin)
):
    """Get all bookings (Admin only)"""
    booking_crud = BookingCRUD(Booking)
    return await booking_crud.get_multi(db)
