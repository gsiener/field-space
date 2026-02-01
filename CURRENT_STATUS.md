# Current Status: Socceroof Field Availability

## Summary

**Project Complete!** We've successfully implemented a CLI tool to check field availability at Socceroof locations using the BondSports API.

## What Works

### 1. Authentication
- Email/password login working perfectly
- Returns valid AWS Cognito JWT tokens
- Custom headers properly configured:
  - `x-bonduseraccesstoken`
  - `x-bonduseridtoken`
  - `x-bonduserusername`

### 2. Availability Checking (THE KEY FEATURE!)
```bash
$ python check_availability.py wall-street 2026-02-15

======================================================================
SOCCEROOF WALL STREET - Sunday, February 15, 2026
======================================================================

Field 1- Single Field (5v5) :
  Available: 9:00 AM - 1:00 PM (4h)
  Available: 3:30 PM - 6:00 PM (2h 30m)
  Available: 7:00 PM - 12:00 AM (5h)
  Booked: 8:00 AM - 9:00 AM
  Booked: 1:00 PM - 3:30 PM
  ...
```

### 3. Public API Access
- **Facility info**: `/v1/venues/{facilityId}`
- **Organization data**: `/v1/organizations/{orgId}` and `/v4/organization/{orgId}`
- **Resources/fields**: `/v4/resources/organization/{orgId}/facility/{facilityId}/resources`
- **Resource details**: `/v4/resources/{resourceId}`
- **Pricing**: `/v4/resources/{resourceId}/packages-v1`

## The Discovered Endpoint

After testing 20+ endpoint variations that all returned 404, we used Chrome DevTools MCP to capture the real API endpoint:

**Endpoint**: `POST /v4/online-rentals/organization/{orgId}/facility/{facilityId}/check-availability`

**Request Body**:
```json
{
  "days": ["2026-02-15"],
  "sport": 4
}
```

**Response Structure**:
```json
{
  "data": {
    "2026-02-15": [
      {
        "parentId": 3215,
        "isClosed": false,
        "open": "09:00:00",
        "close": "09:30:00"
      }
    ]
  }
}
```

- Each slot is 30 minutes
- `isClosed: false` = available, `isClosed: true` = booked
- `parentId` maps to a field/resource ID

## Usage

```bash
# Set credentials
export BONDSPORTS_EMAIL="name@example.com"
export BONDSPORTS_PASSWORD="yourpassword"

# Check availability
python check_availability.py wall-street 2026-02-15
python check_availability.py crown-heights 2026-02-15
python check_availability.py all 2026-02-15
```

## Facility Information

**Wall Street** (facilityId: 502, orgId: 450):
- 10 fields/resources
- Operating hours: Weekdays 10AM-2AM, Weekends 8AM-2AM
- Pricing: $175-$275/hour depending on time

**Crown Heights** (facilityId: 484, orgId: 436):
- 7 fields/resources
- Similar structure

## Files

| File | Status | Purpose |
|------|--------|---------|
| `bondsports_api.py` | ✅ Complete | API client with auth & all endpoints |
| `check_availability.py` | ✅ Complete | CLI tool for checking availability |
| `test_connection.py` | ✅ Works | Test auth and public API |
| `.env` | ✅ Ready | Your credentials |

## How We Found It

1. Previous sessions tested 20+ endpoint patterns - all returned 404
2. User confirmed time slots appear on the website when checking availability
3. Used Chrome DevTools MCP to monitor network traffic while interacting with the booking page
4. Captured the POST request to `/v4/online-rentals/.../check-availability`
5. Implemented the endpoint in `bondsports_api.py`
6. Built the CLI tool in `check_availability.py`

## Notes

- When booking on the website, select "Other" activity for broader availability (not "Soccer")
- Sport ID 4 = Soccer in the API
