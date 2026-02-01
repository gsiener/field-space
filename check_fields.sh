#!/bin/bash

# Socceroof Field Availability Checker
# Simple wrapper around bondsports_api.py

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if credentials are set
if [ -z "$BONDSPORTS_TOKEN" ]; then
    if [ -z "$BONDSPORTS_EMAIL" ] || [ -z "$BONDSPORTS_PASSWORD" ]; then
        echo -e "${RED}Error: BondSports credentials not set${NC}"
        echo ""
        echo "For SSO accounts (Google/Gmail login):"
        echo "  export BONDSPORTS_TOKEN='your_session_token'"
        echo "  See get_token.md for instructions on getting your token"
        echo ""
        echo "For email/password accounts:"
        echo "  export BONDSPORTS_EMAIL='your@email.com'"
        echo "  export BONDSPORTS_PASSWORD='yourpassword'"
        exit 1
    fi
else
    echo -e "${GREEN}Using session token (SSO account)${NC}"
fi

# Usage function
usage() {
    echo "Socceroof Field Availability Checker"
    echo ""
    echo "Usage: $0 <date> [location]"
    echo ""
    echo "Arguments:"
    echo "  date       Date in YYYY-MM-DD format (e.g., 2026-02-15)"
    echo "  location   Optional: 'wall-street' or 'crown-heights' (default: both)"
    echo ""
    echo "Examples:"
    echo "  $0 2026-02-15                    # Check both locations"
    echo "  $0 2026-02-15 wall-street        # Check Wall Street only"
    echo "  $0 2026-02-15 crown-heights      # Check Crown Heights only"
    exit 1
}

# Check arguments
if [ $# -lt 1 ]; then
    usage
fi

DATE=$1
LOCATION=${2:-"both"}

# Validate date format
if ! [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo -e "${RED}Error: Invalid date format${NC}"
    echo "Use YYYY-MM-DD format (e.g., 2026-02-15)"
    exit 1
fi

# Check which locations to query
LOCATIONS=()
if [ "$LOCATION" == "both" ]; then
    LOCATIONS=("wall-street" "crown-heights")
elif [ "$LOCATION" == "wall-street" ] || [ "$LOCATION" == "crown-heights" ]; then
    LOCATIONS=("$LOCATION")
else
    echo -e "${RED}Error: Unknown location: $LOCATION${NC}"
    echo "Use 'wall-street', 'crown-heights', or 'both'"
    exit 1
fi

# Check availability for each location
for loc in "${LOCATIONS[@]}"; do
    python bondsports_api.py availability "$loc" "$DATE"
    echo ""
done

echo -e "${GREEN}✓ Done${NC}"
