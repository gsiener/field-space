#!/usr/bin/env python3
"""
Check availability with automated login

Uses browser automation to log in with email/password and check availability.
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime

FACILITIES = {
    'wall-street': {
        'url': 'https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450',
        'name': 'Socceroof Wall Street',
        'facilityId': 502
    },
    'crown-heights': {
        'url': 'https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436',
        'name': 'Socceroof Crown Heights',
        'facilityId': 484
    }
}

def run_browser(cmd):
    """Run agent-browser command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def check_availability(location, date_str, email, password):
    """Check availability with automated login"""

    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        return

    facility = FACILITIES[location]

    print(f"\n{'='*70}")
    print(f"CHECKING AVAILABILITY: {facility['name']}")
    print(f"{'='*70}")
    print(f"Date: {date_str}")
    print()

    # Open booking page
    print("Opening BondSports...")
    run_browser(f'agent-browser open "{facility["url"]}"')
    time.sleep(3)

    # Click Login button
    print("Clicking login...")
    run_browser('agent-browser click @e1')
    time.sleep(2)

    # Get login form elements
    stdout, _, _ = run_browser('agent-browser snapshot -i --json')
    data = json.loads(stdout)

    # Fill in email
    print(f"Logging in as {email}...")
    run_browser(f'agent-browser fill @e5 "{email}"')
    time.sleep(0.5)

    # Fill in password
    run_browser(f'agent-browser fill @e6 "{password}"')
    time.sleep(0.5)

    # Click Sign In
    run_browser('agent-browser click @e7')
    time.sleep(4)

    # Take screenshot after login
    screenshot1 = f"/tmp/{location}-logged-in.png"
    run_browser(f'agent-browser screenshot "{screenshot1}"')
    print(f"✓ Logged in - screenshot: {screenshot1}")

    # Now fill in the booking form
    print(f"\nChecking availability for {date_str}...")

    # Get updated snapshot
    run_browser('agent-browser snapshot -i')

    # Click activity selector
    run_browser('agent-browser find text "Activity" click')
    time.sleep(1)

    # Select Soccer
    run_browser('agent-browser find text "Soccer" click')
    time.sleep(1)

    # Enter date
    run_browser(f'agent-browser find placeholder "Date" fill "{date_str}"')
    time.sleep(1)

    # Click Check Availability
    run_browser('agent-browser find text "Check Availability" click')
    time.sleep(3)

    # Take screenshot of results
    screenshot2 = f"/tmp/{location}-availability-{date_str}.png"
    run_browser(f'agent-browser screenshot "{screenshot2}"')
    print(f"✓ Results screenshot: {screenshot2}")

    # Get page content to extract availability
    stdout, _, _ = run_browser('agent-browser get html body')

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Check the screenshots:")
    print(f"  1. After login: {screenshot1}")
    print(f"  2. Availability: {screenshot2}")
    print()
    print("Browser still open. To close: agent-browser close")
    print(f"{'='*70}\n")

def main():
    if len(sys.argv) < 3:
        print("Check Availability with Automated Login")
        print("\nUsage: python check_with_login.py <location> <date>")
        print("\nExamples:")
        print("  python check_with_login.py wall-street 2026-02-15")
        print("  python check_with_login.py crown-heights 2026-02-20")
        print(f"\nLocations: {', '.join(FACILITIES.keys())}")
        print("\nCredentials from .env:")
        print("  BONDSPORTS_USER=your@email.com")
        print("  BONDSPORTS_PASS=yourpassword")
        return

    location = sys.argv[1]
    date = sys.argv[2]

    # Get credentials from env
    email = os.environ.get('BONDSPORTS_USER') or os.environ.get('BONDSPORTS_EMAIL')
    password = os.environ.get('BONDSPORTS_PASS') or os.environ.get('BONDSPORTS_PASSWORD')

    if not email or not password:
        print("Error: Credentials not set")
        print("Set in .env file:")
        print("  BONDSPORTS_USER=your@email.com")
        print("  BONDSPORTS_PASS=yourpassword")
        print("\nThen run: source .env && python check_with_login.py ...")
        return

    check_availability(location, date, email, password)

if __name__ == '__main__':
    main()
