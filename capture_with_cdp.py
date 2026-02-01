#!/usr/bin/env python3
"""
Use Playwright's CDP (Chrome DevTools Protocol) to capture network requests.
This captures ALL network traffic including the availability API call.
"""
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def capture_with_cdp():
    captured_requests = []
    
    with sync_playwright() as p:
        # Launch with CDP enabled
        browser = p.chromium.launch(
            headless=False,
            args=['--remote-debugging-port=9222']
        )
        
        context = browser.new_context()
        page = context.new_page()
        
        # Enable network tracking via CDP
        client = page.context.new_cdp_session(page)
        client.send('Network.enable')
        
        def handle_request(event):
            request = event
            url = request.get('request', {}).get('url', '')
            
            if 'api.bondsports.co' in url:
                method = request.get('request', {}).get('method', 'GET')
                captured_requests.append({
                    'method': method,
                    'url': url,
                    'headers': request.get('request', {}).get('headers', {})
                })
                print(f"\n🔍 {method} {url}")
        
        def handle_response(event):
            response = event
            url = response.get('response', {}).get('url', '')
            
            if 'api.bondsports.co' in url:
                status = response.get('response', {}).get('status', 0)
                print(f"📥 {status} - {url[:100]}")
                
                # For successful API responses, try to get the body
                if status == 200 and any(word in url.lower() for word in ['slot', 'availab', 'schedule', 'book']):
                    print(f"   ⭐ This might be the availability endpoint!")
        
        client.on('Network.requestWillBeSent', handle_request)
        client.on('Network.responseReceived', handle_response)
        
        print("="*70)
        print("NETWORK MONITORING ACTIVE")
        print("="*70)
        print("\nNavigating to Crown Heights booking page...")
        
        page.goto('https://bondsports.co/facility/Socceroof%20-%20Crown%20Heights-New%20York/484?organizationId=436')
        page.wait_for_timeout(3000)
        
        print("\n📝 Instructions:")
        print("1. Log in if needed (name@example.com / password)")
        print("2. Select Activity: 'Other' or 'Soccer'")
        print("3. Enter a date")
        print("4. Click 'Check Availability'")
        print("5. Watch this terminal for API calls!")
        print("\nWhen you're done, press Enter here...")
        
        input()
        
        print("\n" + "="*70)
        print("CAPTURED API CALLS TO api.bondsports.co:")
        print("="*70)
        
        for req in captured_requests:
            if any(word in req['url'].lower() for word in ['slot', 'availab', 'schedule', 'book', 'time']):
                print(f"\n⭐ {req['method']} {req['url']}")
        
        print("\n" + "="*70)
        print("ALL CAPTURED CALLS:")
        print("="*70)
        for req in captured_requests:
            print(f"{req['method']} {req['url']}")
        
        browser.close()

if __name__ == '__main__':
    capture_with_cdp()
