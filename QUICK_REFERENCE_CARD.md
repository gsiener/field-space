# API Integration Quick Reference Card

Print this and keep it handy! 1-page reference for API integrations.

---

## The 3 Golden Rules

1. **DevTools First, Code Later** - Verify API exists before writing code
2. **Test Auth Separately** - Don't mix authentication with data access
3. **Start Minimal** - curl → basic script → full client

---

## Pre-Integration Checklist (5 minutes)

```bash
☐ Open browser DevTools (F12)
☐ Watch Network tab while using website
☐ Find API calls (filter by Fetch/XHR)
☐ Copy request as curl
☐ Test curl in terminal
☐ Document base URL and endpoints
```

**If no API found → Use browser automation instead**

---

## The 3-Step Validation

```bash
# Step 1: Does endpoint exist?
curl -s "https://api.example.com/v1/test" | jq
# Should return JSON (not HTML)

# Step 2: Can I authenticate?
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass"}'
# Should return token

# Step 3: Can I access data?
curl -s -H "Authorization: Bearer TOKEN" \
  "https://api.example.com/v1/data" | jq
# Should return data
```

**All 3 work? → Proceed with integration**
**Any fail? → Debug before writing code**

---

## Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 401 | Unauthorized | Check auth token/headers |
| 403 | Forbidden | Check permissions/token |
| 404 | Not Found | Verify endpoint exists |
| 429 | Rate Limited | Add delays/caching |
| 500 | Server Error | Check request format |

---

## Authentication Quick Debug

```python
# Test auth with debug output
import requests

response = requests.post(
    'https://api.example.com/auth/login',
    json={'email': 'test@example.com', 'password': 'pass'}
)

print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Body: {response.text}")

# Extract token
token = response.json().get('access_token')
print(f"Token: {token[:20]}...")
```

**If 401/403:**
- Check endpoint URL (compare with browser)
- Check payload format (email vs username?)
- Check required headers
- Verify credentials are correct

**If SSO/OAuth:**
- Don't automate - extract token manually
- Login via browser → DevTools → Copy token
- Document process in `get_token.md`

---

## Essential Headers to Check

Common auth headers (check in browser DevTools):
```
Authorization: Bearer {token}
x-api-key: {key}
x-auth-token: {token}
x-access-token: {token}
x-bonduseraccesstoken: {token}  (example from BondSports)
```

Common request headers:
```
Content-Type: application/json
User-Agent: Mozilla/5.0 ...
Accept: application/json
```

---

## Token Expiration Pattern

```python
import time
from datetime import datetime, timedelta

class APIClient:
    def __init__(self):
        self.token = None
        self.token_expiry = None

    def ensure_auth(self):
        """Call before every request"""
        if not self.token or datetime.now() >= self.token_expiry:
            self.refresh_token()

    def refresh_token(self):
        # Get new token
        self.token = self.login()
        self.token_expiry = datetime.now() + timedelta(hours=1)

    def get_data(self):
        self.ensure_auth()  # Always ensure auth first
        return requests.get(url, headers={'Authorization': f'Bearer {self.token}'})
```

---

## Retry Pattern

```python
from time import sleep

def request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"Retry {attempt+1}/{max_retries} in {wait}s")
                sleep(wait)
            else:
                raise
```

---

## Safe Data Extraction

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

# Usage - won't crash on missing keys
name = safe_get(data, 'user', 'profile', 'name', default='Unknown')
item_id = safe_get(data, 'items', 0, 'id', default=0)
```

---

## Browser DevTools Cheat Sheet

**Find API Requests:**
1. F12 (open DevTools)
2. Network tab
3. Filter: "Fetch/XHR"
4. Interact with website
5. Click request → Headers tab

**Copy as curl:**
- Right-click request → Copy → Copy as cURL
- Paste in terminal to test

**Find Auth Token:**
- Method 1: Network tab → Find API request → Headers → Look for Authorization
- Method 2: Application tab → Cookies → Find session cookie
- Method 3: Console tab → Run: `localStorage.getItem('auth_token')`

---

## Decision Tree: API vs Browser Automation

```
Start
  │
  ├─ Can you see API calls in DevTools? ─ No ──→ Use Browser Automation
  │                                      │
  │                                     Yes
  │                                      │
  ├─ Does curl return JSON? ─────────── No ──→ Use Browser Automation
  │                                      │
  │                                     Yes
  │                                      │
  ├─ Is authentication simple? ───────── No ──→ Extract token manually + API
  │   (email/password, API key)          │      OR Browser Automation
  │                                     Yes
  │                                      │
  └─ Use API ←───────────────────────────┘
```

---

## Error Message Decoder

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| "json.decoder.JSONDecodeError" | Endpoint returns HTML | Wrong URL - verify with DevTools |
| "KeyError: 'access_token'" | Token field has different name | Check response structure |
| "ConnectionError" | Network/timeout issue | Add timeout, retry logic |
| "401 Unauthorized" | Bad/missing auth | Check headers, verify token |
| "403 Forbidden" | Insufficient permissions | Check account permissions |
| "404 Not Found" | Endpoint doesn't exist | Verify URL with DevTools |
| "429 Too Many Requests" | Rate limited | Add delays, caching |
| "500 Server Error" | Bad request format | Check payload structure |

---

## Must-Have Environment Variables

```bash
# Set credentials
export API_EMAIL="your@email.com"
export API_PASSWORD="yourpassword"
export API_TOKEN="token_for_sso_accounts"

# Verify
echo $API_EMAIL

# Use in Python
import os
email = os.environ.get('API_EMAIL')
```

---

## Minimal Test Script Template

```python
#!/usr/bin/env python3
"""Minimal API test - start here"""
import requests
import os

BASE_URL = "https://api.example.com"

# Test 1: Public endpoint
try:
    r = requests.get(f"{BASE_URL}/v1/test")
    print(f"✓ Public endpoint works: {r.status_code}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: Authentication
email = os.environ.get('API_EMAIL')
password = os.environ.get('API_PASSWORD')

if email and password:
    try:
        r = requests.post(
            f"{BASE_URL}/auth/login",
            json={'email': email, 'password': password}
        )
        token = r.json().get('token')
        print(f"✓ Auth works: {token[:20]}...")

        # Test 3: Authenticated request
        r = requests.get(
            f"{BASE_URL}/v1/data",
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"✓ Data access works: {r.status_code}")
    except Exception as e:
        print(f"✗ Failed: {e}")
else:
    print("Set API_EMAIL and API_PASSWORD to test auth")
```

Save as `test_api.py`, then:
```bash
export API_EMAIL="your@email.com"
export API_PASSWORD="yourpassword"
python test_api.py
```

---

## Rate Limiting Quick Fix

```python
import time

# Add delay between requests
def get_data(endpoints):
    results = []
    for endpoint in endpoints:
        response = requests.get(endpoint)
        results.append(response.json())
        time.sleep(1)  # 1 second delay
    return results
```

---

## Cache Pattern (Simple)

```python
import json
from pathlib import Path
from datetime import datetime, timedelta

CACHE_FILE = Path('.api_cache.json')
CACHE_HOURS = 1

def get_cached(key):
    """Get cached data if still valid"""
    if not CACHE_FILE.exists():
        return None

    cache = json.loads(CACHE_FILE.read_text())
    if key not in cache:
        return None

    entry = cache[key]
    cached_time = datetime.fromisoformat(entry['time'])
    if datetime.now() - cached_time < timedelta(hours=CACHE_HOURS):
        return entry['data']
    return None

def save_cache(key, data):
    """Save data to cache"""
    cache = {}
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text())

    cache[key] = {
        'data': data,
        'time': datetime.now().isoformat()
    }

    CACHE_FILE.write_text(json.dumps(cache))

# Usage
data = get_cached('my_endpoint')
if not data:
    data = fetch_from_api()
    save_cache('my_endpoint', data)
```

---

## When to Stop and Reconsider

Stop if you see 3+ of these red flags:

- [ ] All endpoints return HTML (not JSON)
- [ ] Consistent 404 on logical endpoints
- [ ] No way to authenticate (or only OAuth you can't access)
- [ ] CAPTCHA or bot detection
- [ ] Heavy rate limiting (>10 requests/minute)
- [ ] Terms of Service prohibit API access
- [ ] Spent >2 hours with no working endpoint

**Consider:** Browser automation instead

---

## Essential Commands

```bash
# Test endpoint
curl -s "https://api.example.com/endpoint" | jq

# Test with auth
curl -s -H "Authorization: Bearer TOKEN" \
  "https://api.example.com/endpoint" | jq

# Test POST
curl -X POST "https://api.example.com/endpoint" \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' | jq

# Save response
curl -s "https://api.example.com/endpoint" > response.json

# Pretty print JSON
cat response.json | jq

# Install jq (if needed)
# Mac: brew install jq
# Ubuntu: sudo apt install jq
```

---

## Debugging Checklist

When something doesn't work:

1. [ ] Test with curl first
2. [ ] Check response is JSON (not HTML)
3. [ ] Compare with browser DevTools request
4. [ ] Verify endpoint URL is exact
5. [ ] Check all required headers
6. [ ] Verify token hasn't expired
7. [ ] Test authentication separately
8. [ ] Enable debug logging
9. [ ] Check for rate limiting
10. [ ] Try simpler endpoint first

---

## Time Estimates

- **Discovery (DevTools):** 30-60 min
- **Auth Testing:** 30-45 min
- **Basic API Client:** 1-2 hours
- **Full Integration:** 6-12 hours

**Time saved by validating first:** 4-8 hours

---

## Resources

**Documentation:**
- `API_INTEGRATION_CHECKLIST.md` - Full checklist
- `API_INTEGRATION_BEST_PRACTICES.md` - Detailed guide
- `API_TROUBLESHOOTING_GUIDE.md` - Debug help

**Tools:**
- Browser DevTools (F12)
- curl + jq for testing
- Python requests library
- Postman (optional GUI)

---

## Remember

**Never write integration code before verifying the API exists and works via browser DevTools and curl.**

**30 minutes of validation saves 4+ hours of debugging.**

---

© Based on real-world BondSports API integration experience
