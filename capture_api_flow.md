# Capture BondSports API Flow

Let's capture the exact API calls BondSports makes so we can automate them.

## Instructions

1. **Open Chrome/Firefox and open DevTools**
   - Press F12 or Cmd+Option+I
   - Go to **Network** tab
   - Check **"Preserve log"**

2. **Clear and start recording**
   - Click the clear button (🚫) to clear all requests
   - Make sure recording is on (red dot)

3. **Complete a booking check**
   - Go to: https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450
   - Log in with: name@example.com
   - Select Activity: Soccer
   - Enter Date: 02/15/2026
   - Click "Check Availability"

4. **Find the slots API call**
   Look for requests to `api.bondsports.co` - likely something like:
   - `/v1/venues/502/slots`
   - `/v1/organizations/450/slots`
   - `/v4/resources/.../slots`
   - `/availability`

5. **Copy the request details**

   Right-click on the API request → "Copy" → "Copy as cURL"

   Or manually copy:
   - **Request URL** (full URL)
   - **Request Method** (GET/POST)
   - **Request Headers** (ALL of them, especially):
     - `Authorization`
     - `Cookie`
     - `X-Auth-Token` or similar
     - Any other auth-related headers
   - **Query Parameters** (if any)
   - **Request Payload** (if POST)

6. **Share with me**

   Either:
   - Paste the cURL command
   - Or paste the headers and URL

## What to Look For

The authentication might be in:
- `Authorization: Bearer <token>` header
- `Cookie: <session-data>` header
- Custom header like `X-Auth-Token`
- Query parameter like `?token=...`

## Example of what I need

```
GET https://api.bondsports.co/v1/venues/502/slots?startDate=2026-02-15&endDate=2026-02-15
Headers:
  Authorization: Bearer eyJhbGc...
  Cookie: session=abc123...
  Content-Type: application/json
```

Once I have this, I can replicate it exactly in our API client!
