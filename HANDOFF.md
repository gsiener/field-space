# Session Handoff: BondSports Availability API

**Date**: 2026-02-01
**Status**: 🟡 Awaiting endpoint discovery
**Priority**: HIGH - User confirmed time slots appear on website

---

## Immediate Next Steps (After Restart)

### 1. Verify Chrome DevTools MCP is Active ⚡

After restarting Claude Code session:

```bash
# Check if tools are available
# Should see chrome-devtools MCP tools loaded
```

MCP has been installed at: `~/.claude.json`

### 2. Capture the Real Availability Endpoint 🎯

**This is the ONE missing piece!**

The user observed that visiting:
```
https://www.socceroof.com/en/book/club/crown-heights/activity/rent-a-field/
```

And filling out:
- Activity: "Other" or "Soccer"
- Date: Any date
- Click "Check Availability"

**Shows time slots** - so the data IS being loaded from an API endpoint.

**Use Chrome DevTools MCP to**:
1. Launch Chrome with debugging
2. Navigate to the booking page
3. Monitor network requests
4. Capture the API call when "Check Availability" is clicked
5. Extract: URL, method, headers, parameters

### 3. Implement & Test Immediately

Once you have the endpoint:

```python
# Add to bondsports_api.py
def get_availability(self, facility_id, start_date, end_date=None, **kwargs):
    """The endpoint you discovered"""
    url = f"{self.base_url}/DISCOVERED_ENDPOINT"
    params = {
        'startDate': start_date,
        'endDate': end_date or start_date,
        'facilityId': facility_id,
        # Add any other required params from capture
    }
    response = self.session.get(url, params=params, headers=self._get_headers())
    response.raise_for_status()
    return response.json()
```

Test:
```bash
python -c "
from bondsports_api import BondSportsAPI, FACILITIES
api = BondSportsAPI()
api.login('name@example.com', 'yourpassword')
data = api.get_availability(502, '2026-02-15')
print(data)
"
```

---

## Current State Summary

### ✅ What's Working (100%)

**Authentication**:
- Email/password login via AWS Cognito
- JWT token extraction and storage
- Custom headers properly configured
- Refresh token support
- Both SSO and email/password accounts

**Public API Access**:
- Facility information (`/v1/venues/{id}`)
- Organization data (`/v4/organization/{id}`)
- Resources/fields list with operating hours
- Pricing packages
- Field metadata

**Test Results**:
```bash
$ python test_connection.py
✓ Public API Access: PASS
✓ Authentication: PASS
✗ Slot Fetching: FAIL (404)
```

### ❌ What's Not Working

**Availability Endpoints** - All return 404:
- Tested 20+ different endpoint variations
- Multiple URL patterns (v1, v4, venues, organizations, bookings, schedules)
- Different HTTP methods (GET, POST)
- Various parameter combinations

**Root cause**: The real endpoint pattern hasn't been discovered yet.

### 🔍 The Breakthrough

**User confirmation**: Time slots DO appear on the website when using the booking form.

This proves:
- The endpoint exists
- Authentication works end-to-end
- Data structure is accessible
- We just need to capture the actual API call

---

## Critical Information

### Credentials
```bash
Email: name@example.com
Password: yourpassword
```

### Facilities
```python
Wall Street: facilityId=502, orgId=450
Crown Heights: facilityId=484, orgId=436
```

### Authentication Headers (REQUIRED)
```python
{
    'x-bonduseraccesstoken': access_token,
    'x-bonduseridtoken': id_token,
    'x-bonduserusername': username
}
```

### Login Endpoint
```
POST https://api.bondsports.co/auth/login
Body: {email, password, platform: 'consumer'}
```

**CRITICAL**: Must include `platform: 'consumer'` or login fails

---

## Files You Need

### Must Read
- **`CLAUDE.md`** - Complete session guide (this is comprehensive)
- **`bondsports_api.py`** - Main API client (lines 227-261 for auth, 90-102 for headers)
- **`test_connection.py`** - Working authentication test

### Reference
- **`CURRENT_STATUS.md`** - Full status document
- **`docs/solutions/api-integration-issues/bondsports-availability-endpoints-not-accessible.md`** - Problem documentation

### If MCP Fails
- **`manual_check.md`** - Instructions for manual capture via Chrome DevTools

---

## Fallback Plan (If Chrome DevTools MCP Has Issues)

### Option A: Manual Chrome DevTools
Ask user to:
1. Open Chrome, press F12
2. Go to Network tab, check "Preserve log"
3. Visit booking page
4. Fill form and click "Check Availability"
5. Find the API call in network tab
6. Copy as cURL or share the URL + headers

### Option B: Playwright with Enhanced Logging
File: `capture_with_cdp.py` (created but not tested)
- Uses Chrome DevTools Protocol
- Logs all API calls
- Manual interaction required

### Option C: Contact BondSports
Email: support@bondsports.co
Request: API documentation for availability endpoints

---

## Expected Data Structure (Based on Public Endpoints)

**Typical BondSports Response**:
```json
{
  "data": [...],  // Main data array or object
  "meta": {...},   // Optional metadata
  "status": "success"
}
```

**Likely availability response**:
```json
{
  "data": [
    {
      "resourceId": 6084,
      "resourceName": "Field 1",
      "date": "2026-02-15",
      "slots": [
        {
          "startTime": "08:00",
          "endTime": "09:00",
          "available": true,
          "price": 175
        },
        ...
      ]
    }
  ]
}
```

Or it might be organized differently. Once captured, adapt parsing accordingly.

---

## Success Metrics

### Phase 1: Discovery (CURRENT PHASE)
- [ ] Chrome DevTools MCP loaded and working
- [ ] Captured real availability API endpoint
- [ ] Verified endpoint returns data

### Phase 2: Implementation
- [ ] Added method to `bondsports_api.py`
- [ ] Successfully fetches availability data
- [ ] Parses response correctly

### Phase 3: User Experience
- [ ] Works for both locations
- [ ] Works for any date
- [ ] Displays time slots in readable format
- [ ] Shows available blocks per field

---

## Conversation Context

**User's original request**:
> "I want to check availability for indoor soccer spaces and get what times are available (as contiguous blocks) for each field"

**What we built**:
- Complete API client with authentication
- Public data access working perfectly
- Extensive endpoint testing and documentation

**What's missing**:
- The ONE endpoint that returns availability/time slots

**Why it's missing**:
- BondSports doesn't document availability endpoints
- Standard REST patterns don't work
- Endpoint might use non-standard URL structure

**How to fix**:
- Capture the real API call from the working website
- This is what Chrome DevTools MCP is for!

---

## Important Reminders

1. **Don't reinvent the wheel** - Authentication already works perfectly
2. **The endpoint exists** - User confirmed seeing time slots
3. **Use Chrome DevTools MCP** - That's why we installed it
4. **Test immediately** - Once found, implement and test right away
5. **Document the success** - Update all docs with the working solution

---

## Final Notes

This has been a thorough investigation:
- Built complete authentication system
- Tested 20+ endpoint variations systematically
- Created comprehensive documentation
- Prepared multiple fallback approaches

**The payoff is close**: We just need that one missing endpoint URL.

**Estimated time to completion**: 30-60 minutes after capturing the endpoint

**Next Claude**: You've got this! The hard work is done, now just capture that endpoint! 🚀

---

## Quick Reference Commands

```bash
# After restart - first thing to check
# Verify MCP is loaded (should see chrome-devtools tools)

# If MCP is ready, use it to:
# 1. Launch Chrome
# 2. Navigate to booking page
# 3. Capture network traffic
# 4. Find the availability endpoint

# Once you have the endpoint, test immediately:
export BONDSPORTS_EMAIL="name@example.com"
export BONDSPORTS_PASSWORD="yourpassword"
python test_connection.py

# Then implement the new method and test
python -c "from bondsports_api import *; ..."
```

Good luck! 🎯
