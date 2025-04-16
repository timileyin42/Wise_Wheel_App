import httpx
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.background import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.crud.booking import BookingCRUD
from app.schemas.user import UserResponse
from app.schemas.payment import PaymentResponse
from app.db.session import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/initialize", response_model=PaymentResponse)
async def initialize_payment(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Initialize Paystack payment"""
    booking = await BookingCRUD.get(db, booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.paystack.co/transaction/initialize",
            headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
            json={
                "email": current_user.email,
                "amount": int(booking.total_amount * 100),
                "reference": f"BOOKING_{booking_id}",
                "callback_url": f"{settings.BASE_URL}/payments/verify/{booking_id}"
            }
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Payment initialization failed")
    
    return response.json()

@router.post("/webhook")
async def payment_webhook(
    background_tasks: BackgroundTasks,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Paystack payment webhook"""
    # Verify signature
    signature = request.headers.get("x-paystack-signature")
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        await request.body(),
        hashlib.sha512
    ).hexdigest()
    
    if signature != computed_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    if payload["event"] == "charge.success":
        booking_id = payload["data"]["reference"].split("_")[-1]
        background_tasks.add_task(
            BookingCRUD.confirm_payment,
            db,
            booking_id,
            payload["data"]["id"]
        )
    
    return {"status": "ok"}
