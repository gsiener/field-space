# API Integration Troubleshooting Guide

A practical guide for debugging common API integration issues. Each section includes symptoms, diagnosis steps, and solutions.

---

## Table of Contents

1. [Authentication Failures](#1-authentication-failures)
2. [Endpoint Not Found (404)](#2-endpoint-not-found-404)
3. [Unauthorized (401/403)](#3-unauthorized-401403)
4. [Token Expiration Issues](#4-token-expiration-issues)
5. [Rate Limiting (429)](#5-rate-limiting-429)
6. [Malformed Response](#6-malformed-response)
7. [SSO/OAuth Integration](#7-ssooauth-integration)
8. [Network/Connection Issues](#8-networkconnection-issues)
9. [Data Parsing Errors](#9-data-parsing-errors)
10. [CORS Issues](#10-cors-issues)

---

## 1. Authentication Failures

### Symptoms

- Login request returns 401 or 403
- Response says "Invalid credentials"
- Token is None or empty
- Can't get past authentication step

### Diagnosis

```python
# Test authentication with debugging
import requests
import json

def debug_login(email, password):
    url = "https://api.example.com/auth/login"
    payload = {'email': email, 'password': password}

    print(f"Request URL: {url}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")

    response = requests.post(url, json=payload)

    print(f"\nResponse status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")

    return response

# Run it
debug_login("your@email.com", "yourpassword")
```

### Common Causes and Solutions

#### Cause 1: Wrong endpoint URL

**Check:**
```bash
# Test in browser DevTools - see exact endpoint used
# Compare with your code

# Try variations:
curl -X POST https://api.example.com/auth/login
curl -X POST https://api.example.com/v1/auth/login
curl -X POST https://api.example.com/login
curl -X POST https://api.example.com/auth
```

**Solution:** Use the exact endpoint from browser DevTools

#### Cause 2: Wrong payload format

**Check:**
```python
# API might expect different field names
payloads_to_try = [
    {'email': email, 'password': password},
    {'username': email, 'password': password},
    {'user': email, 'pass': password},
    {'login': email, 'password': password},
]

for payload in payloads_to_try:
    print(f"\nTrying: {payload}")
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
```

**Solution:** Match exact field names from browser DevTools

#### Cause 3: Missing headers

**Check:**
```python
# Add headers that browser sends
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Accept': 'application/json',
}

response = requests.post(url, json=payload, headers=headers)
```

**Solution:** Copy headers from browser DevTools request

#### Cause 4: SSO/OAuth authentication

**Symptoms:**
- Login page redirects to Google/GitHub/etc.
- No email/password fields
- Response returns OAuth flow URL

**Solution:**
Don't try to automate OAuth. Instead, extract token manually:

1. Login via browser
2. Open DevTools → Application → Cookies
3. Copy session token
4. Use token directly in code

Create `get_token.md`:
```markdown
# Manual Token Extraction

1. Open https://example.com in browser
2. Login with your account
3. Open DevTools (F12)
4. Go to Application → Cookies
5. Find cookie named 'session_token' or similar
6. Copy the value
7. Set environment variable:
   export API_TOKEN="paste_token_here"
```

---

## 2. Endpoint Not Found (404)

### Symptoms

- HTTP 404 response
- "Not Found" error
- Endpoint seems logical but doesn't exist

### Diagnosis

```bash
# Test endpoint exists
curl -v "https://api.example.com/v1/endpoint"

# Check response:
# - 404 = endpoint doesn't exist
# - 401 = endpoint exists but needs auth
# - 200 = endpoint works
```

### Common Causes and Solutions

#### Cause 1: Endpoint doesn't actually exist

**Never assume an endpoint exists without testing!**

**Diagnosis:**
```bash
# Open browser DevTools
# Interact with website
# Watch Network tab for actual API calls
# Copy exact URLs used
```

**Solution:**
Use only endpoints you've verified exist via browser DevTools

#### Cause 2: Wrong API version

**Check:**
```bash
# Try different versions
curl "https://api.example.com/v1/endpoint"
curl "https://api.example.com/v2/endpoint"
curl "https://api.example.com/endpoint"
```

**Solution:** Use version from browser DevTools

#### Cause 3: Wrong resource ID format

**Check:**
```bash
# Try different ID formats
curl "https://api.example.com/v1/resources/123"      # integer
curl "https://api.example.com/v1/resources/abc123"   # string
curl "https://api.example.com/v1/resources/resource-123"  # slug
```

**Solution:** Match ID format from working examples

#### Cause 4: Missing required query parameters

**Check:**
```bash
# Endpoint might require parameters
curl "https://api.example.com/v1/slots"
# 404 ✗

curl "https://api.example.com/v1/slots?date=2026-02-01"
# 200 ✓
```

**Solution:** Add required parameters from browser examples

---

## 3. Unauthorized (401/403)

### Symptoms

- HTTP 401 (Unauthorized) or 403 (Forbidden)
- Have a token but still can't access endpoint
- Authentication worked but data access fails

### Diagnosis

```python
# Test with detailed debugging
def test_authenticated_request(token, endpoint):
    headers = {'Authorization': f'Bearer {token}'}

    print(f"Token: {token[:20]}...")
    print(f"Endpoint: {endpoint}")
    print(f"Headers: {headers}")

    response = requests.get(
        f"https://api.example.com{endpoint}",
        headers=headers
    )

    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")

    return response

test_authenticated_request(token, "/v1/data")
```

### Common Causes and Solutions

#### Cause 1: Wrong header name

**Check browser DevTools for exact header name:**
- `Authorization: Bearer TOKEN`
- `x-auth-token: TOKEN`
- `x-api-key: TOKEN`
- `x-bonduseraccesstoken: TOKEN` (BondSports example)

**Solution:**
```python
# Use exact header name from browser
headers = {
    'x-bonduseraccesstoken': access_token,
    'x-bonduseridtoken': id_token,
}
```

#### Cause 2: Token expired

**Check:**
```python
# Token might have expiration
import time
import jwt  # if JWT token

# Try to decode (if JWT)
try:
    decoded = jwt.decode(token, options={"verify_signature": False})
    exp = decoded.get('exp')
    if exp:
        expired = exp < time.time()
        print(f"Token expired: {expired}")
except:
    print("Not a JWT token")
```

**Solution:** Refresh token before it expires

```python
class APIClient:
    def __init__(self):
        self.token = None
        self.token_expiry = 0

    def ensure_auth(self):
        if not self.token or time.time() >= self.token_expiry:
            self.refresh_token()

    def get_data(self):
        self.ensure_auth()
        # ... make request
```

#### Cause 3: Multiple tokens required

Some APIs need multiple auth values:

**Solution:**
```python
# Example from BondSports
headers = {
    'x-bonduseraccesstoken': self.access_token,
    'x-bonduseridtoken': self.id_token,
    'x-bonduserusername': self.username,
}
```

#### Cause 4: Insufficient permissions

**Symptoms:**
- Get 403 (forbidden) instead of 401
- Token is valid but user lacks permission

**Solution:**
- Verify account has necessary permissions
- Check if endpoint requires admin/special role
- May need different account type

---

## 4. Token Expiration Issues

### Symptoms

- Works initially, fails after some time
- Error: "Token expired" or "Invalid token"
- Need to login again frequently

### Diagnosis

```python
# Test token lifetime
import time

token = login()
print(f"Got token at: {time.time()}")

# Wait 1 hour
time.sleep(3600)

# Try to use token
response = make_request(token)
print(f"After 1 hour: {response.status_code}")
```

### Solution 1: Automatic token refresh

```python
import time
from datetime import datetime, timedelta

class APIClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

    def login(self, email, password):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={'email': email, 'password': password}
        )
        data = response.json()

        # Store tokens
        self.access_token = data['credentials']['accessToken']
        self.refresh_token = data['credentials']['refreshToken']

        # Calculate expiry (usually 1 hour)
        self.token_expiry = datetime.now() + timedelta(hours=1)

    def refresh_auth(self):
        """Refresh access token"""
        response = requests.post(
            f"{self.base_url}/auth/refresh",
            json={'refreshToken': self.refresh_token}
        )
        data = response.json()

        self.access_token = data['credentials']['accessToken']
        self.token_expiry = datetime.now() + timedelta(hours=1)

    def ensure_authenticated(self):
        """Make sure we have a valid token"""
        if not self.access_token or datetime.now() >= self.token_expiry:
            if self.refresh_token:
                self.refresh_auth()
            else:
                raise Exception("No valid token, please login")

    def get_data(self, endpoint):
        """Always ensure auth before request"""
        self.ensure_authenticated()
        return requests.get(
            f"{self.base_url}{endpoint}",
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
```

### Solution 2: Token caching

```python
import json
import os
from pathlib import Path
from datetime import datetime

TOKEN_CACHE_FILE = Path.home() / '.api_tokens.json'

def save_token(service_name, token_data):
    """Save token to disk"""
    cache = {}
    if TOKEN_CACHE_FILE.exists():
        cache = json.loads(TOKEN_CACHE_FILE.read_text())

    cache[service_name] = {
        'token': token_data,
        'timestamp': datetime.now().isoformat()
    }

    TOKEN_CACHE_FILE.write_text(json.dumps(cache))

def load_token(service_name, max_age_hours=1):
    """Load token from disk if still valid"""
    if not TOKEN_CACHE_FILE.exists():
        return None

    cache = json.loads(TOKEN_CACHE_FILE.read_text())
    if service_name not in cache:
        return None

    entry = cache[service_name]
    timestamp = datetime.fromisoformat(entry['timestamp'])
    age = datetime.now() - timestamp

    if age.total_seconds() / 3600 > max_age_hours:
        return None  # Too old

    return entry['token']
```

---

## 5. Rate Limiting (429)

### Symptoms

- HTTP 429 response
- Error: "Too many requests"
- Works fine initially, then fails
- "Rate limit exceeded"

### Diagnosis

```python
# Test rate limits
import time

for i in range(100):
    response = requests.get(endpoint)
    print(f"Request {i}: {response.status_code}")

    if response.status_code == 429:
        print(f"Rate limited after {i} requests")
        headers = dict(response.headers)
        print(f"Rate limit headers: {headers}")
        break

    time.sleep(0.1)  # Small delay
```

### Common Rate Limit Headers

```
X-RateLimit-Limit: 100        # Max requests per period
X-RateLimit-Remaining: 50     # Requests left
X-RateLimit-Reset: 1643723400 # When limit resets (Unix timestamp)
Retry-After: 60               # Seconds to wait
```

### Solution 1: Respect rate limits

```python
import time
from datetime import datetime

class RateLimitedAPI:
    def __init__(self):
        self.requests_made = 0
        self.rate_limit = 100  # per hour
        self.reset_time = None

    def _check_rate_limit(self, response):
        """Extract rate limit info from response"""
        headers = response.headers

        if 'X-RateLimit-Remaining' in headers:
            remaining = int(headers['X-RateLimit-Remaining'])
            if remaining < 10:
                print(f"Warning: Only {remaining} requests remaining")

        if 'X-RateLimit-Reset' in headers:
            reset = int(headers['X-RateLimit-Reset'])
            self.reset_time = datetime.fromtimestamp(reset)

        if response.status_code == 429:
            retry_after = int(headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            return True

        return False

    def request(self, url):
        """Make request with rate limit handling"""
        response = requests.get(url)

        if self._check_rate_limit(response):
            # We were rate limited, retry
            response = requests.get(url)

        self.requests_made += 1
        return response
```

### Solution 2: Add delays between requests

```python
import time

def make_requests_with_delay(endpoints, delay=1):
    """Make requests with delay to avoid rate limiting"""
    results = []

    for i, endpoint in enumerate(endpoints):
        print(f"Request {i+1}/{len(endpoints)}")

        response = requests.get(endpoint)
        results.append(response.json())

        if i < len(endpoints) - 1:  # Don't wait after last request
            time.sleep(delay)

    return results
```

### Solution 3: Implement caching

```python
import json
from pathlib import Path
from datetime import datetime, timedelta

class CachedAPI:
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _cache_key(self, endpoint):
        """Generate cache filename"""
        return self.cache_dir / f"{endpoint.replace('/', '_')}.json"

    def _is_cache_valid(self, cache_file, max_age_minutes=60):
        """Check if cache is still valid"""
        if not cache_file.exists():
            return False

        age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return age < timedelta(minutes=max_age_minutes)

    def get(self, endpoint):
        """Get data with caching"""
        cache_file = self._cache_key(endpoint)

        # Return cached data if valid
        if self._is_cache_valid(cache_file):
            print(f"Using cached data for {endpoint}")
            return json.loads(cache_file.read_text())

        # Fetch fresh data
        print(f"Fetching fresh data for {endpoint}")
        response = requests.get(f"{self.base_url}{endpoint}")
        data = response.json()

        # Cache it
        cache_file.write_text(json.dumps(data))

        return data
```

---

## 6. Malformed Response

### Symptoms

- `json.decoder.JSONDecodeError`
- Response is HTML instead of JSON
- Response is empty
- Response format doesn't match expected structure

### Diagnosis

```python
def debug_response(url):
    response = requests.get(url)

    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Content length: {len(response.content)}")
    print(f"\nFirst 500 chars of response:")
    print(response.text[:500])

    # Try to parse as JSON
    try:
        data = response.json()
        print(f"\n✓ Valid JSON")
        print(f"Keys: {list(data.keys())}")
    except:
        print(f"\n✗ Not valid JSON")
```

### Common Causes and Solutions

#### Cause 1: Endpoint returns HTML error page

**Symptoms:**
```
Response starts with: <!DOCTYPE html>
```

**Solution:**
Wrong endpoint - verify URL with browser DevTools

#### Cause 2: Empty response

**Solution:**
```python
def safe_json_parse(response):
    if not response.text:
        return None

    try:
        return response.json()
    except json.JSONDecodeError:
        print(f"Failed to parse JSON: {response.text[:200]}")
        return None
```

#### Cause 3: Response wrapped in extra structure

**Check:**
```python
# Response might be:
{"data": {"actual": "data"}}  # Wrapped
# Instead of:
{"actual": "data"}  # Direct

# Solution:
def unwrap_response(response):
    data = response.json()
    if 'data' in data:
        return data['data']
    return data
```

---

## 7. SSO/OAuth Integration

### Problem

Service uses Google/GitHub/Facebook login - hard to automate

### Diagnosis

**Signs you have SSO:**
- Login button says "Sign in with Google"
- Redirects to accounts.google.com or github.com
- No email/password fields
- OAuth consent screen appears

### Solution: Manual Token Extraction

Create `get_token.md`:

```markdown
# Getting Your Session Token

Since this service uses SSO (Google login), you need to manually extract your session token.

## Steps

1. **Login via Browser**
   - Go to https://example.com
   - Click "Sign in with Google"
   - Complete the login flow

2. **Open DevTools**
   - Press F12 (or Cmd+Option+I on Mac)
   - Go to "Network" tab
   - Refresh the page

3. **Find API Request**
   - Look for a request to `api.example.com`
   - Click on it
   - Go to "Headers" tab

4. **Copy Token**
   - Look for header like:
     - `Authorization: Bearer abc123...`
     - `x-auth-token: abc123...`
     - `x-access-token: abc123...`
   - Copy the token value (the part after "Bearer " or the full value)

5. **Set Environment Variable**
   ```bash
   export API_TOKEN="paste_your_token_here"
   ```

6. **Test It**
   ```bash
   python test_connection.py
   ```

## Token Expiration

Tokens typically expire after:
- 1 hour (most common)
- 24 hours (some services)
- 7 days (rare)

When you get authentication errors, repeat these steps to get a fresh token.

## Alternative: Extract from Cookies

Sometimes the token is in cookies instead of headers:

1. Open DevTools → Application → Cookies
2. Find cookie named `session`, `auth_token`, etc.
3. Copy the value
4. Export: `export API_TOKEN="cookie_value"`
```

### Automated Token Extraction (Advanced)

```python
# Use browser automation to get token
from playwright.sync_api import sync_playwright

def get_token_via_browser():
    """Login via browser automation and extract token"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Go to login page
        page.goto("https://example.com/login")

        # Click SSO button
        page.click("text=Sign in with Google")

        # Wait for user to complete OAuth flow
        print("Please complete the login in the browser...")
        page.wait_for_url("**/dashboard", timeout=120000)  # 2 minutes

        # Extract token from cookies or localStorage
        cookies = page.context.cookies()
        for cookie in cookies:
            if 'token' in cookie['name'].lower():
                token = cookie['value']
                print(f"Found token: {token[:20]}...")
                browser.close()
                return token

        # Or from localStorage
        token = page.evaluate("localStorage.getItem('auth_token')")
        browser.close()
        return token
```

---

## 8. Network/Connection Issues

### Symptoms

- Connection timeout
- Connection refused
- SSL/Certificate errors
- No route to host

### Diagnosis

```python
import requests
from requests.exceptions import (
    ConnectionError,
    Timeout,
    SSLError,
    RequestException
)

def diagnose_connection(url):
    try:
        response = requests.get(url, timeout=10)
        print(f"✓ Connection successful: {response.status_code}")
    except Timeout:
        print("✗ Connection timeout - server too slow or not responding")
    except ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print("Possible causes:")
        print("  - Wrong URL")
        print("  - Server is down")
        print("  - Network issue")
    except SSLError as e:
        print(f"✗ SSL error: {e}")
        print("Possible causes:")
        print("  - Invalid certificate")
        print("  - Certificate expired")
    except RequestException as e:
        print(f"✗ Request error: {e}")

diagnose_connection("https://api.example.com/test")
```

### Solutions

#### Solution 1: Increase timeout

```python
# Default timeout might be too short
response = requests.get(url, timeout=30)  # 30 seconds
```

#### Solution 2: Retry logic

```python
from time import sleep

def request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except (ConnectionError, Timeout) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                sleep(wait_time)
            else:
                raise
```

#### Solution 3: SSL verification (development only)

```python
# ONLY for development/testing - NOT for production
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

response = requests.get(url, verify=False)
```

---

## 9. Data Parsing Errors

### Symptoms

- `KeyError: 'expected_key'`
- `AttributeError: 'NoneType' has no attribute`
- Data structure different than expected

### Diagnosis

```python
def explore_response_structure(response_data, prefix=""):
    """Recursively explore response structure"""
    if isinstance(response_data, dict):
        print(f"{prefix}Dict with keys:")
        for key in response_data.keys():
            value = response_data[key]
            print(f"{prefix}  {key}: {type(value).__name__}")
            if isinstance(value, (dict, list)):
                explore_response_structure(value, prefix + "  ")
    elif isinstance(response_data, list):
        print(f"{prefix}List with {len(response_data)} items")
        if response_data:
            print(f"{prefix}First item type: {type(response_data[0]).__name__}")
            explore_response_structure(response_data[0], prefix + "  ")

# Use it
response = requests.get(url)
data = response.json()
explore_response_structure(data)
```

### Solution: Safe data extraction

```python
def safe_get(data, *keys, default=None):
    """Safely extract nested values"""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        elif isinstance(result, list) and isinstance(key, int):
            result = result[key] if key < len(result) else None
        else:
            return default

        if result is None:
            return default

    return result

# Usage
data = response.json()

# Instead of: data['user']['profile']['name']
name = safe_get(data, 'user', 'profile', 'name', default='Unknown')

# Instead of: data['items'][0]['id']
item_id = safe_get(data, 'items', 0, 'id', default=0)
```

---

## 10. CORS Issues

### Symptoms

- Error: "CORS policy blocked"
- Works in curl/Postman but fails in browser
- "No 'Access-Control-Allow-Origin' header"

### Understanding CORS

CORS (Cross-Origin Resource Sharing) is a browser security feature. It only affects:
- JavaScript running in a browser
- Requests to a different domain than the page

It does NOT affect:
- curl
- Postman
- Python scripts
- Backend services

### Solution

**If you're building a web app:**
- API must send CORS headers
- Can't fix from client side
- Need to:
  - Ask API provider to enable CORS
  - Use a proxy server
  - Move logic to backend

**If you're writing a script:**
- CORS doesn't apply
- Use Python/Node.js directly
- Don't use browser JavaScript

---

## Emergency Debugging Checklist

When nothing works, go through this:

- [ ] Verified endpoint exists via browser DevTools
- [ ] Tested with curl in terminal
- [ ] Checked response is JSON (not HTML)
- [ ] Verified authentication method
- [ ] Copied exact headers from browser
- [ ] Checked for required query parameters
- [ ] Verified token hasn't expired
- [ ] Checked for rate limiting
- [ ] Tested with simple working endpoint first
- [ ] Enabled debug logging
- [ ] Checked API documentation (if exists)
- [ ] Searched for error message online
- [ ] Tried different API version
- [ ] Verified network connectivity

---

## Debugging Tools

### Python logging

```python
import logging
import http.client as http_client

# Enable debug logging
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# Now all requests will show detailed debug info
response = requests.get(url)
```

### Requests session with logging

```python
import requests

class LoggedSession(requests.Session):
    def request(self, method, url, **kwargs):
        print(f"\n{'='*60}")
        print(f"{method} {url}")
        if 'headers' in kwargs:
            print(f"Headers: {kwargs['headers']}")
        if 'json' in kwargs:
            print(f"JSON: {kwargs['json']}")
        if 'params' in kwargs:
            print(f"Params: {kwargs['params']}")

        response = super().request(method, url, **kwargs)

        print(f"Response: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text[:500]}")
        print(f"{'='*60}\n")

        return response

# Use it
session = LoggedSession()
response = session.get(url)
```

---

## Getting Help

When asking for help, include:

1. **What you're trying to do**
   - "Check availability for sports facility"

2. **What you've tried**
   - "Tested endpoint with curl - works"
   - "Same request in Python - fails"

3. **Full error message**
   ```
   requests.exceptions.HTTPError: 401 Client Error: Unauthorized
   ```

4. **Code that demonstrates the issue**
   ```python
   response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
   # Returns 401
   ```

5. **What you've already checked**
   - Token is valid
   - Endpoint exists
   - Headers match browser

This will help others help you faster!

---

## Summary

**Most Common Issues (90% of problems):**

1. **Endpoint doesn't exist** - Always verify with browser DevTools first
2. **Wrong authentication header** - Copy exact header name from browser
3. **Token expired** - Implement auto-refresh
4. **Wrong endpoint URL** - Match exactly from browser
5. **Missing required parameters** - Check browser request

**Debug Process:**

1. Test with curl first
2. Enable debug logging
3. Compare with browser DevTools
4. Test authentication separately
5. Start with simple endpoint
6. Add complexity incrementally

**Remember:** 95% of API integration issues can be avoided by verifying the API exists and works via browser DevTools BEFORE writing code.
