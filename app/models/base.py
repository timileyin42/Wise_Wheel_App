import uuid
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, DateTime, func
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID

class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime, 
            default=func.now(), 
            onupdate=func.now(), 
            nullable=False
        )

class UUIDBase(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
