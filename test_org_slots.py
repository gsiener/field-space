#!/usr/bin/env python3
"""Test organization-level slots endpoints"""
import sys
from bondsports_api import BondSportsAPI, FACILITIES

email = "name@example.com"
password = "yourpassword"

api = BondSportsAPI()
api.login(email, password)

facility = FACILITIES['wall-street']
date = "2026-02-15"

# Get resource IDs
resources_resp = api.get_facility_resources(facility['organizationId'], facility['facilityId'])
resource_ids = [r['id'] for r in resources_resp.get('data', [])]

print(f"Testing with {len(resource_ids)} resources")

# Try organization slots endpoint
print(f"\n1. Testing /v1/organizations/{facility['organizationId']}/slots")
try:
    slots = api.get_organization_slots(facility['organizationId'], date, date)
    print(f"✓ SUCCESS! Got response with keys: {list(slots.keys())}")
    print(f"  Data: {slots.get('data', [])[:2]}")  # Show first 2 items
except Exception as e:
    print(f"✗ Failed: {e}")

# Try space-specific slots endpoints
print(f"\n2. Testing /v1/organizations/{facility['organizationId']}/spaces/{{spaceId}}/slots")
for resource_id in resource_ids[:3]:  # Test first 3 resources
    try:
        slots = api.get_space_slots(facility['organizationId'], resource_id, date, date)
        print(f"✓ SUCCESS for resource {resource_id}! Keys: {list(slots.keys())}")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Resource {resource_id}: {str(e)[:60]}")
