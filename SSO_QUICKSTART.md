# Quick Start for SSO Accounts (Google/Gmail Login)

Since your BondSports account uses SSO with Gmail, you'll need to use a session token instead of email/password.

## Two Options

### Option 1: Manual Token Capture (Recommended)

This is the simplest way - you log in once in your browser, grab the token, and use it until it expires.

#### Step 1: Log In and Get Your Token

1. **Open BondSports and log in**
   - Go to https://bondsports.co
   - Click "Sign In"
   - Log in with your Google account

2. **Open Developer Tools**
   - Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)

3. **Find Your Token**

   **Method A: From Console (Easiest)**
   ```javascript
   // Paste this in the Console tab:
   localStorage.getItem('auth_token') ||
   sessionStorage.getItem('auth_token') ||
   document.cookie.match(/token=([^;]+)/)?.[1] ||
   'Token not found - try Method B'
   ```

   **Method B: From Network Tab**
   - Go to "Network" tab
   - Reload the page
   - Find a request to `api.bondsports.co`
   - Click on it → "Headers" section
   - Look for `Authorization: Bearer <token>`
   - Copy everything after "Bearer "

   **Method C: From Application/Storage Tab**
   - Go to "Application" (Chrome) or "Storage" (Firefox) tab
   - Look in Cookies or Local Storage for `bondsports.co`
   - Find entries like `auth_token`, `access_token`, or `jwt`
   - Copy the value

#### Step 2: Set the Token

```bash
export BONDSPORTS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Add to your shell config to make it permanent:
```bash
echo 'export BONDSPORTS_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

#### Step 3: Test It

```bash
python test_connection.py
```

You should see:
```
✓ Public API Access: PASS
✓ Authentication: PASS (using session token)
✓ Slot Fetching: PASS
```

#### Step 4: Check Availability

```bash
./check_fields.sh 2026-02-15
```

### Option 2: Browser Automation (Fallback)

If you can't get the token, use browser automation which handles SSO automatically:

```bash
python bondsports_checker.py wall-street 2026-02-15
```

This opens a browser, navigates to the booking page, and extracts availability visually.

**Pros:**
- Handles SSO automatically
- No token needed

**Cons:**
- Slower (opens browser each time)
- May require manual interaction to complete login

## Token Expiration

Session tokens typically expire after:
- **1-24 hours** (short-lived)
- **7-30 days** (long-lived)

When it expires, you'll see:
```
✗ Token invalid or expired
```

Just log in again and get a new token.

## Quick Reference

```bash
# Set token
export BONDSPORTS_TOKEN="your_token_here"

# Test connection
python test_connection.py

# Check availability
./check_fields.sh 2026-02-15
./check_fields.sh 2026-02-15 wall-street
./check_fields.sh 2026-02-15 crown-heights

# Python directly
python bondsports_api.py availability wall-street 2026-02-15
python bondsports_api.py availability wall-street 2026-02-15 "Field 1"
```

## Troubleshooting

**"Token invalid or expired"**
- Log in again and get a new token
- Make sure you copied the entire token

**"Token not found"**
- Try all three methods (A, B, C) in Step 1
- Make sure you're logged in before checking
- Token might be in a different location depending on how BondSports implements auth

**Can't find token anywhere**
- Use Option 2 (browser automation) instead
- Or try a different browser
- Check if you're actually logged in (can you see the booking pages?)

## Security

- **Never share your token** - it gives full access to your account
- **Don't commit it to git** - already in `.gitignore`
- **Treat it like a password**
- Token is stored only in environment variables (not in files)

## Files

| File | Purpose |
|------|---------|
| `get_token.md` | Detailed token extraction guide |
| `bondsports_api.py` | Main API client (supports tokens) |
| `check_fields.sh` | Simple wrapper (auto-detects token) |
| `test_connection.py` | Test your setup |

## What You Get

Same output as email/password accounts:

```
Field 1- Single Field (5v5) (ID: 6084)
  Operating Hours: 10:00 - 02:00
  Booked Slots (2):
    • 14:00 - 16:00
    • 20:00 - 22:00
  Available Blocks (3):
    ✓ 10:00 - 14:00 (4h)
    ✓ 16:00 - 20:00 (4h)
    ✓ 22:00 - 02:00 (4h)
```

Perfect for finding available time slots quickly!
