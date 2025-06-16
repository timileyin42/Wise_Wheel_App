from typing import Any, Generic, TypeVar, Type
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import UUIDBase

ModelType = TypeVar("ModelType", bound=UUIDBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations"""
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: str) -> ModelType | None:
        """Get single record by ID"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        """Create new record"""
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)  # Handle dictionary input
        else:
            db_obj = self.model(**obj_in.dict(exclude_unset=True))  # Handle Pydantic model

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update existing record"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> ModelType:
        """Delete record by ID"""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        db_obj = result.scalar_one()
        await db.delete(db_obj)
        await db.commit()
        return db_obj
