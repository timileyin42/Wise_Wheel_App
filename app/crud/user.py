from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserGoogleCreate, UserUpdate
from app.crud.base import CRUDBase

class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model with auth extensions"""

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email address"""
        result = await db.execute(
            select(User).filter(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_google_id(self, db: AsyncSession, google_id: str) -> User | None:
        """Get user by Google OAuth2 ID"""
        result = await db.execute(
            select(User).filter(User.google_id == google_id)
        )
        return result.scalar_one_or_none()

    async def create_with_google(self, db: AsyncSession, obj_in: UserGoogleCreate) -> User:
        """Create user from Google OAuth2 data"""
        user_data = obj_in.dict()
        user_data.update({
            "is_verified": True,
            "google_id": user_data.pop("google_id")
        })
        return await super().create(db, user_data)

    async def authenticate(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> User | None:
        """Authenticate user with email/password"""
        user = await self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_last_login(self, db: AsyncSession, user: User) -> User:
        """Update user's last login timestamp"""
        user.last_login = datetime.utcnow()
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def mark_verified(self, db: AsyncSession, user: User) -> User:
        """Mark user email as verified"""
        user.is_verified = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update_password(
        self,
        db: AsyncSession,
        user_id: int,
        new_password: str
    ) -> User:
        """Update user password"""
        hashed_password = get_password_hash(new_password)
        result = await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(hashed_password=hashed_password)
        )
        await db.commit()
        
        # Refresh and return updated user
        user = await self.get(db, user_id)
        await db.refresh(user)
        return user
