# Capture Exact Authentication Headers

Let's see exactly how BondSports authenticates API requests.

## Steps

1. **Open BondSports and log in**
   - Go to https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450
   - Make sure you're logged in

2. **Open DevTools Network Tab**
   - Press F12
   - Go to "Network" tab
   - Check "Preserve log"

3. **Trigger an API Call**
   - Click on a date in the booking calendar
   - Or click "Check Availability"
   - Watch for requests to `api.bondsports.co`

4. **Find the Slots API Call**
   - Look for a request to something like:
     - `api.bondsports.co/v1/venues/502/slots`
     - `api.bondsports.co/v1/organizations/450/slots`
   - Click on that request

5. **Copy the Headers**
   - Go to the "Headers" tab
   - Under "Request Headers", look for:
     - `Authorization: ...`
     - `X-Auth-Token: ...`
     - `X-Api-Key: ...`
     - Any other auth-related headers

   Tell me what you see! The exact header names and format.

## What to Look For

The authorization might be in different formats:
- `Authorization: Bearer <token>`
- `Authorization: <token>`
- `X-Auth-Token: <token>`
- `Cookie: ...` (session-based)

Also note:
- Which token value is being sent (compare with the tokens in storage)
- Any other headers that look auth-related

## Alternative: Try ID Token

In your `.env`, try changing to use the ID token instead:

```bash
# Instead of BondUserAccessToken, try BondUserIdToken
BONDSPORTS_TOKEN=<value_of_BondUserIdToken>
```

Then test again:
```bash
source .env && python test_connection.py
```
