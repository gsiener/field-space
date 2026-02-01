#!/usr/bin/env python3
"""
Find the actual API endpoints used by Socceroof booking system

This script uses browser automation to capture network requests
and identify the API calls for availability checks.
"""

import subprocess
import json
import re
from datetime import datetime

def run_command(cmd):
    """Run a shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def analyze_page_source(url):
    """Extract API endpoints from page source"""
    print(f"Analyzing {url}...\n")

    # Open the page
    run_command(f'agent-browser open "{url}"')
    run_command('agent-browser wait 5000')

    # Get page HTML
    html, _, _ = run_command('agent-browser get html body')

    # Look for API-related patterns
    api_patterns = [
        r'https?://[^\s"\']+/api/[^\s"\']+',
        r'apiUrl["\']?\s*[:=]\s*["\']([^"\']+)',
        r'endpoint["\']?\s*[:=]\s*["\']([^"\']+)',
        r'baseURL["\']?\s*[:=]\s*["\']([^"\']+)',
        r'/api/v\d+/[^\s"\']+',
    ]

    print("Searching for API endpoints in page source...")
    found_endpoints = set()

    for pattern in api_patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            found_endpoints.add(match)

    if found_endpoints:
        print("\n✓ Found potential API endpoints:")
        for endpoint in sorted(found_endpoints):
            print(f"  - {endpoint}")
    else:
        print("\n✗ No obvious API endpoints found in HTML")

    # Look for script tags that might contain API calls
    script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"\n✓ Found {len(script_matches)} script blocks")

    # Search for fetch/axios calls
    fetch_calls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)', html)
    axios_calls = re.findall(r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)', html)

    if fetch_calls:
        print("\n✓ Found fetch() calls:")
        for url in set(fetch_calls):
            print(f"  - {url}")

    if axios_calls:
        print("\n✓ Found axios calls:")
        for url in set(axios_calls):
            print(f"  - {url}")

    run_command('agent-browser close')

    return found_endpoints

def main():
    print("="*60)
    print("SOCCEROOF API ENDPOINT FINDER")
    print("="*60)
    print()

    locations = {
        'wall-street': 'https://www.socceroof.com/en/book/club/wall-street/activity/rent-a-field/',
        'crown-heights': 'https://www.socceroof.com/en/book/club/crown-heights/activity/rent-a-field/'
    }

    all_endpoints = {}

    for name, url in locations.items():
        print(f"\n{'='*60}")
        print(f"Analyzing {name.upper()}")
        print(f"{'='*60}")
        endpoints = analyze_page_source(url)
        all_endpoints[name] = list(endpoints)
        print()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if any(all_endpoints.values()):
        print("\nTo make direct API calls, we can use:")
        print("  - curl")
        print("  - Python requests")
        print("  - Node.js fetch/axios")
        print("\nNext: Capture actual network requests during booking flow")
    else:
        print("\nNo API endpoints found in source.")
        print("Next step: Use browser DevTools to capture network requests")
        print("\nManual steps:")
        print("  1. Open browser DevTools (F12)")
        print("  2. Go to Network tab")
        print("  3. Visit booking page")
        print("  4. Select date and check availability")
        print("  5. Look for XHR/Fetch requests")

if __name__ == '__main__':
    main()
