# Socceroof Field Availability Checker

Check availability for indoor soccer fields at Socceroof locations.

## BondSports API Discovery

Socceroof uses **BondSports** as their booking platform. We have reverse-engineered the API and created a Python client for direct access.

### API Base URL
```
https://api.bondsports.co
```

### Discovered Public Endpoints (no authentication required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/organizations/{orgId}` | GET | Organization info (branding, contact) |
| `/v1/venues/{facilityId}` | GET | Facility details with all spaces/fields |
| `/v4/resources/{resourceId}?includeAdditionalData=true` | GET | Resource details with operating hours |
| `/v4/resources/{resourceId}/packages-v1` | GET | Pricing packages for a resource |
| `/v4/resources/organization/{orgId}/facility/{facilityId}/resources` | GET | List all resources for a facility |
| `/v4/organization/{orgId}` | GET | Organization data |

### Authenticated Endpoints (require login)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/organizations/{orgId}/slots` | GET | Get booked slots |
| `/v1/organizations/{orgId}/spaces/{spaceId}/slots` | GET | Slots for specific space |
| `/v1/organizations/{orgId}/schedule` | GET | Schedule data |
| `/v1/venues/{facilityId}/slots` | GET | Venue slots |
| `/auth` | POST | Login |
| `/auth/refresh` | POST | Refresh token |
| `/auth/logout` | POST | Logout |

**Note**: Checking actual availability (booked slots) requires authentication.

## Facility Information

### Wall Street
- **Address**: 28 Liberty Street, New York, NY 10005
- **BondSports Facility ID**: 502
- **Organization ID**: 450
- **Booking URL**: https://bondsports.co/facility/Socceroof%20Wall%20Street-New%20York/502?organizationId=450

**Fields**:
| Field Name | Resource ID |
|------------|-------------|
| Field 1- Single Field (5v5) | 6084 |
| Field 2- Single Field (5v5) | 6085 |
| Big Field 3- Large Field (7v7) | 6086 |
| 3a | 6087 |
| 3b | 6088 |
| 3c | 6089 |
| 3d | 6090 |
| Field 4- (Training Field) | 6091 |

### Crown Heights
- **Address**: Brooklyn, NY
- **BondSports Facility ID**: 484
- **Organization ID**: 436
- **Booking URL**: https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436

**Fields**:
| Field Name | Resource ID |
|------------|-------------|
| Field 1 Single Field (5v5) | 5612 |
| Field 2 Single Field (5v5) | 5613 |
| Field 3 Single Field (5v5) | 5614 |
| Field 4 Single Field (5v5) | 5615 |
| Field 5 Single Field (5v5 Or 6v6) | 5616 |
| Double Field 1 (6v6 or 7v7) | 5711 |
| Double Field 2 (6v6 or 7v7) | 5712 |

## Quick Start (With Authentication)

### 1. Set Your Credentials

```bash
export BONDSPORTS_EMAIL="your@email.com"
export BONDSPORTS_PASSWORD="yourpassword"
```

### 2. Test Your Connection

```bash
python test_connection.py
```

### 3. Check Availability

**Simple way (check both locations):**
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

# Filter for specific field
python bondsports_api.py availability wall-street 2026-02-15 "Field 1"
```

## What You Get

For each field on your specified date:
- **Operating Hours** - When the field is open
- **Booked Slots** - All existing reservations with times
- **Available Blocks** - Contiguous time blocks you can book
  - Start time, end time, and duration

Example output:
```
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
```

## Public API Usage (No Auth Required)

### Python API Client

```bash
# Get facility info with all fields
python bondsports_api.py info wall-street
python bondsports_api.py info crown-heights

# List resources
python bondsports_api.py resources wall-street

# Get operating hours
python bondsports_api.py hours wall-street
python bondsports_api.py hours wall-street "Field 1"

# Get pricing packages
python bondsports_api.py packages 6084
```

### curl Examples

**Get facility details:**
```bash
curl -s "https://api.bondsports.co/v1/venues/502" | python3 -m json.tool
```

**Get all resources for a facility:**
```bash
curl -s "https://api.bondsports.co/v4/resources/organization/450/facility/502/resources?resourceTypes=space&includeActivityTimes=true" | python3 -m json.tool
```

**Get resource details with operating hours:**
```bash
curl -s "https://api.bondsports.co/v4/resources/6084?includeAdditionalData=true" | python3 -m json.tool
```

**Get pricing packages:**
```bash
curl -s "https://api.bondsports.co/v4/resources/6084/packages-v1" | python3 -m json.tool
```

**Get organization info:**
```bash
curl -s "https://api.bondsports.co/v1/organizations/450" | python3 -m json.tool
```

### Python Module Usage

```python
from bondsports_api import BondSportsAPI, get_socceroof_resources

# Initialize client
api = BondSportsAPI()

# Get facility info
facility = api.get_facility(502)

# Get all resources
resources = get_socceroof_resources('wall-street')
for res in resources:
    print(f"{res['name']} (ID: {res['id']})")

# Get resource details
resource = api.get_resource(6084)

# Get operating hours
hours = api.get_operating_hours(6084)

# Get pricing
packages = api.get_resource_packages(6084)
```

## Operating Hours (as of Feb 2026)

### Wall Street (all fields)
- **Weekdays (Mon-Fri)**: 10:00 AM - 2:00 AM
- **Weekends (Sat-Sun)**: 8:00 AM - 2:00 AM

### Pricing (Single Field 75'x45')
- **Non Prime Time**: $175/hour
- **Prime Time**: $275/hour

## Limitations

The public API provides:
- Facility information
- Resource/field listings
- Operating hours
- Pricing packages

**Actual slot availability (what times are booked) requires authentication.**

To check real-time availability, you must:
1. Create a BondSports account
2. Login to get an auth token
3. Use the authenticated endpoints

Alternatively, use browser automation to interact with the booking UI.

## Browser Automation (Fallback)

```bash
# Uses agent-browser for UI interaction
python bondsports_checker.py wall-street 2026-02-15
```

## Files

- `bondsports_api.py` - Main API client
- `bondsports_checker.py` - Browser automation checker
- `check_availability.py` - Alternative checker
- `check-availability.js` - Node.js version
- `find_api.py` - API endpoint discovery tool
