#!/usr/bin/env python3
"""Test booking/reservation endpoints"""
import sys
from bondsports_api import BondSportsAPI, FACILITIES
from datetime import datetime

email = "name@example.com"
password = "yourpassword"

api = BondSportsAPI()
api.login(email, password)

facility = FACILITIES['wall-street']
date = "2026-02-15"

# Try booking/reservation related endpoints
endpoints = [
    f"/v4/bookings",
    f"/v4/bookings/search",
    f"/v4/schedules",
    f"/v4/schedules/availability",
    f"/v1/bookings",
    f"/v1/bookings/search",
    f"/v1/schedules",
]

for endpoint in endpoints:
    try:
        url = f"{api.base_url}{endpoint}"
        params = {
            'startDate': date,
            'endDate': date,
            'organizationId': facility['organizationId'],
            'facilityId': facility['facilityId']
        }
        response = api.session.get(url, params=params, headers=api._get_headers())
        print(f"{response.status_code}: {endpoint}")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ SUCCESS! Keys: {list(data.keys())}")
            sys.exit(0)
    except Exception as e:
        pass

print("\nLet me try POST requests for bookings:")

for endpoint in ["/v4/bookings/search", "/v4/bookings/availability"]:
    try:
        url = f"{api.base_url}{endpoint}"
        payload = {
            'startDate': date,
            'endDate': date,
            'organizationId': facility['organizationId'],
            'facilityId': facility['facilityId']
        }
        response = api.session.post(url, json=payload, headers=api._get_headers())
        print(f"{response.status_code}: POST {endpoint}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"  ✓ SUCCESS! Keys: {list(data.keys())}")
            sys.exit(0)
    except Exception as e:
        pass
