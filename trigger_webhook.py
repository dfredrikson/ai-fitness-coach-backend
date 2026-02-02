
import requests
import json

payload = {
    "object_type": "activity",
    "object_id": 9876543210,  # Random new activity ID
    "aspect_type": "create",
    "owner_id": 131295617,    # Valid User ID from DB
    "subscription_id": 1,
    "event_time": 1234567890
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/webhooks/strava",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
