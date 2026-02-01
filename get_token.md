# Get Your BondSports Session Token (for SSO accounts)

Since your account uses SSO with Gmail, you can't use email/password authentication. Instead, we'll capture your session token after you log in.

## Steps to Get Your Token

### 1. Log in to BondSports

1. Open your browser
2. Go to https://bondsports.co
3. Click "Sign In" and log in with your Google/Gmail account

### 2. Open Browser DevTools

- **Chrome/Edge**: Press `F12` or `Cmd+Option+I` (Mac)
- **Firefox**: Press `F12`
- **Safari**: Enable Developer menu first (Preferences → Advanced), then `Cmd+Option+I`

### 3. Find Your Token

**Method A: From Application/Storage tab**
1. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
2. Expand "Cookies" in the left sidebar
3. Click on `https://bondsports.co`
4. Look for a cookie named something like:
   - `access_token`
   - `auth_token`
   - `jwt`
   - `token`
5. Copy the value

**Method B: From Network tab**
1. Go to "Network" tab
2. Refresh the page
3. Look for any API request to `api.bondsports.co`
4. Click on the request
5. Go to "Headers" section
6. Look for `Authorization` header
7. Copy the token (it will look like `Bearer <long-string>`)

### 4. Set the Token

```bash
export BONDSPORTS_TOKEN="your_token_here"
```

## Using the Token

I'll update the API client to support token-based authentication. You'll be able to use:

```bash
# Set the token
export BONDSPORTS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Use it
python bondsports_api.py availability wall-street 2026-02-15
```

## Token Expiration

Session tokens typically expire after:
- **Short-lived**: 1-24 hours
- **Long-lived**: 7-30 days

When it expires, you'll need to log in again and get a new token.

## Security

- Never share your token with anyone
- Don't commit it to git (it's in `.gitignore`)
- Treat it like a password - it gives full access to your account

## Next Steps

Once you have your token, let me know and I'll update the scripts to use it!
