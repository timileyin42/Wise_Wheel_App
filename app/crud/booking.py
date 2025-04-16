from datetime import datetime, timedelta
from sqlalchemy import select, and_
from app.models.booking import Booking
from app.models.car import Car
from app.schemas.booking import BookingCreate
from app.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession

class BookingCRUD(CRUDBase[Booking, BookingCreate, BookingCreate]):
    """CRUD operations for Booking model with business logic"""
    
    async def create_with_payment(
        self,
        db: AsyncSession,
        obj_in: BookingCreate,
        user_id: str
    ) -> Booking:
        """Create booking with payment validation"""
        # Check car availability
        car = await db.get(Car, obj_in.car_id)
        if not car or not car.is_available:
            raise ValueError("Car not available for booking")
        
        # Check date conflicts
        existing = await db.execute(
            select(Booking).filter(
                and_(
                    Booking.car_id == obj_in.car_id,
                    Booking.start_date <= obj_in.end_date,
                    Booking.end_date >= obj_in.start_date
                )
            )
        )
        if existing.scalars().first():
            raise ValueError("Booking dates conflict with existing reservation")
        
        # Calculate total price
        days = (obj_in.end_date - obj_in.start_date).days
        total = days * car.daily_rate
        
        # Create booking record
        booking_data = obj_in.dict()
        booking_data.update({
            "user_id": user_id,
            "total_amount": total
        })
        return await super().create(db, booking_data)

    async def confirm_payment(
        self,
        db: AsyncSession,
        booking_id: str,
        payment_reference: str
    ) -> Booking:
        """Mark booking as paid"""
        booking = await self.get(db, booking_id)
        if not booking:
            raise ValueError("Booking not found")
        
        booking.payment_status = True
        booking.payment_reference = payment_reference
        db.add(booking)
        await db.commit()
        return booking
