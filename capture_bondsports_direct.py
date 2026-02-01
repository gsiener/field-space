#!/usr/bin/env python3
"""Capture API calls from BondSports direct booking page"""
from playwright.sync_api import sync_playwright
from datetime import datetime
import json

def capture():
    availability_calls = []
    
    def log_request(request):
        if 'api.bondsports.co' in request.url:
            if any(word in request.url.lower() for word in ['slot', 'availab', 'schedule', 'book']):
                print(f"\n🎯 {request.method} {request.url}")
                availability_calls.append({
                    'method': request.method,
                    'url': request.url,
                    'headers': dict(request.headers)
                })
    
    def log_response(response):
        if 'api.bondsports.co' in response.url:
            if any(word in response.url.lower() for word in ['slot', 'availab', 'schedule', 'book']):
                print(f"📥 {response.status} - {response.url[:100]}")
                if response.status == 200:
                    try:
                        data = response.json()
                        print(f"   Keys: {list(data.keys())}")
                        if 'data' in data:
                            print(f"   Data type: {type(data['data'])}")
                            if isinstance(data['data'], list) and len(data['data']) > 0:
                                print(f"   First item keys: {list(data['data'][0].keys())}")
                    except:
                        pass
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.on("request", log_request)
        page.on("response", log_response)
        
        print("Opening BondSports Crown Heights...")
        page.goto("https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436")
        page.wait_for_timeout(3000)
        
        # Login if needed
        if page.locator('button:has-text("Login")').count() > 0:
            print("Logging in...")
            page.click('button:has-text("Login")')
            page.wait_for_timeout(2000)
            page.fill('input[type="email"]', 'name@example.com')
            page.fill('input[type="password"]', 'yourpassword')
            page.click('button:has-text("Sign In")')
            page.wait_for_timeout(3000)
        
        print("\nFilling booking form...")
        # Click Activity dropdown
        page.click('button:has-text("Activity")')
        page.wait_for_timeout(1000)
        page.click('text=Soccer')
        page.wait_for_timeout(1000)
        
        # Enter date
        today = datetime.now().strftime('%m/%d/%Y')
        date_input = page.locator('input[type="text"]').nth(1)
        date_input.fill(today)
        page.wait_for_timeout(1000)
        
        print(f"\n🔍 Clicking Check Availability...")
        page.click('button:has-text("Check Availability")')
        page.wait_for_timeout(8000)  # Wait for results to load
        
        print("\n" + "="*70)
        print("AVAILABILITY API CALLS FOUND:")
        print("="*70)
        for call in availability_calls:
            print(f"\n{call['method']} {call['url']}")
        
        print("\n\nCheck browser - do you see time slots?")
        print("Press Enter when done...")
        input()
        browser.close()

if __name__ == '__main__':
    capture()
