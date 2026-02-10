"""Script to add a maintenance record for Filippo's favorite racket"""
import requests
import json

url = "http://localhost:8000/api/v1/maintenance/"

# Maintenance data for the favorite racket
data = {
    "client_racket_id": "c46f7f29-4531-41c7-9bd7-1ad01be93a49",
    "service_type": "stringing",
    "service_cost": 25.00,
    "main_tension_kg": 24.5,
    "cross_tension_kg": 23.0,
    "string_pattern": "16x19",
    "duration_minutes": 30,
    "notes": "First stringing service for my favorite racket!",
    "next_service_due_date": "2026-03-10"
}

print(f"Creating maintenance record at: {url}")
print(f"Data: {json.dumps(data, indent=2)}\n")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")

    if response.status_code in [200, 201]:
        print("\n✓ Maintenance record created successfully!")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n✗ Error creating maintenance record")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")
