"""
Generate Fresh TikTok Cookies
Opens browser, lets you login, then saves cookies
"""

import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path


async def generate_cookies():
    """Interactive cookie generation"""
    print("=" * 70)
    print("🍪 TIKTOK COOKIE GENERATOR")
    print("=" * 70)
    print()
    print("This will:")
    print("1. Open a browser window")
    print("2. Navigate to TikTok")
    print("3. Wait for you to login")
    print("4. Save your cookies to tiktok_cookies.json")
    print()
    print("⚠️  Make sure you:")
    print("   - Login to your TikTok account")
    print("   - Navigate to a few profiles")
    print("   - Verify you can see follower counts")
    print()
    input("Press Enter to continue...")
    print()

    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()

        # Navigate to TikTok
        print("📱 Opening TikTok...")
        await page.goto('https://www.tiktok.com')

        print()
        print("=" * 70)
        print("👤 PLEASE LOGIN TO TIKTOK")
        print("=" * 70)
        print()
        print("Instructions:")
        print("1. Login to your TikTok account in the browser")
        print("2. Visit a few profile pages (e.g., https://www.tiktok.com/@charlidamelio)")
        print("3. Verify you can see follower counts and profile data")
        print("4. Come back here and press Enter when ready")
        print()

        input("Press Enter after you've logged in and verified access...")
        print()

        # Get cookies
        cookies = await context.cookies()

        # Save to file
        cookie_file = Path("tiktok_cookies.json")
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print("=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"Saved {len(cookies)} cookies to {cookie_file}")
        print()
        print("Cookie details:")
        for cookie in cookies:
            if 'tiktok' in cookie['domain'].lower():
                print(f"   - {cookie['name']}: {cookie['value'][:20]}...")
        print()
        print("You can now run the enrichment script!")
        print()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(generate_cookies())
