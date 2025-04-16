from sqlalchemy import func, and_
from geoalchemy2.functions import ST_DWithin
from app.models.car import Car
from app.schemas.car import CarCreate
from app.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession

class CarCRUD(CRUDBase[Car, CarCreate, CarCreate]):
    """CRUD operations for Car model with geo capabilities"""
    
    async def search_available(
        self,
        db: AsyncSession,
        *,
        make: str | None = None,
        model: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_km: float = 10
    ) -> list[Car]:
        """Search available cars with filters"""
        query = select(Car).filter(Car.is_available == True)
        
        # Text filters
        if make:
            query = query.filter(Car.make.ilike(f"%{make}%"))
        if model:
            query = query.filter(Car.model.ilike(f"%{model}%"))
        
        # Price range
        if min_price and max_price:
            query = query.filter(Car.daily_rate.between(min_price, max_price))
        elif min_price:
            query = query.filter(Car.daily_rate >= min_price)
        elif max_price:
            query = query.filter(Car.daily_rate <= max_price)
        
        # Geo search
        if latitude and longitude:
            point = func.ST_MakePoint(longitude, latitude)
            query = query.filter(
                ST_DWithin(Car.location, point, radius_km * 1000)
            )
        
        result = await db.execute(query)
        return result.scalars().all()
