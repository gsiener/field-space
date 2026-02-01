#!/usr/bin/env python3
from bondsports_api import BondSportsAPI
import json

api = BondSportsAPI()
api.login("name@example.com", "yourpassword")

# Check what's at the base endpoints
for version in ['v1', 'v4']:
    url = f"{api.base_url}/{version}"
    response = api.session.get(url, headers=api._get_headers())
    print(f"\n{version} endpoint:")
    print(json.dumps(response.json(), indent=2))
