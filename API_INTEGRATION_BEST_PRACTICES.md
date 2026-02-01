# API Integration Best Practices and Prevention Strategies

A comprehensive guide based on real-world experience integrating with the BondSports API for Socceroof field availability checking.

## Table of Contents

1. [Pre-Integration API Discovery](#1-pre-integration-api-discovery)
2. [Authentication Testing Strategy](#2-authentication-testing-strategy)
3. [Endpoint Discovery Techniques](#3-endpoint-discovery-techniques)
4. [API vs Browser Automation Decision Matrix](#4-api-vs-browser-automation-decision-matrix)
5. [Implementation Checklist](#5-implementation-checklist)
6. [Fallback Strategies](#6-fallback-strategies)
7. [Common Pitfalls and Solutions](#7-common-pitfalls-and-solutions)

---

## 1. Pre-Integration API Discovery

### Step 1: Verify API Exists Before Writing Code

**ALWAYS do this first:**

```bash
# Open browser DevTools BEFORE writing any code
# 1. Open the website in Chrome/Firefox
# 2. Open DevTools (F12 or Cmd+Option+I)
# 3. Go to Network tab
# 4. Filter by "Fetch/XHR" or "API"
# 5. Interact with the website (select dates, check availability)
# 6. Look for API calls in the Network panel
```

**What to look for:**

- API endpoints (URLs starting with `/api/`, `api.`, etc.)
- Request/response payloads
- Authentication headers
- Query parameters
- Response data structure

### Step 2: Test Endpoints Manually

Before writing any integration code, test endpoints with `curl`:

```bash
# Test public endpoints (no auth)
curl -s "https://api.example.com/v1/resources" | jq

# Test with headers that might be required
curl -s -H "Content-Type: application/json" \
     -H "User-Agent: Mozilla/5.0" \
     "https://api.example.com/v1/resources" | jq

# Test authenticated endpoints
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
     "https://api.example.com/v1/slots" | jq
```

**Key indicators an API is usable:**

- Returns JSON/XML data (not HTML)
- Returns structured error messages
- Has consistent URL patterns
- Responds to standard HTTP methods

**Red flags:**

- Returns HTML pages instead of JSON
- Returns 404 for logical endpoints
- No error messages, just blank responses
- Requires complex authentication flows

### Step 3: Document API Structure

Create a quick reference document:

```markdown
## API Discovery Notes

**Base URL:** https://api.example.com

### Public Endpoints (No Auth Required)
- GET /v1/facilities/{id} - Facility info
- GET /v1/resources - List resources

### Authenticated Endpoints
- GET /v1/slots - Booking data (requires auth)

### Authentication
- Method: Bearer token
- Header: Authorization: Bearer {token}
- Login: POST /auth/login

### Test Commands
curl -s "https://api.example.com/v1/facilities/123" | jq
```

---

## 2. Authentication Testing Strategy

### Separate Authentication from Data Access

**Test authentication independently:**

1. Create a minimal authentication test script
2. Verify you can get a token
3. Test the token with a simple endpoint
4. Only then proceed to complex data access

**Example: `test_connection.py`**

```python
#!/usr/bin/env python3
"""Test authentication before building full integration"""

import requests
import os

def test_login():
    """Test login and token retrieval"""
    email = os.environ.get('API_EMAIL')
    password = os.environ.get('API_PASSWORD')

    if not email or not password:
        print("Error: Set API_EMAIL and API_PASSWORD environment variables")
        return False

    # Test login
    response = requests.post(
        'https://api.example.com/auth/login',
        json={'email': email, 'password': password}
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get('credentials', {}).get('accessToken')
        print(f"✓ Login successful")
        print(f"✓ Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_authenticated_endpoint(token):
    """Test a simple authenticated endpoint"""
    response = requests.get(
        'https://api.example.com/v1/user/profile',
        headers={'Authorization': f'Bearer {token}'}
    )

    if response.status_code == 200:
        print("✓ Authenticated request successful")
        return True
    else:
        print(f"✗ Authenticated request failed: {response.status_code}")
        return False

if __name__ == '__main__':
    token = test_login()
    if token:
        test_authenticated_endpoint(token)
```

### SSO and Third-Party Auth

**Problem:** Many services use Google/GitHub/etc. OAuth, which is hard to automate.

**Solutions:**

1. **Extract Session Token from Browser:**
   ```bash
   # In browser DevTools Console:
   document.cookie

   # Or from Network tab, copy the token from request headers
   # Look for: x-bonduseraccesstoken, Authorization, etc.
   ```

2. **Use the extracted token directly:**
   ```bash
   export API_TOKEN="extracted_token_here"
   python your_script.py
   ```

3. **Document the manual token extraction process:**
   - Create a `get_token.md` file with step-by-step instructions
   - Include screenshots if possible
   - Note token expiration time

---

## 3. Endpoint Discovery Techniques

### Method 1: Browser DevTools (Most Reliable)

1. Open browser DevTools (F12)
2. Go to Network tab
3. Clear existing requests
4. Interact with the website
5. Look for XHR/Fetch requests
6. Right-click request → "Copy as cURL"
7. Test in terminal

### Method 2: Reverse Engineering JavaScript

Look for API configuration in page source:

```bash
# Download page HTML
curl -s "https://example.com/booking" > page.html

# Search for API patterns
grep -E 'api|endpoint|baseURL|fetch\(|axios\.' page.html

# Look in script tags
grep -oP '<script[^>]*src="[^"]*"' page.html
```

### Method 3: Common API Patterns

Try standard REST conventions:

```bash
# List all
GET /api/v1/resources

# Get by ID
GET /api/v1/resources/{id}

# Common auth endpoints
POST /api/auth/login
POST /api/auth/refresh
POST /auth/login
POST /oauth/token

# Common resource patterns
GET /api/v1/organizations/{orgId}/resources
GET /api/v1/venues/{venueId}/slots
GET /api/v1/spaces/{spaceId}/bookings
```

### Method 4: Systematic Exploration Script

Create an API exploration tool:

**Example: `explore_api.py`**

```python
#!/usr/bin/env python3
"""Systematically test API endpoints"""

import requests

BASE_URL = "https://api.example.com"

# Common endpoint patterns to test
PATTERNS = [
    "/v1/organizations/{id}",
    "/v1/venues/{id}",
    "/v1/resources",
    "/v1/resources/{id}",
    "/v1/facilities/{id}",
    "/v1/bookings",
    "/v1/slots",
]

def test_endpoint(url, auth=None):
    """Test if endpoint exists and returns data"""
    headers = {}
    if auth:
        headers['Authorization'] = f'Bearer {auth}'

    try:
        response = requests.get(url, headers=headers, timeout=5)
        return {
            'url': url,
            'status': response.status_code,
            'success': 200 <= response.status_code < 300,
            'content_type': response.headers.get('content-type', ''),
            'size': len(response.content)
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'error': str(e)
        }

def explore_api(org_id, facility_id, venue_id):
    """Test common patterns"""
    results = []

    for pattern in PATTERNS:
        # Replace placeholders
        url = BASE_URL + pattern
        url = url.replace('{id}', str(facility_id))
        url = url.replace('{orgId}', str(org_id))
        url = url.replace('{venueId}', str(venue_id))

        result = test_endpoint(url)
        results.append(result)

        status_symbol = "✓" if result.get('success') else "✗"
        print(f"{status_symbol} {result['status']} - {url}")

    return results
```

---

## 4. API vs Browser Automation Decision Matrix

### Use API When:

- API endpoints are publicly documented
- Authentication is straightforward (email/password, API keys)
- API returns structured data (JSON/XML)
- You need to make many requests (rate limits permitting)
- Real-time data is required
- You need to integrate with other systems
- The website's UI might change frequently

### Use Browser Automation When:

- No public API exists
- API requires complex OAuth/SSO that's hard to automate
- API is heavily rate-limited or blocked
- Website uses CAPTCHA or bot detection
- You need to interact with complex UI elements
- API documentation is missing or inaccurate
- You're doing one-off data collection

### Hybrid Approach (Best of Both Worlds):

1. **Use API for structured data:**
   - Facility information
   - Resource listings
   - Operating hours
   - Pricing

2. **Use browser automation for:**
   - Initial authentication (get session token)
   - Actions that require user interaction
   - Visual verification
   - Taking screenshots for users

**Example workflow:**
```python
# 1. Use browser to authenticate and get token
def get_session_token_via_browser():
    browser.open("https://example.com/login")
    browser.click("Login with Google")
    # ... handle OAuth flow ...
    token = browser.get_cookie('session_token')
    return token

# 2. Use API for data access
def get_availability_via_api(token, date):
    response = requests.get(
        'https://api.example.com/v1/slots',
        headers={'Authorization': f'Bearer {token}'},
        params={'date': date}
    )
    return response.json()
```

---

## 5. Implementation Checklist

### Phase 1: Research (Before Writing Code)

- [ ] Open browser DevTools and capture network requests
- [ ] Identify API base URL
- [ ] List all relevant endpoints
- [ ] Document authentication method
- [ ] Test endpoints with `curl`
- [ ] Verify data format (JSON structure)
- [ ] Check for rate limits
- [ ] Document any special headers required

### Phase 2: Minimal Viable Test

- [ ] Create `test_connection.py` for auth only
- [ ] Verify credentials work
- [ ] Test one simple endpoint
- [ ] Document any issues encountered
- [ ] Confirm token expiration time

### Phase 3: Build API Client

- [ ] Create API client class with base methods
- [ ] Implement authentication
- [ ] Add public endpoints first (no auth required)
- [ ] Test each endpoint independently
- [ ] Add authenticated endpoints
- [ ] Implement error handling
- [ ] Add retry logic for transient failures

### Phase 4: Build Business Logic

- [ ] Create high-level functions (e.g., `check_availability`)
- [ ] Parse and transform API responses
- [ ] Handle edge cases (closed days, overnight hours)
- [ ] Add filtering options
- [ ] Format output for users

### Phase 5: Add Fallback Mechanisms

- [ ] Implement browser automation fallback
- [ ] Add manual token extraction instructions
- [ ] Create health check function
- [ ] Add logging for debugging

### Phase 6: Documentation

- [ ] Create README with examples
- [ ] Document all endpoints
- [ ] Add troubleshooting section
- [ ] Include example responses
- [ ] Document authentication methods

---

## 6. Fallback Strategies

### Strategy 1: Graceful Degradation

```python
def check_availability(location, date):
    """Check availability with automatic fallback"""

    # Try API first
    try:
        if has_valid_token():
            return check_via_api(location, date)
    except APIError as e:
        logger.warning(f"API failed: {e}, falling back to browser")

    # Fall back to browser automation
    try:
        return check_via_browser(location, date)
    except BrowserError as e:
        logger.error(f"Browser automation failed: {e}")
        raise Exception("All methods failed")
```

### Strategy 2: Partial Data Access

```python
def get_facility_info(location):
    """Get as much data as possible"""

    result = {
        'location': location,
        'fields': [],
        'availability': None
    }

    # Get facility info (public API - no auth)
    try:
        result['fields'] = api.get_resources(location)
        result['operating_hours'] = api.get_hours(location)
    except Exception as e:
        logger.warning(f"Public API failed: {e}")

    # Get availability (requires auth)
    try:
        if has_auth():
            result['availability'] = api.get_slots(location, date)
        else:
            result['availability_note'] = "Requires authentication"
    except Exception as e:
        logger.warning(f"Authenticated API failed: {e}")

    return result
```

### Strategy 3: Cache and Update

```python
import json
from datetime import datetime, timedelta

CACHE_FILE = '.api_cache.json'
CACHE_DURATION = timedelta(hours=1)

def get_cached_data(key):
    """Get cached data if still valid"""
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)

        if key in cache:
            cached_time = datetime.fromisoformat(cache[key]['timestamp'])
            if datetime.now() - cached_time < CACHE_DURATION:
                return cache[key]['data']
    except:
        pass
    return None

def cache_data(key, data):
    """Cache data for future use"""
    try:
        cache = {}
        try:
            with open(CACHE_FILE) as f:
                cache = json.load(f)
        except:
            pass

        cache[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }

        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        logger.warning(f"Failed to cache: {e}")

def get_data_with_cache(key, fetch_func):
    """Try cache first, then fetch"""
    cached = get_cached_data(key)
    if cached:
        logger.info(f"Using cached data for {key}")
        return cached

    data = fetch_func()
    cache_data(key, data)
    return data
```

---

## 7. Common Pitfalls and Solutions

### Pitfall 1: Assuming API Endpoints Exist

**Problem:**
```python
# Writing code before verifying API exists
def get_slots(date):
    # This endpoint might not exist!
    response = requests.get(f'https://api.example.com/slots?date={date}')
    return response.json()
```

**Solution:**
```python
# Always verify first
# 1. Test with curl
# 2. Check response
# 3. Then write code

def get_slots(date):
    """Get slots - endpoint verified on 2026-02-01"""
    try:
        response = requests.get(
            f'https://api.example.com/slots',
            params={'date': date},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise APIError("Slots endpoint not available")
        raise
```

### Pitfall 2: Not Testing Authentication Separately

**Problem:**
```python
# Combining auth and data access in one big function
def check_availability(email, password, date):
    # If this fails, is it auth or data access?
    token = login(email, password)
    data = get_slots(token, date)
    return process(data)
```

**Solution:**
```python
# Separate concerns - test auth first
def test_auth():
    """Test authentication only"""
    token = login(email, password)
    assert token is not None
    print(f"✓ Auth successful: {token[:10]}...")

def test_simple_endpoint(token):
    """Test a simple endpoint"""
    response = api.get_user_profile(token)
    assert response['status'] == 'success'
    print("✓ API access confirmed")

# Only then build complex functions
def check_availability(date):
    token = get_cached_token() or login()
    return get_slots(token, date)
```

### Pitfall 3: Ignoring Authentication Method Complexity

**Problem:**
```python
# Assuming simple email/password auth
def login(email, password):
    response = requests.post('/auth/login', json={
        'email': email,
        'password': password
    })
    return response.json()['token']
# But what if they use OAuth, SSO, or SAML?
```

**Solution:**
```python
# Check auth method FIRST
# Document in README:

"""
## Authentication Methods

### Method 1: Email/Password (Direct Accounts)
export API_EMAIL=your@email.com
export API_PASSWORD=yourpassword

### Method 2: SSO (Google/GitHub)
1. Login via browser
2. Open DevTools → Application → Cookies
3. Copy session token
4. export API_TOKEN=your_token

See get_token.md for detailed instructions.
"""
```

### Pitfall 4: Not Handling Token Expiration

**Problem:**
```python
# Get token once, use forever
token = login()
# ... hours later ...
data = get_data(token)  # Token expired!
```

**Solution:**
```python
import time

class APIClient:
    def __init__(self):
        self.token = None
        self.token_expiry = 0

    def ensure_authenticated(self):
        """Ensure we have a valid token"""
        if not self.token or time.time() >= self.token_expiry:
            self.refresh_token()

    def refresh_token(self):
        """Get a new token"""
        response = self.login(email, password)
        self.token = response['access_token']
        # Set expiry (e.g., token valid for 1 hour)
        self.token_expiry = time.time() + 3600

    def get_data(self):
        """Always ensure auth before request"""
        self.ensure_authenticated()
        return self._make_request('/data')
```

### Pitfall 5: Over-Engineering Before Validation

**Problem:**
```python
# Building a complex client before verifying API works
class APIClient:
    def __init__(self, config):
        self.setup_connection_pool()
        self.setup_retry_logic()
        self.setup_caching()
        # ... 500 lines later ...
    # But does the API even exist?
```

**Solution:**
```python
# Start minimal, validate, then expand

# Step 1: Minimal test (10 lines)
import requests
response = requests.get('https://api.example.com/test')
print(response.json())

# Step 2: If it works, add auth (20 lines)
def login():
    return requests.post('/auth', json={'email': email, 'password': pw})

# Step 3: If auth works, build client (100 lines)
class APIClient:
    def __init__(self):
        self.base_url = 'https://api.example.com'

    def get(self, path):
        return requests.get(f'{self.base_url}{path}')

# Step 4: Add features incrementally
# - Error handling
# - Retry logic
# - Caching
# - Connection pooling
```

### Pitfall 6: Not Documenting the Discovery Process

**Problem:**
- You figure out the API structure
- Months later, you forget how you found it
- Someone else needs to maintain it
- No documentation exists

**Solution:**

Create an API discovery document as you go:

```markdown
# API Discovery Notes - 2026-02-01

## How I Found the API

1. Opened https://example.com/booking in Chrome
2. Opened DevTools (F12) → Network tab
3. Filtered by "Fetch/XHR"
4. Selected a date in the booking calendar
5. Saw request to: https://api.example.com/v1/slots?date=2026-02-01

## Authentication Discovery

1. Noticed header: x-user-token in requests
2. Logged in and checked Network tab
3. Found login endpoint: POST https://api.example.com/auth/login
4. Request body: {"email": "...", "password": "..."}
5. Response includes accessToken in credentials object

## Endpoints Discovered

### Public (no auth)
- GET /v1/facilities/{id} - Returns facility info
- GET /v1/resources - Lists all resources

### Authenticated
- GET /v1/slots?date=YYYY-MM-DD - Returns bookings
- POST /auth/login - Login

## Test Commands

# Test public endpoint
curl -s "https://api.example.com/v1/facilities/123" | jq

# Test auth
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}' | jq
```

---

## Quick Reference: Step-by-Step Process

### When Starting a New Integration:

1. **Open DevTools FIRST** (before writing any code)
   - Watch network requests
   - Identify API endpoints
   - Document authentication

2. **Test with `curl`**
   ```bash
   curl -s "https://api.example.com/endpoint" | jq
   ```

3. **Create minimal test script**
   ```python
   # test_connection.py
   import requests
   r = requests.get('https://api.example.com/test')
   print(r.json())
   ```

4. **Test authentication separately**
   ```python
   # test_auth.py
   token = login(email, password)
   print(f"Token: {token}")
   ```

5. **Document as you go**
   - Create README.md
   - List all endpoints
   - Show example requests/responses

6. **Build incrementally**
   - Start with one endpoint
   - Add error handling
   - Expand functionality

7. **Add fallback strategies**
   - Browser automation
   - Manual token extraction
   - Cached data

### Red Flags to Watch For:

- No network requests visible in DevTools (might be server-side rendered)
- All responses return HTML (no API exists)
- Authentication uses complex OAuth (hard to automate)
- Endpoints return 404 or 403 consistently
- Rate limiting after few requests
- API requires API keys you can't obtain

### When to Give Up on API:

- No API endpoints visible after thorough investigation
- Authentication requires human interaction (CAPTCHA, 2FA)
- API is internal-only (no public access)
- Terms of Service prohibit API access

**Then:** Use browser automation instead

---

## Tools and Resources

### Essential Tools:

1. **Browser DevTools**
   - Chrome DevTools (F12)
   - Firefox Developer Tools (F12)
   - Network tab for API discovery

2. **Command Line**
   ```bash
   # curl - Test HTTP requests
   curl -s -X GET "https://api.example.com/endpoint" | jq

   # jq - Format JSON output
   echo '{"key":"value"}' | jq

   # httpie - User-friendly HTTP client
   http GET https://api.example.com/endpoint
   ```

3. **Python Libraries**
   ```python
   import requests  # HTTP client
   import json      # JSON handling
   import logging   # Debug logging
   ```

4. **Browser Automation**
   ```bash
   # playwright - Modern browser automation
   pip install playwright
   playwright install

   # selenium - Traditional browser automation
   pip install selenium
   ```

### Testing Template:

```python
#!/usr/bin/env python3
"""
API Integration Test Template

Usage:
    1. Fill in BASE_URL and endpoints
    2. Test public endpoints first
    3. Add authentication
    4. Test authenticated endpoints
"""

import requests
import os
import json
from pprint import pprint

# Configuration
BASE_URL = "https://api.example.com"
EMAIL = os.environ.get('API_EMAIL')
PASSWORD = os.environ.get('API_PASSWORD')

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def test_public_endpoint(self):
        """Test an endpoint that doesn't require auth"""
        print("\n" + "="*60)
        print("Testing Public Endpoint")
        print("="*60)

        try:
            response = self.session.get(f"{BASE_URL}/v1/public/test")
            print(f"Status: {response.status_code}")
            print("Response:")
            pprint(response.json())
            return True
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False

    def test_authentication(self):
        """Test authentication"""
        print("\n" + "="*60)
        print("Testing Authentication")
        print("="*60)

        if not EMAIL or not PASSWORD:
            print("✗ Set API_EMAIL and API_PASSWORD environment variables")
            return False

        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json={'email': EMAIL, 'password': PASSWORD}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token') or data.get('token')
                print(f"✓ Login successful")
                print(f"Token: {self.token[:20]}..." if self.token else "No token")
                return True
            else:
                print(f"✗ Login failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def test_authenticated_endpoint(self):
        """Test an endpoint that requires authentication"""
        print("\n" + "="*60)
        print("Testing Authenticated Endpoint")
        print("="*60)

        if not self.token:
            print("✗ No authentication token available")
            return False

        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = self.session.get(
                f"{BASE_URL}/v1/protected/data",
                headers=headers
            )

            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✓ Request successful")
                print("Response:")
                pprint(response.json())
                return True
            else:
                print(f"✗ Request failed")
                print(response.text)
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n" + "="*60)
        print("API INTEGRATION TEST SUITE")
        print("="*60)

        results = {
            'public_endpoint': self.test_public_endpoint(),
            'authentication': self.test_authentication(),
            'authenticated_endpoint': self.test_authenticated_endpoint()
        }

        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        for test, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {test}")

        return all(results.values())

if __name__ == '__main__':
    tester = APITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
```

---

## Summary: The Golden Rules

1. **DevTools First, Code Later** - Always observe network traffic before writing integration code

2. **Test Auth Separately** - Verify authentication works before accessing data endpoints

3. **Start Minimal** - Test with curl, then minimal script, then full client

4. **Document Everything** - Future you (and others) will thank you

5. **Have a Fallback** - Browser automation when API is unavailable

6. **Verify Before Building** - Don't build a client for an API that doesn't exist

7. **Handle Token Expiration** - Refresh tokens automatically

8. **Test Incrementally** - One endpoint at a time, validate each before moving on

9. **Cache When Possible** - Reduce API calls, improve reliability

10. **Accept When API Isn't Available** - Sometimes browser automation is the only option

---

## Real-World Example: BondSports Integration

This document is based on actual experience integrating with BondSports API for Socceroof field availability.

### What Worked:

1. Started by inspecting network traffic in browser DevTools
2. Identified base URL: `https://api.bondsports.co`
3. Tested public endpoints with curl first
4. Created `test_connection.py` to verify auth separately
5. Built API client incrementally
6. Documented all endpoints in README
7. Added fallback for SSO authentication (manual token extraction)

### What Didn't Work:

1. Tried to guess API endpoints before verifying they existed
2. Combined authentication and data access testing (hard to debug)
3. Assumed certain endpoints existed (resulted in wasted time)

### Key Lessons:

1. **Always verify endpoints exist** before building integration
2. **Test authentication separately** from data access
3. **Document the discovery process** as you go
4. **Plan for SSO scenarios** (can't always automate login)
5. **Build fallback strategies** from the start

### Files Created:

- `/Users/gsiener/src/field-space/bondsports_api.py` - Main API client
- `/Users/gsiener/src/field-space/test_connection.py` - Auth testing
- `/Users/gsiener/src/field-space/explore_api.py` - Endpoint discovery
- `/Users/gsiener/src/field-space/README.md` - Complete documentation
- `/Users/gsiener/src/field-space/bondsports_checker.py` - Browser automation fallback

---

## Conclusion

Following these best practices will save hours of frustration when integrating with third-party APIs:

- Verify API exists before coding
- Test authentication independently
- Document as you discover
- Build incrementally
- Plan fallback strategies
- Accept limitations when necessary

Remember: **The best code is code you don't have to write because you verified the API works first.**
