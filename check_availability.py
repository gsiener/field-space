#!/usr/bin/env python3
"""
Socceroof Field Availability Checker

Check available time slots at Socceroof Wall Street and Crown Heights.

Usage:
    python check_availability.py wall-street 2026-02-15
    python check_availability.py crown-heights 2026-02-15
    python check_availability.py all 2026-02-15

Requires:
    export BONDSPORTS_EMAIL=your@email.com
    export BONDSPORTS_PASSWORD=yourpassword
"""

import os
import sys
from datetime import datetime
from collections import defaultdict
from bondsports_api import BondSportsAPI, FACILITIES


def format_time(time_str: str) -> str:
    """Convert HH:MM:SS to 12-hour format."""
    hour, minute, _ = time_str.split(':')
    hour = int(hour)
    ampm = 'AM' if hour < 12 else 'PM'
    if hour == 0:
        hour = 12
    elif hour > 12:
        hour -= 12
    return f"{hour}:{minute} {ampm}"


def group_contiguous_slots(slots: list) -> list:
    """Group contiguous 30-minute slots into blocks."""
    if not slots:
        return []

    sorted_slots = sorted(slots, key=lambda x: x['open'])
    blocks = []
    current_block = {
        'start': sorted_slots[0]['open'],
        'end': sorted_slots[0]['close'],
        'count': 1
    }

    for slot in sorted_slots[1:]:
        if slot['open'] == current_block['end']:
            # Contiguous - extend the block
            current_block['end'] = slot['close']
            current_block['count'] += 1
        else:
            # Gap - save current block and start new one
            blocks.append(current_block)
            current_block = {
                'start': slot['open'],
                'end': slot['close'],
                'count': 1
            }

    blocks.append(current_block)
    return blocks


def check_availability(location: str, date: str, api: BondSportsAPI):
    """Check and display availability for a location."""
    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        return

    facility = FACILITIES[location]

    # Get availability
    result = api.check_availability(
        org_id=facility['organizationId'],
        facility_id=facility['facilityId'],
        dates=[date],
        sport=4  # Soccer
    )

    # Get resource names
    resources = api.get_facility_resources(
        facility['organizationId'],
        facility['facilityId']
    )
    resource_names = {r['id']: r['name'] for r in resources.get('data', [])}

    # Group slots by space
    slots = result.get('data', {}).get(date, [])
    by_space = defaultdict(list)
    for slot in slots:
        by_space[slot['parentId']].append(slot)

    # Format date for display
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    day_name = date_obj.strftime('%A')
    date_display = date_obj.strftime('%B %d, %Y')

    print(f"\n{'='*70}")
    print(f"{facility['name'].upper()} - {day_name}, {date_display}")
    print(f"{'='*70}")

    for space_id, space_slots in sorted(by_space.items()):
        name = resource_names.get(space_id, f'Space {space_id}')
        available_slots = [s for s in space_slots if not s['isClosed']]
        booked_slots = [s for s in space_slots if s['isClosed']]

        print(f"\n{name}:")

        # Show available blocks
        if available_slots:
            blocks = group_contiguous_slots(available_slots)
            for block in blocks:
                start = format_time(block['start'])
                end = format_time(block['end'])
                duration = block['count'] * 30  # 30-minute slots
                hours = duration // 60
                mins = duration % 60
                duration_str = f"{hours}h" if mins == 0 else f"{hours}h {mins}m"
                print(f"  Available: {start} - {end} ({duration_str})")
        else:
            print(f"  No availability")

        # Show booked summary
        if booked_slots:
            blocks = group_contiguous_slots(booked_slots)
            for block in blocks:
                start = format_time(block['start'])
                end = format_time(block['end'])
                print(f"  Booked: {start} - {end}")


def main():
    if len(sys.argv) < 3:
        print("Socceroof Field Availability Checker")
        print("\nUsage:")
        print("  python check_availability.py <location> <date>")
        print("\nLocations: wall-street, crown-heights, all")
        print("Date format: YYYY-MM-DD")
        print("\nExamples:")
        print("  python check_availability.py wall-street 2026-02-15")
        print("  python check_availability.py crown-heights 2026-02-15")
        print("  python check_availability.py all 2026-02-15")
        print("\nRequires:")
        print("  export BONDSPORTS_EMAIL=your@email.com")
        print("  export BONDSPORTS_PASSWORD=yourpassword")
        return 1

    location = sys.argv[1].lower()
    date = sys.argv[2]

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date format: {date}")
        print("Use YYYY-MM-DD format (e.g., 2026-02-15)")
        return 1

    # Get credentials
    email = os.environ.get('BONDSPORTS_EMAIL')
    password = os.environ.get('BONDSPORTS_PASSWORD')

    if not email or not password:
        print("Error: Credentials not set")
        print("\nSet environment variables:")
        print("  export BONDSPORTS_EMAIL=your@email.com")
        print("  export BONDSPORTS_PASSWORD=yourpassword")
        return 1

    # Login
    api = BondSportsAPI()
    try:
        api.login(email, password)
    except Exception as e:
        print(f"Login failed: {e}")
        return 1

    # Check availability
    if location == 'all':
        for loc in FACILITIES.keys():
            check_availability(loc, date, api)
    elif location in FACILITIES:
        check_availability(location, date, api)
    else:
        print(f"Unknown location: {location}")
        print(f"Available: {', '.join(FACILITIES.keys())}, all")
        return 1

    print(f"\n{'='*70}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
