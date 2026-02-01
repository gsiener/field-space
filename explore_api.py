#!/usr/bin/env python3
"""Explore BondSports API to find available endpoints"""
from bondsports_api import BondSportsAPI

email = "name@example.com"
password = "yourpassword"

api = BondSportsAPI()
api.login(email, password)

# Try some discovery endpoints
discovery_urls = [
    f"{api.base_url}/",
    f"{api.base_url}/v1",
    f"{api.base_url}/v4",
    f"{api.base_url}/docs",
    f"{api.base_url}/api",
    f"{api.base_url}/swagger",
]

print("Trying discovery endpoints...")
for url in discovery_urls:
    try:
        response = api.session.get(url, headers=api._get_headers())
        print(f"{response.status_code}: {url}")
        if response.status_code == 200:
            print(f"  Content-Type: {response.headers.get('content-type')}")
            print(f"  Body length: {len(response.text)}")
    except Exception as e:
        print(f"Error on {url}: {str(e)[:50]}")
        
print("\n\nBased on what we know works, let me try similar patterns to the resources endpoint...")

# The resources endpoint works with this pattern:
# /v4/resources/organization/{orgId}/facility/{facilityId}/resources
# Maybe there's a similar pattern for something else?

test_endpoints = [
    "/v4/bookings/organization/450/facility/502/bookings",
    "/v4/slots/organization/450/facility/502/slots",
    "/v4/availability/organization/450/facility/502/slots",
    "/v4/schedule/organization/450/facility/502/schedule",
]

for endpoint in test_endpoints:
    try:
        url = f"{api.base_url}{endpoint}"
        params = {'startDate': '2026-02-15', 'endDate': '2026-02-15'}
        response = api.session.get(url, params=params, headers=api._get_headers())
        print(f"{response.status_code}: {endpoint}")
        if response.status_code not in [404]:
            print(f"  ⚠ Interesting! Not a 404")
    except Exception as e:
        pass
