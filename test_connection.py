#!/usr/bin/env python3
"""
Test connection to BondSports API

This script tests:
1. Public API access (no auth)
2. Authentication (with credentials)
3. Slot fetching (authenticated)
"""

import os
import sys
from bondsports_api import BondSportsAPI, FACILITIES

def test_public_api():
    """Test public endpoints."""
    print("="*70)
    print("TEST 1: Public API Access")
    print("="*70)

    api = BondSportsAPI()

    try:
        # Test facility endpoint
        facility = api.get_facility(502)  # Wall Street
        print("✓ Successfully fetched Wall Street facility info")
        print(f"  Facility name: {facility.get('data', {}).get('name')}")

        # Test resources endpoint
        resources = api.get_facility_resources(450, 502)
        num_resources = len(resources.get('data', []))
        print(f"✓ Successfully fetched resources ({num_resources} fields)")

        return True

    except Exception as e:
        print(f"✗ Public API test failed: {e}")
        return False


def test_authentication():
    """Test authentication."""
    print("\n" + "="*70)
    print("TEST 2: Authentication")
    print("="*70)

    # Check for token first (SSO accounts)
    token = os.environ.get('BONDSPORTS_TOKEN')

    if token:
        print("Using session token (SSO account)")
        print(f"Token: {token[:20]}..." if len(token) > 20 else "Token set")

        api = BondSportsAPI(auth_token=token)

        # Test token by trying to fetch slots
        try:
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            facility = FACILITIES['wall-street']
            slots = api.get_venue_slots(facility['facilityId'], today, today)
            print("✓ Token is valid")
            return True
        except Exception as e:
            print(f"✗ Token invalid or expired: {e}")
            print("\nPlease get a new token:")
            print("  1. Log in to bondsports.co")
            print("  2. Open DevTools (F12)")
            print("  3. Find your auth token (see get_token.md)")
            print("  4. export BONDSPORTS_TOKEN='your_token'")
            return False

    # Fall back to email/password
    email = os.environ.get('BONDSPORTS_EMAIL')
    password = os.environ.get('BONDSPORTS_PASSWORD')

    if not email or not password:
        print("✗ Credentials not set")
        print("\nFor SSO accounts (Google/Gmail login):")
        print("  export BONDSPORTS_TOKEN='your_session_token'")
        print("  See get_token.md for instructions")
        print("\nFor email/password accounts:")
        print("  export BONDSPORTS_EMAIL='your@email.com'")
        print("  export BONDSPORTS_PASSWORD='yourpassword'")
        return False

    print(f"Email: {email}")

    api = BondSportsAPI()

    try:
        auth_data = api.login(email, password)
        print("✓ Successfully authenticated")
        print(f"  Token: {api.auth_token[:20]}..." if api.auth_token else "  No token")
        return True

    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\nPossible issues:")
        print("  - Account uses SSO (use BONDSPORTS_TOKEN instead)")
        print("  - Incorrect email or password")
        print("  - Account locked or disabled")
        print("  - Network issues")
        return False


def test_slot_fetching():
    """Test fetching slots (requires authentication)."""
    print("\n" + "="*70)
    print("TEST 3: Slot Fetching")
    print("="*70)

    email = os.environ.get('BONDSPORTS_EMAIL')
    password = os.environ.get('BONDSPORTS_PASSWORD')

    if not email or not password:
        print("⊘ Skipping (no credentials)")
        return None

    api = BondSportsAPI()

    try:
        # Login
        api.login(email, password)

        # Try to fetch slots for today
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        facility = FACILITIES['wall-street']
        slots = api.get_venue_slots(facility['facilityId'], today, today)

        num_slots = len(slots.get('data', []))
        print(f"✓ Successfully fetched slots for {today}")
        print(f"  Found {num_slots} booked slot(s)")

        return True

    except Exception as e:
        print(f"✗ Slot fetching failed: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("BONDSPORTS API CONNECTION TEST")
    print("="*70)
    print()

    results = []

    # Test public API
    results.append(("Public API", test_public_api()))

    # Test authentication
    results.append(("Authentication", test_authentication()))

    # Test slot fetching
    slot_result = test_slot_fetching()
    if slot_result is not None:
        results.append(("Slot Fetching", slot_result))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n✓ All tests passed! You're ready to check availability.")
        print("\nNext steps:")
        print("  ./check_fields.sh 2026-02-15")
        print("  python bondsports_api.py availability wall-street 2026-02-15")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")

    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
