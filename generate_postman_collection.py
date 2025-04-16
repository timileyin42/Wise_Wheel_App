import json

endpoints = [
    ("POST", "/api/auth/register", "Register"),
    ("POST", "/api/auth/token", "Login"),
    ("GET", "/api/auth/google", "Google Auth"),
    ("GET", "/api/auth/google/callback", "Google Auth Callback"),
    ("GET", "/api/auth/verify-email/{token}", "Verify Email"),
    ("GET", "/api/cars/", "Search Cars"),
    ("POST", "/api/cars/", "Create Car"),
    ("POST", "/api/cars/{car_id}/upload", "Upload Car Image"),
    ("POST", "/api/bookings/", "Create Booking"),
    ("GET", "/api/bookings/me", "Get My Bookings"),
    ("POST", "/api/payments/initialize", "Initialize Payment"),
    ("POST", "/api/payments/webhook", "Payment Webhook"),
    ("GET", "/api/users/me", "Get Current User Profile"),
    ("PATCH", "/api/users/me", "Update Profile"),
    ("POST", "/api/users/me/upload-photo", "Upload Profile Photo"),
    ("GET", "/api/admin/admin/users", "List Users"),
    ("DELETE", "/api/admin/admin/cars/{car_id}", "Delete Car"),
    ("GET", "/api/admin/admin/bookings", "Get All Bookings"),
    ("GET", "/health", "Health Check")
]

collection = {
    "info": {
        "name": "Car Rental API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": []
}

for method, url, name in endpoints:
    collection["item"].append({
        "name": name,
        "request": {
            "method": method,
            "header": [],
            "url": {
                "raw": f"http://localhost:8000{url}",
                "host": ["localhost"],
                "port": "8000",
                "path": url.lstrip("/").split("/")
            }
        }
    })

with open("car_rental_api_collection.json", "w") as f:
    json.dump(collection, f, indent=2)

