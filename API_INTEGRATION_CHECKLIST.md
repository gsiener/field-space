# API Integration Checklist

A quick reference guide for integrating with third-party APIs. Print this and check off items as you go.

## Phase 1: Discovery (DO THIS FIRST!)

### Before Writing Any Code:

- [ ] Open the website in Chrome/Firefox
- [ ] Open DevTools (F12) → Network tab
- [ ] Filter by "Fetch/XHR" or "API"
- [ ] Clear network log
- [ ] Interact with the website (click buttons, select dates, etc.)
- [ ] Look for API calls in the Network panel
- [ ] Right-click interesting requests → "Copy as cURL"
- [ ] Test the curl command in terminal
- [ ] Document the base URL (e.g., `https://api.example.com`)

### API Verification:

- [ ] Identified at least one working endpoint
- [ ] Response is JSON/XML (not HTML)
- [ ] Response contains structured data
- [ ] Endpoint returns consistent data format
- [ ] Error messages are JSON (not HTML error pages)

### If No API Found:

- [ ] Checked all XHR/Fetch requests
- [ ] Looked in page source for API URLs
- [ ] Tried common REST patterns (`/api/v1/`, `/v1/`, etc.)
- [ ] Checked for GraphQL endpoint (`/graphql`)
- [ ] Decision: Use browser automation instead

---

## Phase 2: Authentication Testing

### Identify Auth Method:

- [ ] Checked Network tab for auth-related headers
- [ ] Looked for: `Authorization`, `x-api-key`, `x-auth-token`, etc.
- [ ] Identified login endpoint (e.g., `POST /auth/login`)
- [ ] Documented auth method (email/password, API key, OAuth, SSO)

### For Email/Password Auth:

- [ ] Created test account
- [ ] Tested login with curl:
  ```bash
  curl -X POST https://api.example.com/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"pass123"}'
  ```
- [ ] Verified response contains token
- [ ] Tested token with a simple endpoint
- [ ] Documented token location in response (e.g., `credentials.accessToken`)

### For OAuth/SSO Auth:

- [ ] Documented the OAuth provider (Google, GitHub, etc.)
- [ ] Created `get_token.md` with manual extraction instructions
- [ ] Tested extracting token from browser DevTools
- [ ] Verified extracted token works with API
- [ ] Documented token expiration time

### Create Test Script:

- [ ] Created `test_connection.py` or similar
- [ ] Test only authentication (no data access yet)
- [ ] Verified script can get a valid token
- [ ] Run test and confirm it works:
  ```bash
  python test_connection.py
  ```

---

## Phase 3: Endpoint Documentation

### Document Each Endpoint:

For each endpoint discovered, document:

- [ ] HTTP method (GET, POST, PUT, DELETE)
- [ ] Full URL path
- [ ] Query parameters
- [ ] Request headers required
- [ ] Request body format (if POST/PUT)
- [ ] Response format
- [ ] Authentication required? (yes/no)
- [ ] Example curl command

### Create API Documentation:

- [ ] Create README.md or API_DOCS.md
- [ ] List base URL
- [ ] Separate public vs authenticated endpoints
- [ ] Include example requests for each endpoint
- [ ] Include example responses
- [ ] Document any special headers or parameters

### Example Documentation Format:

```markdown
## Endpoints

### Public Endpoints (no auth required)

#### GET /v1/resources
Returns list of all resources

**Example:**
curl -s "https://api.example.com/v1/resources" | jq

**Response:**
{
  "data": [
    {"id": 1, "name": "Resource 1"},
    {"id": 2, "name": "Resource 2"}
  ]
}

### Authenticated Endpoints

#### GET /v1/slots
Returns booking slots

**Requires:** Authorization header

**Example:**
curl -s -H "Authorization: Bearer TOKEN" \
  "https://api.example.com/v1/slots?date=2026-02-01" | jq
```

---

## Phase 4: Build API Client

### Minimal API Client:

- [ ] Create API client file (e.g., `api_client.py`)
- [ ] Define base URL constant
- [ ] Create API class with `__init__` method
- [ ] Add authentication method (login/set token)
- [ ] Test authentication works

### Add Public Endpoints First:

- [ ] Implement one public endpoint method
- [ ] Test it works without authentication
- [ ] Add error handling
- [ ] Add logging/debugging output
- [ ] Test with real API

### Add Authenticated Endpoints:

- [ ] Implement method to add auth headers
- [ ] Add one authenticated endpoint method
- [ ] Test with valid token
- [ ] Test with invalid token (verify error handling)
- [ ] Add remaining authenticated endpoints one by one

### Error Handling:

- [ ] Handle network errors (timeout, connection refused)
- [ ] Handle HTTP errors (404, 500, etc.)
- [ ] Handle authentication errors (401, 403)
- [ ] Handle rate limiting (429)
- [ ] Handle invalid responses (malformed JSON)
- [ ] Add retry logic for transient failures

---

## Phase 5: Build Business Logic

### High-Level Functions:

- [ ] Create user-facing functions (e.g., `check_availability`)
- [ ] Parse and transform API responses
- [ ] Handle edge cases (null values, missing data)
- [ ] Add data validation
- [ ] Format output for users

### Data Processing:

- [ ] Parse dates/times correctly
- [ ] Handle timezone conversions if needed
- [ ] Calculate derived data (e.g., available time blocks)
- [ ] Filter and sort results
- [ ] Format output (tables, JSON, etc.)

### Testing:

- [ ] Test with valid inputs
- [ ] Test with invalid inputs
- [ ] Test edge cases (empty results, errors)
- [ ] Test with different date/time formats
- [ ] Verify calculations are correct

---

## Phase 6: Fallback Strategies

### Token Expiration:

- [ ] Implement token refresh logic
- [ ] Store token expiration time
- [ ] Automatically refresh before expiration
- [ ] Handle refresh failures gracefully

### Caching:

- [ ] Implement simple file-based cache
- [ ] Set appropriate cache duration
- [ ] Add cache invalidation logic
- [ ] Test cache hit/miss scenarios

### Browser Automation Fallback:

- [ ] Install browser automation tool (playwright/selenium)
- [ ] Create fallback script
- [ ] Test browser automation independently
- [ ] Add automatic fallback when API fails
- [ ] Document when to use each method

---

## Phase 7: Documentation

### README.md:

- [ ] Project description
- [ ] Installation instructions
- [ ] Configuration (environment variables)
- [ ] Usage examples
- [ ] API endpoints list
- [ ] Troubleshooting section
- [ ] Known limitations

### Code Documentation:

- [ ] Docstrings for all functions
- [ ] Type hints (Python) or JSDoc (JavaScript)
- [ ] Inline comments for complex logic
- [ ] Example usage in docstrings

### User Documentation:

- [ ] Quick start guide
- [ ] Authentication setup instructions
- [ ] Common use cases with examples
- [ ] FAQ section
- [ ] Error messages and solutions

---

## Phase 8: Testing and Validation

### Unit Tests:

- [ ] Test authentication
- [ ] Test each endpoint method
- [ ] Test error handling
- [ ] Test data parsing
- [ ] Test edge cases

### Integration Tests:

- [ ] Test full workflow (auth → data access → processing)
- [ ] Test with real API
- [ ] Test fallback mechanisms
- [ ] Test cache behavior

### Manual Testing:

- [ ] Run all examples from README
- [ ] Test with different inputs
- [ ] Verify output is correct
- [ ] Check error messages are helpful
- [ ] Test on clean environment

---

## Common Red Flags

Stop and reconsider if you see:

- [ ] All endpoints return HTML instead of JSON
- [ ] Consistent 404 errors on logical endpoints
- [ ] No authentication method discovered
- [ ] API requires credentials you can't obtain
- [ ] Heavy rate limiting after few requests
- [ ] CAPTCHA or bot detection
- [ ] Terms of Service prohibit API access
- [ ] OAuth requires credentials you don't have

**If 3+ red flags:** Consider browser automation instead of API

---

## Decision Matrix: API vs Browser Automation

### Use API if:

- [ ] Endpoints return JSON/structured data
- [ ] Authentication is straightforward
- [ ] Documentation exists (official or discovered)
- [ ] No rate limiting (or acceptable limits)
- [ ] No CAPTCHA or bot detection
- [ ] Faster than browser automation
- [ ] More reliable/maintainable

### Use Browser Automation if:

- [ ] No API exists or not discoverable
- [ ] Complex authentication (OAuth with no access)
- [ ] Heavy rate limiting on API
- [ ] CAPTCHA or bot detection on API
- [ ] Need to interact with complex UI
- [ ] Visual verification required
- [ ] One-time data collection

### Use Hybrid Approach if:

- [ ] API exists but auth is complex → browser for auth, API for data
- [ ] Some data via API, some requires UI → use both
- [ ] Need screenshots for verification → API + browser screenshots

---

## Quick Command Reference

### Testing Endpoints:

```bash
# Test GET endpoint
curl -s "https://api.example.com/endpoint" | jq

# Test with query parameters
curl -s "https://api.example.com/endpoint?param=value" | jq

# Test POST endpoint
curl -X POST "https://api.example.com/endpoint" \
  -H "Content-Type: application/json" \
  -d '{"key":"value"}' | jq

# Test with authentication
curl -s -H "Authorization: Bearer TOKEN" \
  "https://api.example.com/endpoint" | jq

# Save response to file
curl -s "https://api.example.com/endpoint" > response.json
```

### Environment Variables:

```bash
# Set credentials
export API_EMAIL="your@email.com"
export API_PASSWORD="yourpassword"
export API_TOKEN="your_token_here"

# Verify they're set
echo $API_EMAIL
```

### Python Quick Test:

```python
import requests
import os

# Test endpoint
response = requests.get('https://api.example.com/test')
print(response.json())

# Test with auth
token = os.environ.get('API_TOKEN')
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://api.example.com/data', headers=headers)
print(response.json())
```

---

## Time Estimates

Typical time for each phase (for moderately complex API):

- **Phase 1 (Discovery):** 30-60 minutes
- **Phase 2 (Auth Testing):** 30-45 minutes
- **Phase 3 (Documentation):** 15-30 minutes
- **Phase 4 (API Client):** 1-2 hours
- **Phase 5 (Business Logic):** 2-4 hours
- **Phase 6 (Fallbacks):** 1-2 hours
- **Phase 7 (Documentation):** 30-60 minutes
- **Phase 8 (Testing):** 1-2 hours

**Total:** 6-12 hours for complete integration

**Time saved by following this checklist:** 4-8 hours (avoided dead ends and rework)

---

## Critical Success Factors

The most important items to get right:

1. **Verify API exists before coding** (Phase 1)
2. **Test authentication separately** (Phase 2)
3. **Document endpoints as you discover them** (Phase 3)
4. **Start minimal, build incrementally** (Phase 4)
5. **Handle token expiration** (Phase 6)
6. **Have a fallback strategy** (Phase 6)

**If you skip Phase 1-2, you'll likely waste hours debugging non-existent endpoints.**

---

## Quick Start Template

Copy this into a new file to start quickly:

```python
#!/usr/bin/env python3
"""
API Integration Quick Start Template

1. Fill in BASE_URL
2. Test authentication
3. Add endpoints one by one
"""

import requests
import os
import json

BASE_URL = "https://api.example.com"

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def login(self, email, password):
        """Test authentication"""
        response = self.session.post(
            f"{BASE_URL}/auth/login",
            json={'email': email, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data.get('access_token')
        return self.token

    def _get_headers(self):
        """Get headers with auth token"""
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}

    def get_data(self, endpoint):
        """Generic GET request"""
        response = self.session.get(
            f"{BASE_URL}{endpoint}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

# Test it
if __name__ == '__main__':
    client = APIClient()

    # Test auth
    email = os.environ.get('API_EMAIL')
    password = os.environ.get('API_PASSWORD')

    if email and password:
        token = client.login(email, password)
        print(f"✓ Logged in: {token[:20]}...")

        # Test endpoint
        data = client.get_data('/v1/test')
        print(f"✓ Data retrieved: {data}")
    else:
        print("Set API_EMAIL and API_PASSWORD environment variables")
```

---

## Final Checklist

Before considering the integration complete:

- [ ] All endpoints documented
- [ ] Authentication tested and working
- [ ] Error handling implemented
- [ ] Fallback strategy in place
- [ ] README with examples written
- [ ] Code tested manually
- [ ] Token expiration handled
- [ ] Rate limiting considered
- [ ] Caching implemented (if appropriate)
- [ ] Logging added for debugging
- [ ] Environment variables documented
- [ ] Known limitations documented

---

## Next Steps After Completion

- [ ] Add monitoring/alerting for API failures
- [ ] Set up automated testing
- [ ] Add performance optimization
- [ ] Consider adding webhooks if available
- [ ] Build user-friendly CLI/GUI
- [ ] Add data export options
- [ ] Consider API versioning strategy
- [ ] Plan for API changes/deprecation

---

## Resources

- **Browser DevTools:** F12 in Chrome/Firefox
- **JSON Formatter:** `| jq` or https://jsonformatter.org
- **HTTP Client:** `curl`, `httpie`, or `postman`
- **Python:** `requests` library for HTTP
- **Documentation:** This checklist + API_INTEGRATION_BEST_PRACTICES.md

---

## Remember

**The #1 rule:** Never write integration code before verifying the API works with curl or browser DevTools.

**The #2 rule:** Test authentication separately from data access.

**The #3 rule:** Document as you discover, not after.

Follow these rules and you'll save hours of debugging and frustration.
