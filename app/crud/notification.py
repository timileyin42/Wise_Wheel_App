from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.notification import Notification

class NotificationCRUD:
    def __init__(self, model):
        self.model = model

    async def get_user_notifications(self, db: AsyncSession, user_id: str):
        result = await db.execute(select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc()))
        return result.scalars().all()

    async def mark_all_read(self, db: AsyncSession, user_id: str):
        await db.execute(update(self.model).where(self.model.user_id == user_id).values(is_read=True))
        await db.commit()

    async def delete_user_notification(self, db: AsyncSession, notification_id: str, user_id: str):
        result = await db.execute(select(self.model).where(self.model.id == notification_id, self.model.user_id == user_id))
        notification = result.scalar_one_or_none()
        if not notification:
            return False
        await db.delete(notification)
        await db.commit()
        return True
