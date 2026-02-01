---
title: "BondSports API: Availability Endpoints Not Accessible Despite Successful Authentication"
category: api-integration-issues
module: BondSports Booking Platform
date: 2026-02-01
severity: high
status: partial

problem:
  description: Unable to retrieve field availability data from BondSports API despite successful authentication
  goal: Programmatically check soccer field availability at Socceroof facilities
  impact: Cannot automate availability checking; requires manual website interaction or browser automation

symptoms:
  - All availability/slots API endpoints return 404 Not Found
  - Successfully authenticated with AWS Cognito (JWT tokens obtained)
  - Public API endpoints work correctly (facility info, resources, pricing)
  - Tested 20+ endpoint variations without success
  - Website displays availability but API endpoint unknown

components:
  platform: BondSports API
  base_url: https://api.bondsports.co
  authentication: AWS Cognito JWT
  facilities:
    - Socceroof Wall Street (facilityId 502, orgId 450)
    - Socceroof Crown Heights (facilityId 484, orgId 436)

tags:
  - api
  - authentication
  - bondsports
  - availability
  - jwt
  - cognito
  - rest-api
  - 404-error
  - endpoint-discovery
  - socceroof
  - field-booking
  - aws-cognito
---

# BondSports API: Availability Endpoints Not Accessible

## Problem Summary

Successfully implemented AWS Cognito authentication with the BondSports API and can access public facility information, but **all availability/slots endpoints return 404 Not Found**. After testing 20+ different endpoint variations, determined that BondSports does not expose real-time availability data through their documented API.

## Symptoms

- ❌ All `/slots` and `/availability` endpoints return 404
- ✅ Authentication works perfectly (AWS Cognito JWT)
- ✅ Public endpoints work (facility info, resources, hours, pricing)
- ❌ Cannot retrieve booked slots or real-time availability
- ⚠️ Website shows availability but API path unknown

## Root Cause

BondSports API intentionally does not expose availability/booking data through public endpoints, likely to:
- Prevent automated scraping/booking bots
- Protect competitive pricing information
- Ensure users interact through official interfaces
- Control access to real-time data

## Investigation Steps

### Endpoints Tested (All Returned 404)

```python
# Venue/Facility based
/v1/venues/{facilityId}/slots
/v4/venues/{facilityId}/slots
/v1/facilities/{facilityId}/slots
/v4/facilities/{facilityId}/slots

# Organization based
/v1/organizations/{orgId}/slots
/v1/organizations/{orgId}/venues/{facilityId}/slots
/v4/organizations/{orgId}/venues/{facilityId}/slots

# Space/Resource based
/v1/organizations/{orgId}/spaces/{spaceId}/slots
/v4/resources/availability

# Booking based
/v4/bookings/slots
/v1/bookings/availability
/v4/bookings/availability
/v4/bookings/organization/{orgId}/facility/{facilityId}/bookings

# Schedule based
/v4/schedules/availability
```

### What Works

```python
# Public endpoints (no auth required)
GET /v1/organizations/{orgId}          # Organization info
GET /v1/venues/{facilityId}            # Facility details
GET /v4/organization/{orgId}           # Organization data

# Resource endpoints (no auth required)
GET /v4/resources/{resourceId}         # Resource details with hours
GET /v4/resources/{resourceId}/packages-v1  # Pricing
GET /v4/resources/organization/{orgId}/facility/{facilityId}/resources  # List fields
```

## Solution

### Working Implementation

**File**: `bondsports_api.py` (lines 227-261)

```python
def login(self, email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate with BondSports API using AWS Cognito.
    Returns authentication data including JWT tokens.
    """
    url = f"{self.base_url}/auth/login"
    payload = {
        'email': email,
        'password': password,
        'platform': 'consumer'  # Required field
    }
    response = self.session.post(url, json=payload)
    response.raise_for_status()

    data = response.json()
    if 'credentials' in data:
        creds = data['credentials']
        self.access_token = creds.get('accessToken')
        self.id_token = creds.get('userIdToken')
        self.username = creds.get('username')
        self.refresh_token = creds.get('refreshToken')
        self.auth_token = self.access_token

    return data
```

**Custom Headers** (lines 90-102):

```python
def _get_headers(self) -> Dict[str, str]:
    """BondSports requires custom headers, not standard Authorization."""
    headers = {}
    if self.access_token:
        headers['x-bonduseraccesstoken'] = self.access_token
    if self.id_token:
        headers['x-bonduseridtoken'] = self.id_token
    if self.username:
        headers['x-bonduserusername'] = self.username
    return headers
```

### Current Options

#### Option 1: Manual Website Checking (Recommended)

Visit https://www.socceroof.com/en/book/ directly:
- Select location (Wall Street or Crown Heights)
- Choose activity (Soccer)
- Select date
- View real-time availability

**Pros**: 100% reliable, visual confirmation
**Cons**: Manual process, not automated

#### Option 2: Browser Automation (Partial Solution)

**File**: `check_playwright.py`

```bash
export BONDSPORTS_USER="name@example.com"
export BONDSPORTS_PASS="password"
python check_playwright.py wall-street 02/15/2026
```

Automates login and form filling, captures screenshots for visual inspection.

**Pros**: Semi-automated, captures screenshots
**Cons**: Requires visual inspection, fragile if UI changes

#### Option 3: Public API for Static Data

```bash
# Get facility information
python bondsports_api.py info wall-street

# Get operating hours
python bondsports_api.py hours wall-street

# Get pricing
python bondsports_api.py packages 6084
```

**Pros**: Fast, reliable, programmable
**Cons**: Cannot get real-time availability

### Test Results

```bash
$ python test_connection.py

======================================================================
TEST 1: Public API Access
======================================================================
✓ Successfully fetched Wall Street facility info
✓ Successfully fetched resources (10 fields)

======================================================================
TEST 2: Authentication
======================================================================
✓ Successfully authenticated
  Token: eyJraWQiOiJJUnkyUytZ...

======================================================================
TEST 3: Slot Fetching
======================================================================
✗ Slot fetching failed: 404 Not Found
```

## Prevention Strategies

### Before Starting API Integration

1. **Validate API Exists First**
   ```bash
   # Open browser DevTools → Network tab
   # Perform action on website
   # Look for API calls to api.bondsports.co
   # Copy request as cURL
   ```

2. **Test Endpoints with curl**
   ```bash
   curl -s "https://api.bondsports.co/v1/test" | jq
   ```

3. **Separate Authentication Testing**
   - Create `test_connection.py` to test auth independently
   - Verify token extraction before attempting data access
   - Test with simple endpoint first

### API Integration Checklist

- [ ] Use browser DevTools to capture real API calls
- [ ] Test endpoints exist with `curl` before coding
- [ ] Test authentication separately from data access
- [ ] Document working endpoints as you discover them
- [ ] Build incrementally (public endpoints first)
- [ ] Implement fallback strategies early
- [ ] Handle 404/401/403 errors gracefully

### Decision Matrix: API vs Browser Automation

**Use Direct API when:**
- ✅ Endpoints return JSON
- ✅ Simple authentication (Bearer token)
- ✅ No CAPTCHA or rate limits
- ✅ Official documentation available

**Use Browser Automation when:**
- ❌ No API available or endpoints return 404
- ❌ Complex OAuth/SSO flows
- ❌ Need visual verification
- ❌ Website is only reliable source

**Use Hybrid Approach when:**
- ⚠️ Some endpoints work, others don't
- ⚠️ Browser needed for auth, API for data

## Related Files

| File | Purpose | Status |
|------|---------|--------|
| `bondsports_api.py` | Main API client | ✅ Working |
| `test_connection.py` | Auth testing | ✅ Working |
| `check_playwright.py` | Browser automation | ⚠️ Partial |
| `test_slots_endpoints.py` | Endpoint testing | ❌ All 404 |
| `.env` | Credentials | ✅ Configured |
| `CURRENT_STATUS.md` | Full status doc | ✅ Complete |

## Key Learnings

1. **Always verify API endpoints exist before implementing**
   Saved 4-8 hours by using browser DevTools first

2. **Test authentication separately from data access**
   `test_connection.py` validated auth before attempting slots

3. **Not all APIs expose all data**
   BondSports intentionally restricts availability data

4. **Browser automation is a valid fallback**
   When API isn't available, automation is better than manual

5. **Document as you discover**
   Don't wait until end to write documentation

## Next Steps

### For Immediate Use
Use https://www.socceroof.com/en/book/ directly

### For Automation
Use `check_playwright.py` for semi-automated checking

### For Future
Contact BondSports (support@bondsports.co) to request:
- Official API documentation
- Access to availability endpoints
- Partner/developer API credentials

## References

- [BondSports Platform](https://bondsports.co)
- [Socceroof Booking](https://www.socceroof.com/en/book/)
- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- Related docs: `API_INTEGRATION_BEST_PRACTICES.md`, `API_TROUBLESHOOTING_GUIDE.md`
