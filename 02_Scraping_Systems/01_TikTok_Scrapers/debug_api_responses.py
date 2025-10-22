"""
Debug: See what API responses TikTok actually returns
Saves raw API data to JSON for inspection
"""

import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime


async def debug_video_apis(url: str):
    """Capture ALL API responses from a video page"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for debugging
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()
        api_responses = []

        # Capture ALL responses
        async def handle_response(response):
            try:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        data = await response.json()
                        api_responses.append({
                            'url': response.url,
                            'data': data
                        })
                        print(f"📡 Captured: {response.url[:80]}...")
            except:
                pass

        page.on('response', handle_response)

        print(f"🔍 Loading: {url}")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(5000)

        print(f"\n📊 Total API responses captured: {len(api_responses)}")

        # Save raw data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"debug_api_responses_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump(api_responses, f, indent=2)

        print(f"💾 Saved to: {output_file}")
        print("\n🔎 Searching for account data in responses...")

        # Search for account-related fields
        found_account_data = False
        for i, response in enumerate(api_responses):
            data = response['data']
            data_str = json.dumps(data)

            # Look for common account field names
            account_indicators = [
                'followerCount', 'followingCount', 'videoCount',
                'heartCount', 'verified', 'uniqueId', 'stats',
                'author', 'user', 'UserModule', 'userInfo'
            ]

            found_fields = [field for field in account_indicators if field in data_str]

            if found_fields:
                print(f"\n✅ Response {i+1} ({response['url'][:60]}...)")
                print(f"   Found fields: {', '.join(found_fields)}")
                found_account_data = True

                # Try to extract the actual data structure
                if 'userInfo' in data:
                    print("   📦 userInfo structure found:")
                    if 'user' in data['userInfo']:
                        print(f"      uniqueId: {data['userInfo']['user'].get('uniqueId', 'N/A')}")
                        print(f"      verified: {data['userInfo']['user'].get('verified', 'N/A')}")
                    if 'stats' in data['userInfo']:
                        stats = data['userInfo']['stats']
                        print(f"      followerCount: {stats.get('followerCount', 'N/A')}")
                        print(f"      videoCount: {stats.get('videoCount', 'N/A')}")

                if 'UserModule' in data:
                    print("   📦 UserModule structure found:")
                    for user_id, user_data in data['UserModule'].items():
                        if isinstance(user_data, dict):
                            print(f"      User ID: {user_id[:20]}...")
                            print(f"      uniqueId: {user_data.get('uniqueId', 'N/A')}")
                            if 'stats' in user_data:
                                print(f"      followerCount: {user_data['stats'].get('followerCount', 'N/A')}")

        if not found_account_data:
            print("❌ NO account data found in any API response!")
            print("   This explains why enrichment is failing.")
            print("\n💡 Next steps:")
            print("   1. Check if TikTok changed their API structure")
            print("   2. Try scraping from HTML/DOM instead of API")
            print("   3. Consider using official TikTok API if available")

        await browser.close()


async def main():
    """Debug a sample video URL"""
    print("=" * 70)
    print("🐛 TikTok API Response Debugger")
    print("=" * 70)
    print()

    # Use first URL from the scraped data
    test_url = "https://www.tiktok.com/t/ZP8AWfapC/"

    await debug_video_apis(test_url)

    print("\n" + "=" * 70)
    print("✅ Debug complete! Check the JSON file for raw API data.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
