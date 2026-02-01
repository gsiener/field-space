#!/usr/bin/env python3
"""
Robust availability checker using Playwright

Playwright handles sessions and cookies better than agent-browser.
Install: pip install playwright && playwright install chromium
"""

import sys
import os
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Playwright not installed")
    print("Install with: pip install playwright && playwright install chromium")
    sys.exit(1)

FACILITIES = {
    'wall-street': {
        'url': 'https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450',
        'name': 'Socceroof Wall Street',
        'facilityId': 502,
        'orgId': 450
    },
    'crown-heights': {
        'url': 'https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436',
        'name': 'Socceroof Crown Heights',
        'facilityId': 484,
        'orgId': 436
    }
}

def check_availability(location, date_str, email, password, headless=True):
    """Check availability using Playwright"""

    if location not in FACILITIES:
        print(f"Unknown location: {location}")
        return

    facility = FACILITIES[location]

    print(f"\n{'='*70}")
    print(f"CHECKING AVAILABILITY: {facility['name']}")
    print(f"{'='*70}")
    print(f"Date: {date_str}\n")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        # Enable request interception to log API calls
        def log_request(request):
            if 'api.bondsports.co' in request.url:
                print(f"\n🔍 API Call: {request.method} {request.url}")
                print(f"   Headers: {request.headers}")

        page.on("request", log_request)

        try:
            # Go to facility page
            print("Loading booking page...")
            page.goto(facility['url'])
            page.wait_for_load_state('networkidle')

            # Click Login
            print("Clicking login...")
            page.click('button:has-text("Login")')
            page.wait_for_timeout(2000)

            # Fill in credentials
            print(f"Logging in as {email}...")
            page.fill('input[type="text"], input[type="email"]', email)
            page.fill('input[type="password"]', password)

            # Click Sign In
            page.click('button:has-text("Sign In")')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)

            # Take screenshot after login
            screenshot1 = f'/tmp/{location}-playwright-logged-in.png'
            page.screenshot(path=screenshot1)
            print(f"✓ Logged in - {screenshot1}")

            # Fill booking form
            print(f"\nFilling booking form for {date_str}...")

            # Select activity
            page.click('button:has-text("Activity")')
            page.wait_for_timeout(1000)
            page.click('text=Soccer')
            page.wait_for_timeout(1000)

            # Enter date
            date_input = page.locator('input[type="text"]').nth(1)
            date_input.fill(date_str)
            page.wait_for_timeout(1000)

            # Click Check Availability
            print("Checking availability...")
            page.click('button:has-text("Check Availability")')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(3000)

            # Take screenshot of results
            screenshot2 = f'/tmp/{location}-playwright-results-{date_str}.png'
            page.screenshot(path=screenshot2)
            print(f"✓ Results - {screenshot2}")

            # Try to extract availability data from the page
            print(f"\n{'='*70}")
            print("AVAILABILITY DATA")
            print(f"{'='*70}")

            # Look for time slots or availability information
            content = page.content()

            # Save HTML for analysis
            html_file = f'/tmp/{location}-results-{date_str}.html'
            with open(html_file, 'w') as f:
                f.write(content)
            print(f"HTML saved: {html_file}")

            print(f"\nScreenshots:")
            print(f"  1. After login: {screenshot1}")
            print(f"  2. Results: {screenshot2}")
            print(f"\n{'='*70}\n")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path=f'/tmp/{location}-error.png')

        finally:
            if not headless:
                input("Press Enter to close browser...")
            browser.close()

def main():
    if len(sys.argv) < 3:
        print("Playwright Availability Checker")
        print("\nUsage: python check_playwright.py <location> <date> [--headed]")
        print("\nExamples:")
        print("  python check_playwright.py wall-street 2026-02-15")
        print("  python check_playwright.py crown-heights 02/15/2026 --headed")
        print(f"\nLocations: {', '.join(FACILITIES.keys())}")
        print("\nRequires:")
        print("  pip install playwright")
        print("  playwright install chromium")
        print("\nCredentials from .env:")
        print("  BONDSPORTS_USER=your@email.com")
        print("  BONDSPORTS_PASS=yourpassword")
        return

    location = sys.argv[1]
    date = sys.argv[2]
    headless = '--headed' not in sys.argv

    # Get credentials
    email = os.environ.get('BONDSPORTS_USER') or os.environ.get('BONDSPORTS_EMAIL')
    password = os.environ.get('BONDSPORTS_PASS') or os.environ.get('BONDSPORTS_PASSWORD')

    if not email or not password:
        print("Error: Credentials not set")
        print("Set in .env file:")
        print("  BONDSPORTS_USER=your@email.com")
        print("  BONDSPORTS_PASS=yourpassword")
        return

    check_availability(location, date, email, password, headless)

if __name__ == '__main__':
    main()
