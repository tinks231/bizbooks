"""
Quick test to check where Vercel serverless functions actually execute
Run this on your production URL to see the actual function region
"""

import requests
import time

def check_vercel_regions():
    url = "https://mahaveerelectricals.bizbooks.co.in/health"
    
    print("🔍 Checking Vercel Configuration...\n")
    print("=" * 60)
    
    # Make multiple requests to check
    for i in range(3):
        start = time.time()
        response = requests.get(url)
        latency = (time.time() - start) * 1000
        
        print(f"\n📊 Request {i+1}:")
        print(f"Status: {response.status_code}")
        print(f"Latency: {latency:.0f}ms")
        
        # Check headers
        headers_to_check = [
            'x-vercel-id',
            'x-vercel-cache',
            'x-vercel-execution-region',
            'server',
            'x-vercel-proxy-region',
            'x-vercel-ip-country',
            'x-edge-location'
        ]
        
        print("\n📍 Headers:")
        for header in headers_to_check:
            value = response.headers.get(header)
            if value:
                print(f"  {header}: {value}")
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("\n🔍 ANALYSIS:")
    print("\nLook for 'x-vercel-execution-region' or 'x-vercel-id'")
    print("Common regions:")
    print("  • iad1 = Washington DC (US East) - DEFAULT FREE TIER")
    print("  • sin1 = Singapore")
    print("  • bom1 = Mumbai")
    print("  • sfo1 = San Francisco")
    print("\nIf you see 'iad1' → Functions run in US (your suspicion is correct!)")
    print("If you see 'bom1' → Functions run in Mumbai (you're good!)")

if __name__ == "__main__":
    check_vercel_regions()

