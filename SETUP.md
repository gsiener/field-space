# Setup Guide

## Quick Start

You have a BondSports account, so you can check real-time availability!

### 1. Set Your Credentials

Add these to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export BONDSPORTS_EMAIL="your@email.com"
export BONDSPORTS_PASSWORD="yourpassword"
```

Or set them temporarily in your current session:

```bash
export BONDSPORTS_EMAIL="your@email.com"
export BONDSPORTS_PASSWORD="yourpassword"
```

### 2. Check Availability

**Easy way (both locations):**
```bash
./check_fields.sh 2026-02-15
```

**Specific location:**
```bash
./check_fields.sh 2026-02-15 wall-street
./check_fields.sh 2026-02-15 crown-heights
```

**Using Python directly:**
```bash
python bondsports_api.py availability wall-street 2026-02-15
python bondsports_api.py availability crown-heights 2026-02-15
```

**Filter for specific field:**
```bash
python bondsports_api.py availability wall-street 2026-02-15 "Field 1"
```

## What You'll Get

The tool will show you:

1. **Operating Hours** - When each field is open
2. **Booked Slots** - All existing reservations
3. **Available Blocks** - Contiguous time blocks you can book
   - Start and end times
   - Duration (in hours and minutes)

## Example Output

```
======================================================================
CHECKING AVAILABILITY: Socceroof Wall Street
======================================================================
Date: 2026-02-15

Authenticating...
✓ Logged in successfully

Fetching fields...
Found 8 field(s)

Fetching bookings for 2026-02-15...

======================================================================
AVAILABILITY
======================================================================

Field 1- Single Field (5v5) (ID: 6084)
  Operating Hours: 10:00 - 02:00
  Booked Slots (3):
    • 14:00 - 15:30
    • 18:00 - 19:00
    • 21:00 - 23:00
  Available Blocks (4):
    ✓ 10:00 - 14:00 (4h)
    ✓ 15:30 - 18:00 (2h 30m)
    ✓ 19:00 - 21:00 (2h)
    ✓ 23:00 - 02:00 (3h)

Field 2- Single Field (5v5) (ID: 6085)
  Operating Hours: 10:00 - 02:00
  Available Blocks (1):
    ✓ 10:00 - 02:00 (16h)
```

## Security Note

**Never commit your credentials to git!**

Your credentials are stored in environment variables only. The `.gitignore` should exclude any credential files.

If you want to store them in a file (not recommended):
1. Create a `.env` file
2. Add it to `.gitignore`
3. Source it before running: `source .env && ./check_fields.sh 2026-02-15`

## Troubleshooting

### "Authentication failed"
- Check your email and password are correct
- Make sure you can log in at https://bondsports.co
- Try resetting your password if needed

### "Credentials not set"
- Make sure you've exported the environment variables
- Check: `echo $BONDSPORTS_EMAIL`
- Try setting them again in your current shell

### "Failed to fetch slots"
- Your credentials might be correct but lack permissions
- Try logging in on the website first to verify your account works
- Check that your account has access to the Socceroof facilities

## Advanced Usage

### Check multiple dates in a loop

```bash
# Check availability for the next 7 days
for i in {0..6}; do
    DATE=$(date -v+${i}d +%Y-%m-%d)
    echo "Checking $DATE..."
    ./check_fields.sh "$DATE" wall-street
done
```

### Export to JSON

```python
from bondsports_api import BondSportsAPI, FACILITIES, get_socceroof_resources
import json
import os

email = os.environ['BONDSPORTS_EMAIL']
password = os.environ['BONDSPORTS_PASSWORD']

api = BondSportsAPI()
api.login(email, password)

date = "2026-02-15"
facility = FACILITIES['wall-street']

slots = api.get_venue_slots(facility['facilityId'], date, date)

with open(f'availability-{date}.json', 'w') as f:
    json.dump(slots, f, indent=2)
```

## Next Steps

Once you have the tool working:

1. **Automate checks** - Set up a cron job to check daily
2. **Add notifications** - Get alerts when fields become available
3. **Compare pricing** - Factor in prime vs. non-prime time slots
4. **Batch queries** - Check multiple dates at once
