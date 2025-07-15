from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.crud.notification import NotificationCRUD

router = APIRouter(prefix="/notifications", tags=["Notifications"])

notification_crud = NotificationCRUD(Notification)

@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Fetch all notifications for the logged-in user"""
    return await notification_crud.get_user_notifications(db, current_user.id)

@router.post("/read")
async def mark_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Mark all notifications as read for the logged-in user"""
    await notification_crud.mark_all_read(db, current_user.id)
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a notification by ID for the logged-in user"""
    deleted = await notification_crud.delete_user_notification(db, notification_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}
