#!/usr/bin/env python3
"""
Simple Availability Checker using Browser Automation

This works with SSO accounts since it uses your existing browser session.
Just make sure you're logged in to bondsports.co first.
"""

import subprocess
import sys
import json
import time
from datetime import datetime

FACILITIES = {
    'wall-street': {
        'url': 'https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450',
        'name': 'Socceroof Wall Street'
    },
    'crown-heights': {
        'url': 'https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436',
        'name': 'Socceroof Crown Heights'
    }
}

def run_browser(cmd):
    """Run agent-browser command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def check_availability(location, date_str):
    """Check availability using browser automation"""

    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        print(f"Available: {', '.join(FACILITIES.keys())}")
        return

    facility = FACILITIES[location]

    print(f"\n{'='*70}")
    print(f"CHECKING AVAILABILITY: {facility['name']}")
    print(f"{'='*70}")
    print(f"Date: {date_str}")
    print()

    # Open the booking page
    print("Opening booking page...")
    run_browser(f'agent-browser open "{facility["url"]}"')
    time.sleep(5)

    # Take screenshot
    screenshot = f"/tmp/{location}-{date_str}.png"
    run_browser(f'agent-browser screenshot "{screenshot}"')
    print(f"Screenshot saved: {screenshot}")

    # Get page snapshot
    print("\nGetting page elements...")
    stdout, _, _ = run_browser('agent-browser snapshot -i --json')

    try:
        data = json.loads(stdout)
        refs = data.get('data', {}).get('refs', {})

        # Look for date picker elements
        date_elements = [
            (ref, info) for ref, info in refs.items()
            if 'date' in str(info).lower() or 'calendar' in str(info).lower()
        ]

        if date_elements:
            print(f"\nFound {len(date_elements)} date-related elements")
            print("You may need to interact manually to select the date")

        # Look for available time slots
        time_elements = [
            (ref, info) for ref, info in refs.items()
            if 'time' in str(info).lower() or ':' in info.get('name', '')
        ]

        if time_elements:
            print(f"\nFound {len(time_elements)} time-related elements:")
            for ref, info in time_elements[:10]:
                name = info.get('name', '')
                if name:
                    print(f"  {name}")

    except json.JSONDecodeError:
        print("Could not parse page data")

    print(f"\n{'='*70}")
    print("BROWSER SESSION OPEN")
    print(f"{'='*70}")
    print("The booking page is open in the browser.")
    print("You can:")
    print("  1. Select your date manually")
    print("  2. View available time slots")
    print("  3. Take more screenshots: agent-browser screenshot output.png")
    print("  4. Close when done: agent-browser close")
    print(f"{'='*70}\n")

def main():
    if len(sys.argv) < 3:
        print("Simple Availability Checker (Browser Automation)")
        print("\nUsage: python check_availability_simple.py <location> <date>")
        print("\nExamples:")
        print("  python check_availability_simple.py wall-street 2026-02-15")
        print("  python check_availability_simple.py crown-heights 2026-02-20")
        print(f"\nLocations: {', '.join(FACILITIES.keys())}")
        print("\nNote: Make sure you're logged in to bondsports.co first!")
        return

    location = sys.argv[1]
    date = sys.argv[2]

    check_availability(location, date)

if __name__ == '__main__':
    main()
