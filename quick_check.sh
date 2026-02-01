#!/bin/bash
# Quick availability check using browser automation

LOCATION=${1:-wall-street}
DATE=${2:-$(date +%m/%d/%Y)}

if [ -z "$BONDSPORTS_EMAIL" ] || [ -z "$BONDSPORTS_PASSWORD" ]; then
    echo "Error: Set credentials first:"
    echo "  export BONDSPORTS_EMAIL='name@example.com'"
    echo "  export BONDSPORTS_PASSWORD='yourpassword'"
    exit 1
fi

echo "=============================================================="
echo "SOCCEROOF AVAILABILITY CHECKER"
echo "=============================================================="
echo "Location: $LOCATION"
echo "Date: $DATE"
echo ""
echo "Opening browser automation..."
echo ""

export BONDSPORTS_USER="$BONDSPORTS_EMAIL"
export BONDSPORTS_PASS="$BONDSPORTS_PASSWORD"

python check_playwright.py "$LOCATION" "$DATE"

echo ""
echo "=============================================================="
echo "Check the screenshots in /tmp/ for availability"
echo "=============================================================="
