# Quick Start Guide

## You Have BondSports Credentials? Great!

Here's how to check field availability in 3 steps:

### Step 1: Set Your Credentials

```bash
export BONDSPORTS_EMAIL="your@email.com"
export BONDSPORTS_PASSWORD="yourpassword"
```

**Pro tip:** Add these to your `~/.bashrc` or `~/.zshrc` so you don't have to set them every time:

```bash
echo 'export BONDSPORTS_EMAIL="your@email.com"' >> ~/.zshrc
echo 'export BONDSPORTS_PASSWORD="yourpassword"' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Test It Works

```bash
python test_connection.py
```

You should see:
```
✓ Public API Access: PASS
✓ Authentication: PASS
✓ Slot Fetching: PASS
```

### Step 3: Check Availability

**Want to check a specific date at both locations?**
```bash
./check_fields.sh 2026-02-15
```

**Just one location?**
```bash
./check_fields.sh 2026-02-15 wall-street
```

**Want more control?**
```bash
# Check all fields
python bondsports_api.py availability wall-street 2026-02-15

# Check specific field only
python bondsports_api.py availability wall-street 2026-02-15 "Field 1"
```

## What You'll See

The tool shows you exactly when each field is available:

```
======================================================================
CHECKING AVAILABILITY: Socceroof Wall Street
======================================================================
Date: 2026-02-15

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

This tells you:
- Field 1 is open from 10 AM to 2 AM
- It's booked from 2-4 PM and 8-10 PM
- You can book: 10 AM-2 PM, 4-8 PM, or 10 PM-2 AM

## Common Use Cases

### Check the next 7 days

```bash
for i in {0..6}; do
    DATE=$(date -v+${i}d +%Y-%m-%d 2>/dev/null || date -d "+${i} days" +%Y-%m-%d)
    ./check_fields.sh "$DATE" wall-street
done
```

### Compare both locations for the same time

```bash
./check_fields.sh 2026-02-20
```

This shows both Wall Street and Crown Heights side-by-side.

### Find fields available right now

```bash
TODAY=$(date +%Y-%m-%d)
./check_fields.sh "$TODAY"
```

## Files in This Project

| File | Purpose |
|------|---------|
| `bondsports_api.py` | Python API client (main tool) |
| `check_fields.sh` | Simple wrapper script |
| `test_connection.py` | Test your setup |
| `SETUP.md` | Detailed setup instructions |
| `README.md` | Full documentation |

## Troubleshooting

**"Credentials not set"**
- Run: `echo $BONDSPORTS_EMAIL`
- If empty, set the environment variables again

**"Authentication failed"**
- Check your credentials are correct
- Try logging in at https://bondsports.co to verify your account works

**"Failed to fetch slots"**
- Your account might not have permission to view these facilities
- Try accessing them through the website first

## Advanced: Python Module

You can also use it as a Python module:

```python
from bondsports_api import BondSportsAPI, check_availability
import os

email = os.environ['BONDSPORTS_EMAIL']
password = os.environ['BONDSPORTS_PASSWORD']

# Check availability
check_availability(
    location='wall-street',
    date='2026-02-15',
    email=email,
    password=password
)
```

## Security Note

Your credentials are stored in environment variables only. They're never written to files or committed to git. The `.gitignore` is configured to exclude any credential files.

## Need Help?

1. Read `SETUP.md` for detailed instructions
2. Run `python test_connection.py` to diagnose issues
3. Check `README.md` for full API documentation
