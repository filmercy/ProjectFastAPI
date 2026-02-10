"""Check maintenance records for favorite racket"""
import requests
import json

racket_id = "c46f7f29-4531-41c7-9bd7-1ad01be93a49"
url = f"http://localhost:8000/api/v1/maintenance/?client_racket_id={racket_id}"

response = requests.get(url)
data = response.json()

print(f"Total maintenance records for your favorite racket: {data['total']}\n")

for i, record in enumerate(data['items'], 1):
    print(f"Record {i}:")
    print(f"  Service: {record['service_type']}")
    print(f"  Cost: ${record['service_cost']}")
    print(f"  Date: {record['service_date']}")
    print(f"  Tension: {record['main_tension_kg']}kg (mains) / {record['cross_tension_kg']}kg (crosses)")
    print(f"  Pattern: {record['string_pattern']}")
    print(f"  Duration: {record['duration_minutes']} minutes")
    print(f"  Notes: {record['notes']}")
    print(f"  Next service due: {record['next_service_due_date']}")
    print()
