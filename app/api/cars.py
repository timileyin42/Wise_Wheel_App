from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.car import CarCRUD
from app.schemas.car import CarResponse, CarCreate
from app.schemas.user import UserResponse
from app.core.security import get_current_user
from app.db.session import get_db
from app.utils.geolocation import geocode_address
from app.utils.cloudinary import upload_car_image
from datetime import datetime

router = APIRouter(prefix="/cars", tags=["Cars"])

async def get_car_or_404(db: AsyncSession, car_id: str):
    """Helper function to get car or raise 404"""
    car = await CarCRUD().get(db, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@router.get("/", response_model=list[CarResponse])
async def search_cars(
    make: str | None = Query(None),
    model: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Search available cars with filters"""
    return await CarCRUD().search_available(
        db,
        make=make,
        model=model,
        min_price=min_price,
        max_price=max_price,
        latitude=latitude,
        longitude=longitude
    )

@router.post("/", response_model=CarResponse)
async def create_car(
    car_data: CarCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create new car listing (Admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    lat, lng = await geocode_address(car_data.address)
    car_data_dict = car_data.dict()
    car_data_dict.update({"latitude": lat, "longitude": lng})
    return await CarCRUD().create(db, car_data_dict)

@router.get("/{car_id}/availability")
async def get_car_availability(
    car_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get car availability with optional date range filtering
    Returns periods with status (available/booked)
    """
    car = await get_car_or_404(db, car_id)
    
    # Default to next 30 days if no dates provided
    if not start_date:
        start_date = datetime.utcnow()
    if not end_date:
        end_date = start_date + timedelta(days=30)
    
    # Get conflicting bookings
    bookings = await db.execute(
        select(Booking)
        .where(Booking.car_id == car_id)
        .where(Booking.status == "confirmed")
        .where(
            or_(
                and_(
                    Booking.start_date <= end_date,
                    Booking.end_date >= start_date
                ),
                Booking.end_date == None  # For open-ended bookings
            )
        )
    )
    bookings = bookings.scalars().all()
    
    # Generate availability periods
    availability = []
    current_date = start_date
    
    while current_date < end_date:
        period_end = current_date + timedelta(days=1)
        is_available = True
        
        for booking in bookings:
            if (booking.start_date <= period_end and 
                (booking.end_date is None or booking.end_date >= current_date)):
                is_available = False
                break
        
        availability.append({
            "start_date": current_date,
            "end_date": period_end,
            "status": "available" if is_available else "booked"
        })
        
        current_date = period_end
    
    return availability

@router.post("/{car_id}/upload")
async def upload_car_image(
    car_id: str,
    file: UploadFile = File(...),
    public_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload image for specific car"""
    car = await get_car_or_404(db, car_id)
    image_url = await upload_car_image(file, public_id=public_id)
    # Update car with new image URL
    return {"url": image_url}
