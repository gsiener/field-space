#!/usr/bin/env python3
"""Test different slots endpoint variations"""
import sys
from bondsports_api import BondSportsAPI, FACILITIES

email = "name@example.com"
password = "yourpassword"

api = BondSportsAPI()
api.login(email, password)

facility = FACILITIES['wall-street']
date = "2026-02-15"

# Try different endpoint patterns
endpoints = [
    f"/v1/venues/{facility['facilityId']}/slots",
    f"/v4/venues/{facility['facilityId']}/slots",
    f"/v1/facilities/{facility['facilityId']}/slots",
    f"/v4/facilities/{facility['facilityId']}/slots",
    f"/v1/organizations/{facility['organizationId']}/venues/{facility['facilityId']}/slots",
    f"/v4/organizations/{facility['organizationId']}/venues/{facility['facilityId']}/slots",
    f"/v4/bookings/slots",
    f"/v1/bookings/availability",
    f"/v4/bookings/availability",
]

for endpoint in endpoints:
    try:
        url = f"{api.base_url}{endpoint}"
        params = {'startDate': date, 'endDate': date}
        response = api.session.get(url, params=params, headers=api._get_headers())
        if response.status_code == 200:
            print(f"✓ SUCCESS: {endpoint}")
            data = response.json()
            print(f"  Keys: {list(data.keys())}")
            sys.exit(0)
        else:
            print(f"✗ {response.status_code}: {endpoint}")
    except Exception as e:
        print(f"✗ ERROR: {endpoint} - {str(e)[:50]}")

print("\nNone of the endpoints worked.")
