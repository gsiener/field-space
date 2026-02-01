#!/usr/bin/env python3
"""
Capture the REAL API call that happens when checking availability.
Uses Playwright with network monitoring to see what endpoint the website actually calls.
"""
import sys
from playwright.sync_api import sync_playwright
from datetime import datetime

def capture_api_calls():
    api_calls = []
    
    def capture_request(request):
        if 'api.bondsports.co' in request.url:
            api_calls.append({
                'method': request.method,
                'url': request.url,
                'headers': dict(request.headers),
                'post_data': request.post_data
            })
            print(f"\n🎯 CAPTURED: {request.method} {request.url}")
    
    def capture_response(response):
        if 'api.bondsports.co' in response.url and 'slot' in response.url.lower() or 'availab' in response.url.lower():
            print(f"📥 RESPONSE: {response.status} - {response.url}")
            try:
                body = response.json()
                print(f"   Body keys: {list(body.keys())}")
            except:
                pass
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Capture all requests and responses
        page.on("request", capture_request)
        page.on("response", capture_response)
        
        print("Opening Crown Heights booking page...")
        page.goto("https://www.socceroof.com/en/book/club/crown-heights/activity/rent-a-field/")
        page.wait_for_load_state('networkidle')
        
        # Check if login needed
        if page.locator('button:has-text("Login")').count() > 0:
            print("Logging in...")
            page.click('button:has-text("Login")')
            page.wait_for_timeout(2000)
            page.fill('input[type="email"]', 'name@example.com')
            page.fill('input[type="password"]', 'yourpassword')
            page.click('button:has-text("Sign In")')
            page.wait_for_timeout(3000)
            page.goto("https://www.socceroof.com/en/book/club/crown-heights/activity/rent-a-field/")
            page.wait_for_timeout(2000)
        
        print("\nFilling form...")
        # Select "Other" from Activity dropdown
        page.click('select[name="activity"], button:has-text("Activity")')
        page.wait_for_timeout(1000)
        
        # Try to select "Other"
        if page.locator('option:has-text("Other")').count() > 0:
            page.select_option('select', label='Other')
        else:
            page.click('text=Other')
        page.wait_for_timeout(1000)
        
        # Enter today's date
        today = datetime.now().strftime('%m/%d/%Y')
        page.fill('input[type="text"], input[type="date"]', today)
        page.wait_for_timeout(1000)
        
        print(f"\n🔍 Clicking 'Check Availability' and monitoring API calls...")
        page.click('button:has-text("Check Availability")')
        page.wait_for_timeout(5000)
        
        print("\n" + "="*70)
        print("CAPTURED API CALLS:")
        print("="*70)
        for call in api_calls:
            if 'slot' in call['url'].lower() or 'availab' in call['url'].lower() or 'schedule' in call['url'].lower():
                print(f"\n🎯 {call['method']} {call['url']}")
                if call['post_data']:
                    print(f"   POST Data: {call['post_data']}")
        
        print("\n\nPress Enter to close browser...")
        input()
        browser.close()

if __name__ == '__main__':
    capture_api_calls()
