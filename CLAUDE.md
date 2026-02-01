# Claude Session Guide: BondSports Field Availability Project

## Quick Start

```bash
# Check field availability
export BONDSPORTS_EMAIL="name@example.com"
export BONDSPORTS_PASSWORD="yourpassword"
python check_availability.py wall-street 2026-02-15
python check_availability.py crown-heights 2026-02-15
python check_availability.py all 2026-02-15
```

## Project Overview

**Goal**: Automate checking soccer field availability at Socceroof locations (Wall Street & Crown Heights) using the BondSports booking API.

**Current Status**: ✅ COMPLETE
- ✅ Authentication working perfectly
- ✅ Public API endpoints accessible
- ✅ **Availability endpoint discovered and working!**
- ✅ CLI tool for checking availability

## The Discovered Endpoint

After extensive testing of 20+ endpoint variations that all returned 404, we used Chrome DevTools MCP to capture the real API endpoint by monitoring network traffic on the booking website.

**Endpoint**: `POST /v4/online-rentals/organization/{orgId}/facility/{facilityId}/check-availability`

**Request Body**:
```json
{
  "days": ["2026-02-15"],
  "sport": 4
}
```

**Sport IDs**:
- `4` = Soccer
- Note: When booking on the website, select "Other" activity for broader availability

**Response Structure**:
```json
{
  "data": {
    "2026-02-15": [
      {
        "parentId": 3215,
        "isClosed": false,
        "open": "09:00:00",
        "close": "09:30:00",
        ...
      },
      ...
    ]
  }
}
```

- Each slot is 30 minutes
- `isClosed: false` = available, `isClosed: true` = booked
- `parentId` corresponds to a field/resource ID

## What We Built

### 1. Complete API Client
**File**: `bondsports_api.py`

**Working Features**:
- AWS Cognito JWT authentication via email/password
- Custom headers: `x-bonduseraccesstoken`, `x-bonduseridtoken`, `x-bonduserusername`
- Public API access (facility info, resources, hours, pricing)
- **`check_availability()` method** - the key endpoint!

### 2. CLI Availability Checker
**File**: `check_availability.py`

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

### 3. Test Suite
- `test_connection.py` - Authentication & public API testing

## Credentials

Stored in `.env`:
```bash
BONDSPORTS_EMAIL=name@example.com
BONDSPORTS_PASSWORD=yourpassword
```

## Facilities

**Wall Street**:
- facilityId: 502
- organizationId: 450
- 10 fields/resources

**Crown Heights**:
- facilityId: 484
- organizationId: 436
- 7 fields/resources

## Known Working API Endpoints

```python
# Organization info
GET /v1/organizations/{orgId}
GET /v4/organization/{orgId}

# Facility info
GET /v1/venues/{facilityId}

# Resources (fields)
GET /v4/resources/organization/{orgId}/facility/{facilityId}/resources
GET /v4/resources/{resourceId}
GET /v4/resources/{resourceId}/packages-v1  # Pricing

# Authentication
POST /auth/login
  Payload: {email, password, platform: 'consumer'}
  Returns: {credentials: {accessToken, userIdToken, username, refreshToken}}

# AVAILABILITY (THE KEY ENDPOINT!)
POST /v4/online-rentals/organization/{orgId}/facility/{facilityId}/check-availability
  Payload: {days: ["YYYY-MM-DD"], sport: 4}
  Returns: {data: {"YYYY-MM-DD": [{parentId, isClosed, open, close, ...}]}}
```

## Authentication Details

**Method**: AWS Cognito JWT via email/password

**Custom Headers Required**:
- `x-bonduseraccesstoken` - Access token (JWT)
- `x-bonduseridtoken` - ID token (JWT)
- `x-bonduserusername` - Username from credentials

**Login Endpoint**: `POST /auth/login`

**Required Payload**:
```json
{
  "email": "name@example.com",
  "password": "yourpassword",
  "platform": "consumer"
}
```

## Testing Commands

```bash
# Check availability (primary use case)
export BONDSPORTS_EMAIL="name@example.com"
export BONDSPORTS_PASSWORD="yourpassword"
python check_availability.py wall-street 2026-02-15
python check_availability.py crown-heights 2026-02-15
python check_availability.py all 2026-02-15

# Test authentication
python test_connection.py

# Get facility info
python bondsports_api.py info wall-street

# Get operating hours
python bondsports_api.py hours wall-street
```

## Important Files

| File | Purpose |
|------|---------|
| `bondsports_api.py` | Main API client with all endpoints |
| `check_availability.py` | CLI tool for checking availability |
| `test_connection.py` | Auth and API testing |
| `.env` | Credentials |

## Success Criteria (All Complete)

- [x] Find the availability API endpoint
- [x] Successfully fetch time slots data
- [x] Parse and display available time blocks
- [x] Works for both locations (Wall Street, Crown Heights)
- [x] Works for different dates
- [x] Update documentation with working solution
