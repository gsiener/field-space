# API Integration Best Practices - Documentation Index

Comprehensive guides for successful API integrations based on real-world experience with the BondSports API.

## Quick Links

- **New to API integration?** Start with the [Checklist](#checklist)
- **Already stuck?** Jump to [Troubleshooting](#troubleshooting)
- **Want deep dive?** Read [Best Practices](#best-practices)

---

## Documents in This Collection

### 1. API Integration Checklist
**File:** `API_INTEGRATION_CHECKLIST.md`

**Use this when:** Starting a new API integration

A step-by-step checklist covering:
- Pre-integration discovery (DO THIS FIRST!)
- Authentication testing
- Endpoint documentation
- Implementation phases
- Testing and validation
- Quick command reference

**Time to complete:** 15-30 minutes to review; 6-12 hours for full integration

**Start here if:** You're beginning a new API integration project

---

### 2. Best Practices Guide
**File:** `API_INTEGRATION_BEST_PRACTICES.md`

**Use this when:** You want comprehensive understanding of API integration

In-depth coverage of:
- Pre-integration API discovery techniques
- Authentication testing strategies
- Endpoint discovery methods
- API vs browser automation decision matrix
- Fallback strategies
- Common pitfalls and solutions
- Real-world examples

**Time to read:** 45-60 minutes

**Start here if:** You want to understand the "why" behind best practices

---

### 3. Troubleshooting Guide
**File:** `API_TROUBLESHOOTING_GUIDE.md`

**Use this when:** Something isn't working

Practical debugging for:
- Authentication failures
- 404 (Not Found) errors
- 401/403 (Unauthorized) errors
- Token expiration
- Rate limiting
- Malformed responses
- SSO/OAuth issues
- Network problems
- Data parsing errors

**Time to resolve:** 5-30 minutes per issue

**Start here if:** You're debugging a specific problem

---

## Quick Start Guide

### For Complete Beginners

1. **Read this first** (5 minutes)
   - [Quick Start](#quick-start-in-5-minutes) section below

2. **Print the checklist** (2 minutes)
   - Open `API_INTEGRATION_CHECKLIST.md`
   - Print or keep open in a tab

3. **Follow the checklist** (6-12 hours)
   - Check off items as you go
   - Reference other guides as needed

### For Experienced Developers

1. **Skim the checklist** (5 minutes)
   - `API_INTEGRATION_CHECKLIST.md`
   - Focus on Phase 1-2 (most important)

2. **Keep troubleshooting guide handy** (bookmark it)
   - `API_TROUBLESHOOTING_GUIDE.md`
   - Reference when issues arise

3. **Reference best practices** (as needed)
   - `API_INTEGRATION_BEST_PRACTICES.md`
   - Read relevant sections when needed

---

## Quick Start in 5 Minutes

### The Most Important Rules

**Rule #1: DevTools First, Code Later**

Never write API integration code before verifying the API exists:

```bash
# DO THIS FIRST:
1. Open website in Chrome/Firefox
2. Press F12 (open DevTools)
3. Go to Network tab
4. Interact with website
5. Watch for API calls
6. Right-click request → "Copy as cURL"
7. Test in terminal
```

**Rule #2: Test Authentication Separately**

Don't combine authentication and data access:

```python
# BAD - hard to debug
def get_data(email, password):
    token = login(email, password)
    return fetch_data(token)

# GOOD - test auth first
def test_auth():
    token = login(email, password)
    print(f"✓ Token: {token}")

def get_data():
    token = load_cached_token()
    return fetch_data(token)
```

**Rule #3: Start Minimal**

```python
# Step 1: Minimal test (10 lines)
import requests
response = requests.get('https://api.example.com/test')
print(response.json())

# Step 2: If it works, add auth (20 lines)
# Step 3: If auth works, build client (100 lines)
# Step 4: Add features incrementally
```

### The 5-Minute Validation

Before writing any code:

```bash
# Test 1: Does endpoint exist?
curl -s "https://api.example.com/v1/test" | jq

# Test 2: Can I authenticate?
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Test 3: Can I access data with token?
curl -s -H "Authorization: Bearer TOKEN" \
  "https://api.example.com/v1/data" | jq
```

**If all 3 work:** Proceed with integration (use checklist)

**If any fail:** See troubleshooting guide before writing code

---

## Common Scenarios

### Scenario 1: New Integration from Scratch

**Documents to use:**
1. `API_INTEGRATION_CHECKLIST.md` - Primary guide
2. `API_INTEGRATION_BEST_PRACTICES.md` - Reference for "why"
3. `API_TROUBLESHOOTING_GUIDE.md` - When issues arise

**Process:**
1. Print/open checklist
2. Phase 1: Discovery (validate API exists)
3. Phase 2: Test authentication
4. Phase 3-4: Build client incrementally
5. Phase 5-6: Add business logic and fallbacks
6. Phase 7-8: Document and test

**Time:** 6-12 hours total

---

### Scenario 2: Debugging Broken Integration

**Documents to use:**
1. `API_TROUBLESHOOTING_GUIDE.md` - Primary resource
2. `API_INTEGRATION_BEST_PRACTICES.md` - Section 7 (Common Pitfalls)

**Process:**
1. Identify the error (401, 404, timeout, etc.)
2. Find section in troubleshooting guide
3. Follow diagnosis steps
4. Apply solution
5. Test fix

**Time:** 5-30 minutes per issue

---

### Scenario 3: SSO/OAuth Integration

**Documents to use:**
1. `API_TROUBLESHOOTING_GUIDE.md` - Section 7 (SSO/OAuth)
2. `API_INTEGRATION_BEST_PRACTICES.md` - Section 2 (Auth strategies)

**Key insight:** Don't try to automate OAuth - extract token manually

**Process:**
1. Login via browser
2. Extract token from DevTools
3. Use token directly in code
4. Create `get_token.md` with instructions
5. Document token expiration

**Time:** 30 minutes

---

### Scenario 4: Choosing API vs Browser Automation

**Documents to use:**
1. `API_INTEGRATION_BEST_PRACTICES.md` - Section 4 (Decision Matrix)

**Use API if:**
- Endpoints return JSON
- Authentication is straightforward
- No heavy rate limiting
- No CAPTCHA

**Use Browser Automation if:**
- No API exists
- Complex OAuth with no access
- Need screenshots/visual verification

**Use Hybrid:**
- Browser for auth → API for data
- API for structured data → Browser for screenshots

**Time:** 10 minutes to decide

---

## Real-World Example

This documentation is based on integrating with the BondSports API for Socceroof:

### What We Built

- **bondsports_api.py** - Full API client
- **test_connection.py** - Authentication testing
- **explore_api.py** - Endpoint discovery tool
- **bondsports_checker.py** - Browser automation fallback
- **README.md** - Complete documentation

### Timeline

- **Discovery:** 1 hour (browser DevTools, testing endpoints)
- **Auth Testing:** 45 minutes (handled SSO complexity)
- **API Client:** 3 hours (incremental implementation)
- **Business Logic:** 2 hours (availability calculation)
- **Fallbacks:** 1 hour (browser automation, token caching)
- **Documentation:** 1 hour (README, examples)

**Total:** ~9 hours

**Time saved by following best practices:** ~4 hours (avoided dead ends)

### Key Challenges Solved

1. **SSO authentication** - Used manual token extraction
2. **Undocumented API** - Discovered via browser DevTools
3. **Multiple auth headers** - Found by inspecting requests
4. **Token expiration** - Implemented auto-refresh
5. **Overnight hours** - Handled with time parsing logic

---

## Tools Reference

### Essential Tools

**Browser DevTools**
- Chrome: F12 or Cmd+Option+I
- Firefox: F12 or Cmd+Option+I
- Network tab: See API requests
- Application tab: View cookies/localStorage

**Command Line**
```bash
# curl - Test HTTP requests
curl -s "https://api.example.com/endpoint" | jq

# jq - Format JSON
echo '{"key":"value"}' | jq

# httpie - User-friendly alternative to curl
http GET https://api.example.com/endpoint
```

**Python**
```bash
# Install requests library
pip install requests

# For browser automation (fallback)
pip install playwright
playwright install
```

### Test Template

Quick starter template:

```python
#!/usr/bin/env python3
import requests
import os

BASE_URL = "https://api.example.com"

# Test 1: Public endpoint
response = requests.get(f"{BASE_URL}/v1/test")
print(f"Public endpoint: {response.status_code}")

# Test 2: Authentication
email = os.environ.get('API_EMAIL')
password = os.environ.get('API_PASSWORD')

if email and password:
    auth_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={'email': email, 'password': password}
    )
    print(f"Auth: {auth_response.status_code}")

    if auth_response.status_code == 200:
        token = auth_response.json().get('token')
        print(f"Token: {token[:20]}...")

        # Test 3: Authenticated endpoint
        data_response = requests.get(
            f"{BASE_URL}/v1/data",
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"Data access: {data_response.status_code}")
```

---

## FAQ

### Q: How long does a typical API integration take?

**A:** Following these practices:
- **Simple API:** 2-4 hours
- **Moderate complexity:** 6-12 hours
- **Complex (SSO, rate limits, etc.):** 12-20 hours

Without following these practices: 2-3x longer (due to debugging and rework)

### Q: What if the API isn't documented?

**A:** Use browser DevTools to discover endpoints:
1. Open website in browser
2. F12 → Network tab
3. Interact with site
4. Watch for API calls
5. Copy and test endpoints

See: `API_INTEGRATION_BEST_PRACTICES.md` - Section 3

### Q: What if authentication uses Google/GitHub login?

**A:** Don't try to automate OAuth. Instead:
1. Login via browser
2. Extract session token from DevTools
3. Use token directly in code
4. Document process for users

See: `API_TROUBLESHOOTING_GUIDE.md` - Section 7

### Q: When should I use browser automation instead of API?

**A:** Use browser automation when:
- No API exists
- Complex OAuth you can't access
- API heavily rate-limited
- Need screenshots/visual verification

See: `API_INTEGRATION_BEST_PRACTICES.md` - Section 4

### Q: My requests work in curl but fail in Python. Why?

**A:** Common causes:
1. Missing headers (add User-Agent, Content-Type)
2. SSL verification (Python checks, curl might not)
3. Different authentication handling

See: `API_TROUBLESHOOTING_GUIDE.md` - Section 8

### Q: How do I handle token expiration?

**A:** Implement auto-refresh:
1. Store token expiration time
2. Check before each request
3. Refresh if expired
4. Cache refreshed token

See: `API_TROUBLESHOOTING_GUIDE.md` - Section 4

---

## Success Metrics

You'll know you're following best practices if:

- [ ] Spent time in browser DevTools before writing code
- [ ] Created authentication test script first
- [ ] Have working curl commands for all endpoints
- [ ] Documented endpoints as you discovered them
- [ ] Built API client incrementally (tested each endpoint)
- [ ] Have fallback strategy for SSO/OAuth
- [ ] Created README with examples
- [ ] Handled token expiration
- [ ] Added error handling and retries
- [ ] Total time was 6-12 hours (not 20+ hours debugging)

---

## Anti-Patterns to Avoid

### 1. Code First, Verify Later
```python
# BAD - writing code without verifying API exists
class APIClient:
    def get_slots(self, date):
        return requests.get(f'{self.base_url}/slots?date={date}')
# But does /slots endpoint even exist???
```

### 2. Combining Auth and Data Access
```python
# BAD - can't tell if auth or data access is failing
def check_availability(email, password, date):
    token = login(email, password)
    return get_slots(token, date)
```

### 3. No Error Handling
```python
# BAD - will crash on any error
data = response.json()['data']['items'][0]['value']
```

### 4. Ignoring Token Expiration
```python
# BAD - token will expire
token = login()
# ... hours later ...
data = get_data(token)  # Fails!
```

### 5. No Documentation
```python
# BAD - no one knows how this works
# Just code with no comments, no README, no examples
```

---

## Next Steps

### After Completing Integration

1. **Add monitoring** - Alert on API failures
2. **Set up tests** - Automated testing
3. **Optimize performance** - Caching, connection pooling
4. **Build CLI/GUI** - User-friendly interface
5. **Add webhooks** - If API supports them
6. **Plan for changes** - API versioning strategy

### Continuous Improvement

- Review error logs weekly
- Update documentation when API changes
- Add new endpoints as discovered
- Improve error messages based on user feedback
- Optimize based on usage patterns

---

## Contributing

Found an issue or have improvements? Common areas:

- Add new troubleshooting scenarios
- Share real-world examples
- Improve existing solutions
- Add language-specific examples (JavaScript, Go, etc.)
- Update tools/libraries references

---

## Summary: The Golden Rules

1. **DevTools First, Code Later** - Always verify API exists via browser DevTools
2. **Test Auth Separately** - Verify authentication works before data access
3. **Start Minimal** - Test with curl, then minimal script, then full client
4. **Document Everything** - Future you will thank you
5. **Have a Fallback** - Browser automation for complex auth/no API
6. **Handle Expiration** - Auto-refresh tokens
7. **Test Incrementally** - One endpoint at a time
8. **Cache When Possible** - Reduce API calls
9. **Plan for Errors** - Comprehensive error handling
10. **Accept Limitations** - Sometimes browser automation is the only option

---

## File Structure

```
/Users/gsiener/src/field-space/
├── API_INTEGRATION_BEST_PRACTICES.md  # Comprehensive guide
├── API_INTEGRATION_CHECKLIST.md       # Step-by-step checklist
├── API_TROUBLESHOOTING_GUIDE.md       # Problem-solving guide
├── BEST_PRACTICES_README.md           # This file (index)
├── bondsports_api.py                  # Real implementation example
├── test_connection.py                 # Auth testing example
├── explore_api.py                     # Discovery tool example
└── README.md                          # Project-specific docs
```

---

## Remember

**The best code is code you don't write because you verified everything works first.**

Time spent in browser DevTools (30-60 minutes) can save hours of debugging broken integrations.

**Start here:**
1. Open `API_INTEGRATION_CHECKLIST.md`
2. Follow Phase 1 (Discovery) carefully
3. Reference other guides as needed

**Good luck with your integration!**
