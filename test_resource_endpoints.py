#!/usr/bin/env python3
"""Test resource-based availability endpoints"""
import sys
from bondsports_api import BondSportsAPI, FACILITIES

email = "name@example.com"
password = "yourpassword"

api = BondSportsAPI()
api.login(email, password)

facility = FACILITIES['wall-street']
date = "2026-02-15"

# Get resource IDs first
resources_resp = api.get_facility_resources(facility['organizationId'], facility['facilityId'])
resource_ids = [r['id'] for r in resources_resp.get('data', [])][:2]  # Just test first 2

print(f"Testing with resource IDs: {resource_ids}")

# Try resource-based endpoints
endpoints = [
    f"/v4/resources/availability",
    f"/v4/resources/organization/{facility['organizationId']}/facility/{facility['facilityId']}/availability",
    f"/v4/bookings/organization/{facility['organizationId']}/facility/{facility['facilityId']}/slots",
    f"/v4/bookings/organization/{facility['organizationId']}/availability",
]

for endpoint in endpoints:
    for resource_id in resource_ids:
        try:
            url = f"{api.base_url}{endpoint}"
            params = {
                'startDate': date,
                'endDate': date,
                'resourceId': resource_id,
                'organizationId': facility['organizationId'],
                'facilityId': facility['facilityId']
            }
            response = api.session.get(url, params=params, headers=api._get_headers())
            if response.status_code == 200:
                print(f"✓ SUCCESS: {endpoint}")
                print(f"  Params: {params}")
                data = response.json()
                print(f"  Keys: {list(data.keys())}")
                sys.exit(0)
            elif response.status_code != 404:
                print(f"⚠ {response.status_code}: {endpoint} (resource {resource_id})")
        except Exception as e:
            error_str = str(e)[:80]
            if '404' not in error_str:
                print(f"✗ ERROR: {endpoint} - {error_str}")

print("\nNo success with resource-based endpoints.")
