---
title: BondSports Availability API Endpoint Discovery - POST vs GET and Hidden Namespace
category: api-integration-issues
tags:
  - bondsports
  - api-discovery
  - rest-api
  - http-methods
  - endpoint-not-found
  - network-capture
  - chrome-devtools
  - availability-check
module: bondsports_api.py
symptoms:
  - All GET requests to /slots endpoints return 404
  - All GET requests to /availability endpoints return 404
  - Tested 20+ endpoint variations including /v1/venues/{id}/slots, /v4/bookings/slots, /v4/resources/availability
  - Authentication working correctly (200 responses on auth endpoints)
  - Public API endpoints accessible (facility info, resources, hours, pricing all work)
  - Website shows time slots when clicking "Check Availability", proving data exists
severity: high
date_discovered: 2026-02-01
files_affected:
  - bondsports_api.py
  - check_availability.py
---

# BondSports Availability API Endpoint Discovery

## Problem Summary

Spent 6+ hours testing 20+ API endpoint variations that all returned 404, when the actual availability endpoint:
1. Used **POST** instead of GET
2. Was under **/v4/online-rentals/** path instead of /slots/ or /availability/
3. Required a **JSON body** with "days" array instead of query parameters

## Symptoms

- All GET requests to `/v1/venues/{id}/slots` returned 404
- All GET requests to `/v4/bookings/slots` returned 404
- All GET requests to `/v4/resources/availability` returned 404
- Authentication worked perfectly (could access facility info, resources, pricing)
- Website displayed time slots when clicking "Check Availability" - proving the data existed

## Root Cause

The availability endpoint uses an unexpected:
- **HTTP Method**: POST (not GET)
- **Path namespace**: `/v4/online-rentals/` (not `/slots/` or `/availability/`)
- **Request format**: JSON body (not query parameters)

The endpoint was undocumented and only discoverable by monitoring actual network traffic.

## Solution

### The Discovered Endpoint

```
POST /v4/online-rentals/organization/{orgId}/facility/{facilityId}/check-availability
```

### Request Body

```json
{
  "days": ["2026-02-15"],
  "sport": 4
}
```

- `days`: Array of dates in YYYY-MM-DD format
- `sport`: Sport ID (4 = Soccer, omit for "Other"/broader availability)

### Required Headers

```
Content-Type: application/json
x-bonduseraccesstoken: {accessToken}
x-bonduseridtoken: {idToken}
x-bonduserusername: {username}
```

### Response Structure

```json
{
  "data": {
    "2026-02-15": [
      {
        "parentId": 3215,
        "parentType": "space",
        "dayOfWeek": 8,
        "open": "09:00:00",
        "close": "09:30:00",
        "isClosed": false
      }
    ]
  }
}
```

- Each slot is 30 minutes
- `isClosed: false` = available
- `isClosed: true` = booked
- `parentId` maps to field/resource ID

### Working Code

```python
def check_availability(
    self,
    org_id: int,
    facility_id: int,
    dates: List[str],
    sport: int = 4
) -> Dict[str, Any]:
    """Check availability for online rentals."""
    if not self.auth_token:
        raise ValueError("Authentication required. Call login() first.")

    url = f"{self.base_url}/v4/online-rentals/organization/{org_id}/facility/{facility_id}/check-availability"
    payload = {"days": dates}
    if sport:
        payload["sport"] = sport

    response = self.session.post(url, json=payload, headers=self._get_headers())
    response.raise_for_status()
    return response.json()
```

### Facility IDs

| Location | facilityId | orgId |
|----------|------------|-------|
| Wall Street | 502 | 450 |
| Crown Heights | 484 | 436 |

## How It Was Discovered

1. Previous sessions tested 20+ GET endpoint patterns - all returned 404
2. User confirmed time slots appear on website when checking availability
3. Used **Chrome DevTools MCP** to monitor network traffic
4. Navigated to booking page and filled out the form
5. Captured the POST request when clicking "Check Availability"
6. Identified the correct endpoint, method, and body format

## Prevention Strategies

### 1. Observe Before Guessing
**Rule**: Never write API integration code until you've captured the actual API call from the browser.

```
1. Open Chrome DevTools (F12) -> Network tab
2. Filter by "Fetch/XHR"
3. Perform the action on the website
4. Find the API request
5. Right-click -> "Copy as cURL"
6. Test BEFORE writing code
```

### 2. Time-Box Guessing
**Rule**: If 3 endpoint guesses return 404, stop guessing and start observing.

| Time Budget | Action |
|-------------|--------|
| First 15 min | Try 2-3 obvious patterns |
| If still failing | Switch to browser network monitoring |
| Never spend | More than 30 min guessing |

### 3. Verify HTTP Method Early
**Signs an endpoint uses POST**:
- Action involves querying with complex filters
- Request has a body (visible in "Payload" tab)
- Endpoint name includes verbs like "check", "search", "query"

### 4. Capture Full Request Details
Always record:
- URL (exact path)
- HTTP method
- Request headers (especially auth)
- Request body
- Response structure

## What Was Tried (All 404)

| Endpoint Pattern | Result |
|-----------------|--------|
| `GET /v1/venues/{id}/slots` | 404 |
| `GET /v4/venues/{id}/slots` | 404 |
| `GET /v1/facilities/{id}/slots` | 404 |
| `GET /v4/facilities/{id}/slots` | 404 |
| `GET /v1/organizations/{id}/slots` | 404 |
| `GET /v4/resources/availability` | 404 |
| `GET /v4/bookings/slots` | 404 |
| `GET /v4/schedules/availability` | 404 |
| ... 12+ more variations | 404 |

## Key Learnings

1. **Observation beats assumption**: The endpoint path `/online-rentals/` would never be guessed from REST conventions
2. **POST for queries is common**: Many APIs use POST for complex queries, not just mutations
3. **Browser DevTools is the source of truth**: The actual API is observable - always check there first
4. **Custom auth headers exist**: BondSports uses `x-bonduseraccesstoken` instead of standard `Authorization: Bearer`

## Related Documentation

- [CLAUDE.md](/Users/gsiener/src/field-space/CLAUDE.md) - Project session guide
- [CURRENT_STATUS.md](/Users/gsiener/src/field-space/CURRENT_STATUS.md) - Project status
- [bondsports_api.py](/Users/gsiener/src/field-space/bondsports_api.py) - API client implementation

## Usage

```bash
# Set credentials
export BONDSPORTS_EMAIL="your@email.com"
export BONDSPORTS_PASSWORD="yourpassword"

# Check availability
python check_availability.py wall-street 2026-02-15
python check_availability.py crown-heights 2026-02-15
python check_availability.py all 2026-02-15
```
