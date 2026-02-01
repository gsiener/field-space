#!/usr/bin/env python3
"""
BondSports API Checker for Socceroof

Socceroof uses BondSports as their booking platform.

Facility IDs:
- Wall Street: facilityId=502, organizationId=450
- Crown Heights: facilityId=484, organizationId=436

URLs:
- Wall Street: https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450
- Crown Heights: https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436
"""

import subprocess
import sys
import json
from datetime import datetime
import time

FACILITIES = {
    'wall-street': {
        'facilityId': 502,
        'organizationId': 450,
        'name': 'Socceroof Wall Street-New York',
        'url': 'https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450'
    },
    'crown-heights': {
        'facilityId': 484,
        'organizationId': 436,
        'name': 'Socceroof - Crown Heights-New York',
        'url': 'https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436'
    }
}

def run_command(cmd):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def check_availability(location, date_str):
    """
    Check availability for a location on a given date

    Args:
        location: 'wall-street' or 'crown-heights'
        date_str: Date in format 'YYYY-MM-DD'
    """
    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        print(f"Available: {', '.join(FACILITIES.keys())}")
        sys.exit(1)

    facility = FACILITIES[location]
    url = facility['url']

    print(f"\n{'='*70}")
    print(f"CHECKING AVAILABILITY: {facility['name']}")
    print(f"{'='*70}")
    print(f"Date: {date_str}")
    print(f"Facility ID: {facility['facilityId']}")
    print(f"Organization ID: {facility['organizationId']}")
    print(f"URL: {url}")
    print(f"{'='*70}\n")

    # Open BondSports booking page
    print("Opening BondSports booking page...")
    run_command(f'agent-browser open "{url}"')
    time.sleep(5)

    # Take initial screenshot
    screenshot = f"/tmp/bondsports-{location}-initial.png"
    run_command(f'agent-browser screenshot "{screenshot}"')
    print(f"Screenshot saved: {screenshot}")

    # Get page snapshot
    print("\nGetting interactive elements...")
    stdout, _, _ = run_command('agent-browser snapshot -i --json')

    try:
        data = json.loads(stdout)
        if data.get('success') and data.get('data'):
            refs = data['data'].get('refs', {})
            print(f"\nFound {len(refs)} interactive elements:")

            # Look for date-related elements
            date_elements = [
                (ref, info) for ref, info in refs.items()
                if 'date' in info.get('name', '').lower() or
                   'calendar' in info.get('role', '').lower()
            ]

            if date_elements:
                print("\nDate-related elements:")
                for ref, info in date_elements:
                    print(f"  @{ref}: {info.get('role')} \"{info.get('name')}\"")

            # Look for time slot elements
            time_elements = [
                (ref, info) for ref, info in refs.items()
                if 'time' in info.get('name', '').lower() or
                   'slot' in info.get('name', '').lower() or
                   info.get('role') == 'button'
            ]

            if time_elements[:10]:  # Show first 10
                print("\nPotential time slot elements (first 10):")
                for ref, info in time_elements[:10]:
                    print(f"  @{ref}: {info.get('role')} \"{info.get('name')}\"")

    except json.JSONDecodeError:
        print("Could not parse snapshot JSON")

    # Take final screenshot
    screenshot2 = f"/tmp/bondsports-{location}-final.png"
    run_command(f'agent-browser screenshot "{screenshot2}"')
    print(f"\nFinal screenshot: {screenshot2}")

    print("\n" + "="*70)
    print("BROWSER SESSION OPEN")
    print("="*70)
    print("You can now interact with the browser using agent-browser commands:")
    print("  agent-browser snapshot -i         # See interactive elements")
    print("  agent-browser click @eX           # Click element X")
    print("  agent-browser screenshot file.png # Take screenshot")
    print("  agent-browser close              # Close when done")
    print("="*70)

    return {
        'location': location,
        'facility': facility,
        'date': date_str,
        'screenshots': [screenshot, screenshot2]
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python bondsports_checker.py <location> <date>")
        print("\nExamples:")
        print("  python bondsports_checker.py wall-street 2026-02-15")
        print("  python bondsports_checker.py crown-heights 2026-02-20")
        print(f"\nAvailable locations: {', '.join(FACILITIES.keys())}")
        print("\nFacility Information:")
        for loc, info in FACILITIES.items():
            print(f"  {loc}:")
            print(f"    Name: {info['name']}")
            print(f"    Facility ID: {info['facilityId']}")
            print(f"    Org ID: {info['organizationId']}")
        sys.exit(1)

    location = sys.argv[1]
    date_str = sys.argv[2]

    # Validate date format
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date format: {date_str}")
        print("Use YYYY-MM-DD format (e.g., 2026-02-15)")
        sys.exit(1)

    result = check_availability(location, date_str)

if __name__ == '__main__':
    main()
