#!/usr/bin/env python3
"""
BondSports API Client

This module provides a Python client for the BondSports API, specifically
for checking availability at Socceroof facilities.

Discovered API Endpoints:
========================

PUBLIC ENDPOINTS (no authentication required):
- GET /v1/organizations/{orgId} - Organization info
- GET /v1/venues/{facilityId} - Facility/venue details with spaces list
- GET /v4/resources/{resourceId}?includeAdditionalData=true - Resource details with activity times
- GET /v4/resources/{resourceId}/packages-v1 - Pricing packages for a resource
- GET /v4/resources/organization/{orgId}/facility/{facilityId}/resources - List all resources
- GET /v4/organization/{orgId} - Organization data

AUTHENTICATED ENDPOINTS (require login):
- GET /v1/organizations/{orgId}/slots - Get booked slots
- GET /v1/organizations/{orgId}/spaces/{spaceId}/slots - Get slots for specific space
- GET /v1/organizations/{orgId}/schedule - Get schedule
- GET /v1/organizations/{orgId}/facilities - List facilities
- GET /v1/venues/{facilityId}/slots - Get slots for venue
- POST /auth - Login
- POST /auth/refresh - Refresh token
- POST /auth/logout - Logout

Socceroof Facilities:
====================
- Wall Street: facilityId=502, organizationId=450
- Crown Heights: facilityId=484, organizationId=436
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

BASE_URL = "https://api.bondsports.co"

# Socceroof facility configuration
FACILITIES = {
    'wall-street': {
        'facilityId': 502,
        'organizationId': 450,
        'name': 'Socceroof Wall Street',
        'url': 'https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450'
    },
    'crown-heights': {
        'facilityId': 484,
        'organizationId': 436,
        'name': 'Socceroof Crown Heights',
        'url': 'https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436'
    }
}

# Day of week mapping (BondSports uses 2=Monday, 8=Sunday)
DAY_OF_WEEK_MAP = {
    0: 'Sunday',
    1: 'Monday',
    2: 'Monday',
    3: 'Tuesday',
    4: 'Wednesday',
    5: 'Thursday',
    6: 'Friday',
    7: 'Saturday',
    8: 'Sunday'
}


class BondSportsAPI:
    """Client for the BondSports API."""

    def __init__(self, auth_token: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            auth_token: Optional authentication token for protected endpoints
        """
        self.base_url = BASE_URL
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def _get_headers(self) -> Dict[str, str]:
        """Get headers including auth token if available."""
        headers = {}
        if hasattr(self, 'access_token') and self.access_token:
            headers['x-bonduseraccesstoken'] = self.access_token
        if hasattr(self, 'id_token') and self.id_token:
            headers['x-bonduseridtoken'] = self.id_token
        if hasattr(self, 'username') and self.username:
            headers['x-bonduserusername'] = self.username
        # Backwards compatibility
        if self.auth_token and not hasattr(self, 'access_token'):
            headers['Authorization'] = f'Bearer {self.auth_token}'
        return headers

    def get_organization(self, org_id: int) -> Dict[str, Any]:
        """
        Get organization details.

        Args:
            org_id: Organization ID

        Returns:
            Organization data including branding, contact info, etc.
        """
        url = f"{self.base_url}/v1/organizations/{org_id}"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_facility(self, facility_id: int) -> Dict[str, Any]:
        """
        Get facility/venue details including all spaces.

        Args:
            facility_id: Facility/venue ID

        Returns:
            Facility data with spaces list
        """
        url = f"{self.base_url}/v1/venues/{facility_id}"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_resource(self, resource_id: int, include_additional: bool = True) -> Dict[str, Any]:
        """
        Get resource (space/field) details.

        Args:
            resource_id: Resource/space ID
            include_additional: Include activity times and other data

        Returns:
            Resource data with operating hours
        """
        url = f"{self.base_url}/v4/resources/{resource_id}"
        params = {}
        if include_additional:
            params['includeAdditionalData'] = 'true'
        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_resource_packages(self, resource_id: int) -> Dict[str, Any]:
        """
        Get pricing packages for a resource.

        Args:
            resource_id: Resource/space ID

        Returns:
            List of packages with pricing and availability times
        """
        url = f"{self.base_url}/v4/resources/{resource_id}/packages-v1"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_facility_resources(
        self,
        org_id: int,
        facility_id: int,
        resource_types: str = "space",
        include_activity_times: bool = True,
        include_metadata: bool = True,
        include_facilities: bool = True
    ) -> Dict[str, Any]:
        """
        Get all resources for a facility.

        Args:
            org_id: Organization ID
            facility_id: Facility ID
            resource_types: Type filter (e.g., "space")
            include_activity_times: Include operating hours
            include_metadata: Include resource metadata
            include_facilities: Include facility info

        Returns:
            List of resources with their data
        """
        url = f"{self.base_url}/v4/resources/organization/{org_id}/facility/{facility_id}/resources"
        params = {
            'resourceTypes': resource_types,
            'includeActivityTimes': str(include_activity_times).lower(),
            'includeResourceMetadata': str(include_metadata).lower(),
            'includeFacilities': str(include_facilities).lower()
        }
        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_operating_hours(self, resource_id: int) -> List[Dict[str, Any]]:
        """
        Get operating hours for a resource.

        Args:
            resource_id: Resource/space ID

        Returns:
            List of operating hours by day of week
        """
        data = self.get_resource(resource_id)
        activity_times = data.get('data', {}).get('activityTimes', [])

        hours = []
        for at in activity_times:
            hours.append({
                'dayOfWeek': at.get('dayOfWeek'),
                'dayName': DAY_OF_WEEK_MAP.get(at.get('dayOfWeek'), 'Unknown'),
                'open': at.get('open'),
                'close': at.get('close'),
                'startDate': at.get('availabilityStartDate'),
                'endDate': at.get('availabilityEndDate')
            })
        return sorted(hours, key=lambda x: x['dayOfWeek'])

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with BondSports API.

        Args:
            email: User email
            password: User password

        Returns:
            Authentication data including access token

        Raises:
            requests.HTTPError: If login fails
        """
        url = f"{self.base_url}/auth/login"
        payload = {
            'email': email,
            'password': password,
            'platform': 'consumer'
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        # Store all tokens from response
        if 'credentials' in data:
            creds = data['credentials']
            self.access_token = creds.get('accessToken')
            self.id_token = creds.get('userIdToken')
            self.username = creds.get('username')
            self.refresh_token = creds.get('refreshToken')
            # Backwards compatibility
            self.auth_token = self.access_token

        return data

    def get_organization_slots(
        self,
        org_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get booked slots for an organization.

        Args:
            org_id: Organization ID
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Slot data

        Requires:
            Authentication (must call login() first)
        """
        if not self.auth_token:
            raise ValueError("Authentication required. Call login() first.")

        url = f"{self.base_url}/v1/organizations/{org_id}/slots"
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date

        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_space_slots(
        self,
        org_id: int,
        space_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get slots for a specific space/field.

        Args:
            org_id: Organization ID
            space_id: Space/resource ID
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Slot data for the space

        Requires:
            Authentication (must call login() first)
        """
        if not self.auth_token:
            raise ValueError("Authentication required. Call login() first.")

        url = f"{self.base_url}/v1/organizations/{org_id}/spaces/{space_id}/slots"
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date

        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_venue_slots(
        self,
        facility_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get slots for a venue/facility.

        Args:
            facility_id: Facility ID
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            Slot data for the venue

        Requires:
            Authentication (must call login() first)
        """
        if not self.auth_token:
            raise ValueError("Authentication required. Call login() first.")

        url = f"{self.base_url}/v1/venues/{facility_id}/slots"
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date

        response = self.session.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def check_availability(
        self,
        org_id: int,
        facility_id: int,
        dates: List[str],
        sport: int = 4
    ) -> Dict[str, Any]:
        """
        Check availability for online rentals (THE WORKING ENDPOINT!).

        This is the actual endpoint used by the BondSports website to show
        available time slots for field rentals.

        Args:
            org_id: Organization ID (450 for Wall Street, 436 for Crown Heights)
            facility_id: Facility ID (502 for Wall Street, 484 for Crown Heights)
            dates: List of dates in YYYY-MM-DD format
            sport: Sport ID (4 = Soccer, use None or omit for "Other")

        Returns:
            Dict with 'data' containing time slots keyed by date.
            Each slot has:
                - parentId: Space/field ID
                - parentType: "space"
                - dayOfWeek: Day number (8 = Sunday)
                - open/close: Time slot start/end (HH:MM:SS)
                - isClosed: True if unavailable, False if available

        Requires:
            Authentication (must call login() first)
        """
        if not self.auth_token:
            raise ValueError("Authentication required. Call login() first.")

        url = f"{self.base_url}/v4/online-rentals/organization/{org_id}/facility/{facility_id}/check-availability"
        payload = {"days": dates}
        if sport:
            payload["sport"] = sport

        response = self.session.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()
        return response.json()


def get_socceroof_resources(location: str) -> List[Dict[str, Any]]:
    """
    Get all field resources for a Socceroof location.

    Args:
        location: 'wall-street' or 'crown-heights'

    Returns:
        List of field resources
    """
    if location not in FACILITIES:
        raise ValueError(f"Unknown location: {location}. Use 'wall-street' or 'crown-heights'")

    facility = FACILITIES[location]
    api = BondSportsAPI()

    data = api.get_facility_resources(
        org_id=facility['organizationId'],
        facility_id=facility['facilityId']
    )

    resources = []
    for res in data.get('data', []):
        resources.append({
            'id': res['id'],
            'name': res['name'],
            'type': res.get('resourceType'),
            'status': res.get('status'),
            'description': res.get('description', ''),
            'activityTimes': res.get('activityTimes', [])
        })
    return resources


def parse_time_to_minutes(time_str: str) -> int:
    """Convert time string (HH:MM) to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes


def format_minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to time string (HH:MM)."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def find_available_blocks(
    operating_hours: Dict[str, str],
    booked_slots: List[Dict[str, Any]],
    min_duration: int = 60
) -> List[Dict[str, str]]:
    """
    Find available contiguous time blocks.

    Args:
        operating_hours: Dict with 'open' and 'close' times (HH:MM format)
        booked_slots: List of booked slots with 'startTime' and 'endTime'
        min_duration: Minimum duration in minutes for a block

    Returns:
        List of available blocks with 'start', 'end', and 'duration'
    """
    if not operating_hours:
        return []

    open_time = parse_time_to_minutes(operating_hours['open'])
    close_time = parse_time_to_minutes(operating_hours['close'])

    # Handle overnight hours (e.g., 10:00 AM - 2:00 AM)
    if close_time < open_time:
        close_time += 24 * 60

    # Parse booked slots and sort by start time
    booked = []
    for slot in booked_slots:
        start = parse_time_to_minutes(slot.get('startTime', '00:00'))
        end = parse_time_to_minutes(slot.get('endTime', '00:00'))
        if end < start:
            end += 24 * 60
        booked.append((start, end))

    booked.sort()

    # Find gaps between booked slots
    available = []
    current_time = open_time

    for start, end in booked:
        if start > current_time:
            # There's a gap before this booking
            duration = start - current_time
            if duration >= min_duration:
                available.append({
                    'start': format_minutes_to_time(current_time % (24 * 60)),
                    'end': format_minutes_to_time(start % (24 * 60)),
                    'duration': duration
                })
        current_time = max(current_time, end)

    # Check if there's time after the last booking
    if current_time < close_time:
        duration = close_time - current_time
        if duration >= min_duration:
            available.append({
                'start': format_minutes_to_time(current_time % (24 * 60)),
                'end': format_minutes_to_time(close_time % (24 * 60)),
                'duration': duration
            })

    return available


def get_field_operating_hours(location: str, field_name: str = None) -> Dict[str, Any]:
    """
    Get operating hours for Socceroof fields.

    Args:
        location: 'wall-street' or 'crown-heights'
        field_name: Optional field name filter (partial match)

    Returns:
        Dictionary of field names to operating hours
    """
    resources = get_socceroof_resources(location)
    api = BondSportsAPI()

    result = {}
    for res in resources:
        name = res['name']
        if field_name and field_name.lower() not in name.lower():
            continue

        hours = api.get_operating_hours(res['id'])
        result[name] = {
            'resourceId': res['id'],
            'hours': hours
        }
    return result


def print_facility_info(location: str):
    """Print detailed facility information."""
    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        return

    facility = FACILITIES[location]
    api = BondSportsAPI()

    print(f"\n{'='*60}")
    print(f"FACILITY: {facility['name']}")
    print(f"{'='*60}")
    print(f"Facility ID: {facility['facilityId']}")
    print(f"Organization ID: {facility['organizationId']}")
    print(f"Booking URL: {facility['url']}")

    # Get facility details
    data = api.get_facility(facility['facilityId'])
    fac_data = data.get('data', {})
    print(f"\nTimezone: {fac_data.get('timezone')}")

    # Get resources
    print(f"\n{'='*60}")
    print("FIELDS/SPACES:")
    print(f"{'='*60}")

    resources = get_socceroof_resources(location)
    for res in resources:
        print(f"\n{res['name']}:")
        print(f"  ID: {res['id']}")
        print(f"  Status: {res.get('status')}")

        # Get operating hours
        for at in res.get('activityTimes', []):
            day = DAY_OF_WEEK_MAP.get(at.get('dayOfWeek'), '?')
            print(f"  {day}: {at.get('open')} - {at.get('close')}")


def check_availability_with_token(
    location: str,
    date: str,
    token: str,
    field_name: Optional[str] = None
):
    """
    Check availability using an existing session token (for SSO accounts).

    Args:
        location: 'wall-street' or 'crown-heights'
        date: Date in YYYY-MM-DD format
        token: BondSports session token
        field_name: Optional filter for specific field (partial match)
    """
    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        print(f"Available: {', '.join(FACILITIES.keys())}")
        return

    facility = FACILITIES[location]
    api = BondSportsAPI(auth_token=token)

    print(f"\n{'='*70}")
    print(f"CHECKING AVAILABILITY: {facility['name']}")
    print(f"{'='*70}")
    print(f"Date: {date}")
    print("Using session token (SSO account)")

    # Get resources
    print("\nFetching fields...")
    resources = get_socceroof_resources(location)

    if field_name:
        resources = [r for r in resources if field_name.lower() in r['name'].lower()]
        print(f"Filtering for fields matching: {field_name}")

    print(f"Found {len(resources)} field(s)")

    # Get slots for the date
    print(f"\nFetching bookings for {date}...")
    try:
        slots_data = api.get_venue_slots(
            facility['facilityId'],
            start_date=date,
            end_date=date
        )
    except Exception as e:
        print(f"✗ Failed to fetch slots: {e}")
        print("\nPossible issues:")
        print("  - Token expired (log in again and get a new token)")
        print("  - Token invalid")
        print("  - Network error")
        return

    # Parse slots by resource
    slots_by_resource = {}
    for slot in slots_data.get('data', []):
        resource_id = slot.get('spaceId')
        if resource_id not in slots_by_resource:
            slots_by_resource[resource_id] = []
        slots_by_resource[resource_id].append(slot)

    # Calculate availability for each field
    print(f"\n{'='*70}")
    print("AVAILABILITY")
    print(f"{'='*70}")

    for res in resources:
        resource_id = res['id']
        field_name = res['name']

        # Get operating hours for this day of week
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = date_obj.weekday()
        # BondSports uses 2=Monday, so adjust
        bondsports_day = (day_of_week + 2) % 7 + 2

        activity_times = res.get('activityTimes', [])
        operating_hours = None
        for at in activity_times:
            if at.get('dayOfWeek') == bondsports_day:
                operating_hours = {
                    'open': at.get('open'),
                    'close': at.get('close')
                }
                break

        if not operating_hours:
            print(f"\n{field_name} (ID: {resource_id})")
            print("  ✗ Closed on this day")
            continue

        # Get booked slots
        booked = slots_by_resource.get(resource_id, [])

        # Calculate available blocks
        available = find_available_blocks(operating_hours, booked)

        print(f"\n{field_name} (ID: {resource_id})")
        print(f"  Operating Hours: {operating_hours['open']} - {operating_hours['close']}")

        if booked:
            print(f"  Booked Slots ({len(booked)}):")
            for slot in sorted(booked, key=lambda s: s.get('startTime', '')):
                start = slot.get('startTime')
                end = slot.get('endTime')
                print(f"    • {start} - {end}")

        if available:
            print(f"  Available Blocks ({len(available)}):")
            for block in available:
                duration_hrs = block['duration'] // 60
                duration_mins = block['duration'] % 60
                duration_str = f"{duration_hrs}h {duration_mins}m" if duration_mins else f"{duration_hrs}h"
                print(f"    ✓ {block['start']} - {block['end']} ({duration_str})")
        else:
            print("  ✗ No available time blocks")

    print(f"\n{'='*70}")


def check_availability(
    location: str,
    date: str,
    email: str,
    password: str,
    field_name: Optional[str] = None
):
    """
    Check availability for a location on a specific date.

    Args:
        location: 'wall-street' or 'crown-heights'
        date: Date in YYYY-MM-DD format
        email: BondSports account email
        password: BondSports account password
        field_name: Optional filter for specific field (partial match)
    """
    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        print(f"Available: {', '.join(FACILITIES.keys())}")
        return

    facility = FACILITIES[location]
    api = BondSportsAPI()

    print(f"\n{'='*70}")
    print(f"CHECKING AVAILABILITY: {facility['name']}")
    print(f"{'='*70}")
    print(f"Date: {date}")

    # Login
    print("\nAuthenticating...")
    try:
        auth_data = api.login(email, password)
        print("✓ Logged in successfully")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return

    # Get resources
    print("\nFetching fields...")
    resources = get_socceroof_resources(location)

    if field_name:
        resources = [r for r in resources if field_name.lower() in r['name'].lower()]
        print(f"Filtering for fields matching: {field_name}")

    print(f"Found {len(resources)} field(s)")

    # Get slots for the date
    print(f"\nFetching bookings for {date}...")
    try:
        slots_data = api.get_venue_slots(
            facility['facilityId'],
            start_date=date,
            end_date=date
        )
    except Exception as e:
        print(f"✗ Failed to fetch slots: {e}")
        return

    # Parse slots by resource
    slots_by_resource = {}
    for slot in slots_data.get('data', []):
        resource_id = slot.get('spaceId')
        if resource_id not in slots_by_resource:
            slots_by_resource[resource_id] = []
        slots_by_resource[resource_id].append(slot)

    # Calculate availability for each field
    print(f"\n{'='*70}")
    print("AVAILABILITY")
    print(f"{'='*70}")

    for res in resources:
        resource_id = res['id']
        field_name = res['name']

        # Get operating hours for this day of week
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = date_obj.weekday()
        # BondSports uses 2=Monday, so adjust
        bondsports_day = (day_of_week + 2) % 7 + 2

        activity_times = res.get('activityTimes', [])
        operating_hours = None
        for at in activity_times:
            if at.get('dayOfWeek') == bondsports_day:
                operating_hours = {
                    'open': at.get('open'),
                    'close': at.get('close')
                }
                break

        if not operating_hours:
            print(f"\n{field_name} (ID: {resource_id})")
            print("  ✗ Closed on this day")
            continue

        # Get booked slots
        booked = slots_by_resource.get(resource_id, [])

        # Calculate available blocks
        available = find_available_blocks(operating_hours, booked)

        print(f"\n{field_name} (ID: {resource_id})")
        print(f"  Operating Hours: {operating_hours['open']} - {operating_hours['close']}")

        if booked:
            print(f"  Booked Slots ({len(booked)}):")
            for slot in sorted(booked, key=lambda s: s.get('startTime', '')):
                start = slot.get('startTime')
                end = slot.get('endTime')
                print(f"    • {start} - {end}")

        if available:
            print(f"  Available Blocks ({len(available)}):")
            for block in available:
                duration_hrs = block['duration'] // 60
                duration_mins = block['duration'] % 60
                duration_str = f"{duration_hrs}h {duration_mins}m" if duration_mins else f"{duration_hrs}h"
                print(f"    ✓ {block['start']} - {block['end']} ({duration_str})")
        else:
            print("  ✗ No available time blocks")

    print(f"\n{'='*70}")


def main():
    """Main function demonstrating API usage."""
    import sys
    import os

    if len(sys.argv) < 2:
        print("BondSports API Client for Socceroof")
        print("\nUsage:")
        print("  python bondsports_api.py info <location>")
        print("  python bondsports_api.py resources <location>")
        print("  python bondsports_api.py hours <location> [field_name]")
        print("  python bondsports_api.py packages <resource_id>")
        print("  python bondsports_api.py availability <location> <date> [field_name]")
        print("\nLocations: wall-street, crown-heights")
        print("\nExamples:")
        print("  python bondsports_api.py info wall-street")
        print("  python bondsports_api.py resources crown-heights")
        print("  python bondsports_api.py hours wall-street 'Field 1'")
        print("  python bondsports_api.py packages 6084")
        print("  python bondsports_api.py availability wall-street 2026-02-15")
        print("\nFor availability checking, set environment variables:")
        print("  export BONDSPORTS_EMAIL=your@email.com")
        print("  export BONDSPORTS_PASSWORD=yourpassword")
        return

    command = sys.argv[1]

    if command == 'info':
        location = sys.argv[2] if len(sys.argv) > 2 else 'wall-street'
        print_facility_info(location)

    elif command == 'resources':
        location = sys.argv[2] if len(sys.argv) > 2 else 'wall-street'
        resources = get_socceroof_resources(location)
        print(f"\nResources for {FACILITIES.get(location, {}).get('name', location)}:")
        for res in resources:
            print(f"  {res['id']}: {res['name']}")

    elif command == 'hours':
        location = sys.argv[2] if len(sys.argv) > 2 else 'wall-street'
        field_name = sys.argv[3] if len(sys.argv) > 3 else None
        hours = get_field_operating_hours(location, field_name)
        for field, data in hours.items():
            print(f"\n{field} (ID: {data['resourceId']}):")
            for h in data['hours']:
                print(f"  {h['dayName']}: {h['open']} - {h['close']}")

    elif command == 'packages':
        resource_id = int(sys.argv[2]) if len(sys.argv) > 2 else 6084
        api = BondSportsAPI()
        packages = api.get_resource_packages(resource_id)
        print(f"\nPackages for resource {resource_id}:")
        for pkg in packages.get('data', []):
            p = pkg.get('package', {})
            print(f"\n  {p.get('name')}:")
            print(f"    Price: ${p.get('price')}")
            print(f"    Duration: {p.get('duration')} minutes")

    elif command == 'availability':
        if len(sys.argv) < 4:
            print("Usage: python bondsports_api.py availability <location> <date> [field_name]")
            print("Example: python bondsports_api.py availability wall-street 2026-02-15")
            return

        location = sys.argv[2]
        date = sys.argv[3]
        field_filter = sys.argv[4] if len(sys.argv) > 4 else None

        # Check for token first (for SSO accounts)
        token = os.environ.get('BONDSPORTS_TOKEN')

        if token:
            # Use token directly (for SSO accounts)
            check_availability_with_token(location, date, token, field_filter)
        else:
            # Fall back to email/password
            email = os.environ.get('BONDSPORTS_EMAIL')
            password = os.environ.get('BONDSPORTS_PASSWORD')

            if not email or not password:
                print("Error: Credentials not set")
                print("\nFor SSO accounts (Google/Gmail login):")
                print("  export BONDSPORTS_TOKEN='your_session_token'")
                print("  See get_token.md for instructions on getting your token")
                print("\nFor email/password accounts:")
                print("  export BONDSPORTS_EMAIL=your@email.com")
                print("  export BONDSPORTS_PASSWORD=yourpassword")
                return

            check_availability(location, date, email, password, field_filter)

    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
