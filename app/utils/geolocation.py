import httpx
from app.core.config import settings

async def geocode_address(address: str) -> tuple[float, float]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "address": address,
                "key": settings.GOOGLE_MAPS_API_KEY
            }
        )
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        raise ValueError("Geocoding failed")
