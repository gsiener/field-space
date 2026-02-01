# Project Status: Socceroof Field Availability Checker

## What We've Discovered

### BondSports Platform
- Socceroof uses **BondSports** as their booking platform
- Wall Street: facilityId=502, organizationId=450
- Crown Heights: facilityId=484, organizationId=436

### API Investigation
✅ **Public API Works** - Can access:
- Facility information
- Resource/field listings
- Operating hours
- Pricing packages

❌ **Authentication Challenges**:
- `/auth` endpoint returns 404 (doesn't exist or different path)
- SSO tokens (`BondUserAccessToken` and `BondUserIdToken`) both return 401 Unauthorized
- Email/password login endpoint not found
- The actual authentication mechanism is unclear

### Browser Automation
- Can open the booking page
- Can navigate the interface
- Login flow works but session management is complex
- "Check Availability" button requires proper authentication state

## What We've Built

### Working Tools

1. **`bondsports_api.py`** - Python API client
   - ✅ Get facility info
   - ✅ List fields/resources
   - ✅ Get operating hours
   - ✅ Get pricing
   - ❌ Check real-time availability (auth required)

2. **`check_availability_simple.py`** - Browser automation (no login)
   - Opens booking page
   - Takes screenshots
   - Requires manual date selection

3. **`check_with_login.py`** - Browser automation with login
   - Attempts automated login
   - Navigates booking form
   - Takes screenshots

### Documentation

- `README.md` - Full documentation
- `SSO_QUICKSTART.md` - SSO setup guide
- `get_token.md` - Token extraction guide
- `SETUP.md` - General setup
- `capture_headers.md` - API investigation guide

## Recommended Approaches

### Option 1: Manual Browser Check (Easiest)
**Use the BondSports website directly**:
1. Log in to https://bondsports.co
2. Navigate to Wall Street or Crown Heights facility
3. Use their booking interface

**Pros**: Guaranteed to work, visual verification
**Cons**: Manual, not automated

### Option 2: Browser Automation with Manual Login
**Run browser in headed mode**:
```bash
agent-browser --headed open "https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450"
```

Then:
1. Log in manually (one time)
2. Browser maintains session
3. Use our scripts to automate checking

**Pros**: Semi-automated, maintains session
**Cons**: Requires initial manual login

### Option 3: Reverse Engineer Auth (Advanced)
**Capture actual API calls**:
1. Log in to BondSports in regular browser
2. Open DevTools Network tab
3. Check availability for a date
4. Find the actual API call to `api.bondsports.co`
5. Replicate the exact headers and authentication

**Pros**: Full automation once figured out
**Cons**: Time-consuming, fragile if they change it

## What We Know Works

### Public Information (No Auth)
```bash
# Get facility info with fields
python bondsports_api.py info wall-street

# Get operating hours
python bondsports_api.py hours wall-street

# Get pricing
python bondsports_api.py packages 6084
```

### Operating Hours (from API)
**Wall Street - All fields**:
- Weekdays (Mon-Fri): 10:00 AM - 2:00 AM
- Weekends (Sat-Sun): 8:00 AM - 2:00 AM

**Pricing** (Single Field 75'x45'):
- Non Prime Time: $175/hour
- Prime Time: $275/hour

## Next Steps

### If You Want Full Automation:
1. **Capture the real API authentication**:
   - Log in to BondSports in your browser
   - Open DevTools → Network tab
   - Click "Check Availability" on a date
   - Find the API request to `api.bondsports.co/.../ slots`
   - Copy ALL request headers
   - Share them so we can replicate

2. **Or use Playwright/Puppeteer**:
   - More robust browser automation
   - Better session management
   - Can handle complex auth flows

### If Semi-Manual is OK:
Use the BondSports website directly - it's fast, visual, and guaranteed to work.

## Files You Can Use

| File | Status | Use Case |
|------|--------|----------|
| `bondsports_api.py` | ✅ Working | Get facility info, hours, pricing |
| `check_availability_simple.py` | ⚠️ Partial | Open page, manual interaction |
| `check_with_login.py` | ⚠️ Partial | Automated login attempt |
| `.env` | ✅ Ready | Your credentials stored |

## Bottom Line

**For checking availability TODAY**: Use the BondSports website directly.

**For automation**: We need to capture the exact API authentication BondSports uses, or invest in more sophisticated browser automation (Playwright).

The core infrastructure is built - we just need the final authentication piece to make it fully automated.
