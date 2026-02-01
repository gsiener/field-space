# Manual API Discovery - Instructions

Since automated clicking is failing, let's do this manually with proper network monitoring:

## Method 1: Chrome DevTools (Most Reliable)

1. **Open Chrome and DevTools**:
   - Open: https://www.socceroof.com/en/book/club/crown-heights/activity/rent-a-field/
   - Press F12 or Cmd+Option+I to open DevTools
   - Go to **Network** tab
   - Check **"Preserve log"** checkbox
   - Clear existing requests (click 🚫 button)

2. **Make sure you're logged in**:
   - If not logged in, login with: name@example.com / yourpassword

3. **Fill the form**:
   - Activity: Select "Other" (or "Soccer")
   - Activity Date: Enter today's date or 02/15/2026
   - Click "Check Availability"

4. **Watch the Network tab**:
   - Look for requests to `api.bondsports.co`
   - Find the one that returns the time slots
   - It might be something like:
     - `/v4/schedules/...`
     - `/v4/booking/...`
     - `/v4/slots/...`
     - Or something completely different!

5. **Capture the request**:
   - Click on the API request
   - Go to "Headers" tab
   - Copy the **Request URL** (full URL with parameters)
   - Copy the **Request Headers** (especially auth headers)
   - If it's a POST, copy the **Request Payload**

6. **Share the info**:
   - Paste the full URL here
   - Tell me what the response looks like

## Method 2: Quick Test

Just tell me what you observe:
- When you click "Check Availability", do time slots appear immediately?
- What do the time slots look like? (cards, list, table?)
- Are they for all fields or one field at a time?

This will help me understand what endpoint to look for!
