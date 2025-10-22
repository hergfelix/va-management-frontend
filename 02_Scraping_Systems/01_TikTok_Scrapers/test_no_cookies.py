"""
Quick Test: Enrichment WITHOUT Cookies
Tests if TikTok cookies are actually required
"""

import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime


async def test_account_without_cookies(username: str):
    """Test scraping a single account WITHOUT loading cookies"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        # NO COOKIES LOADED - testing if it works without them

        page = await context.new_page()
        api_responses = []

        # Setup API interception
        async def handle_response(response):
            if '/api/' in response.url:
                try:
                    if response.status == 200:
                        data = await response.json()
                        api_responses.append({'url': response.url, 'data': data})
                except:
                    pass

        page.on('response', handle_response)

        try:
            print(f"🔍 Testing @{username} WITHOUT cookies...")
            profile_url = f"https://www.tiktok.com/@{username}"
            await page.goto(profile_url, wait_until='networkidle', timeout=15000)
            await page.wait_for_timeout(3000)

            # Try to extract data
            for response in api_responses:
                try:
                    data = response['data']

                    if 'userInfo' in data:
                        user = data['userInfo'].get('user', {})
                        stats = data['userInfo'].get('stats', {})

                        result = {
                            'username': user.get('uniqueId', ''),
                            'followers': stats.get('followerCount', 0),
                            'following': stats.get('followingCount', 0),
                            'posts': stats.get('videoCount', 0),
                            'likes': stats.get('heartCount', 0),
                            'verified': user.get('verified', False)
                        }

                        print(f"   ✅ SUCCESS: {result['followers']:,} followers, {result['posts']} posts")
                        await browser.close()
                        return result

                    if 'UserModule' in data:
                        for user_id, user_data in data['UserModule'].items():
                            if isinstance(user_data, dict) and 'stats' in user_data:
                                result = {
                                    'username': user_data.get('uniqueId', ''),
                                    'followers': user_data.get('stats', {}).get('followerCount', 0),
                                    'following': user_data.get('stats', {}).get('followingCount', 0),
                                    'posts': user_data.get('stats', {}).get('videoCount', 0),
                                    'likes': user_data.get('stats', {}).get('heartCount', 0),
                                    'verified': user_data.get('verified', False)
                                }

                                print(f"   ✅ SUCCESS: {result['followers']:,} followers, {result['posts']} posts")
                                await browser.close()
                                return result

                except Exception:
                    continue

            print(f"   ❌ FAILED: No data found")
            await browser.close()
            return None

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)[:50]}")
            await browser.close()
            return None


async def main():
    """Test 5 accounts WITHOUT cookies"""
    print("=" * 70)
    print("🧪 COOKIE TEST: Scraping WITHOUT Cookies")
    print("=" * 70)
    print()

    # Test 5 random accounts from our list
    test_accounts = [
        'megannprime',
        'tyrabugged',
        'maracloudd',
        'sofiathighs',
        'nalanisynths'
    ]

    results = []
    successful = 0
    failed = 0

    for username in test_accounts:
        result = await test_account_without_cookies(username)
        if result:
            successful += 1
            results.append(result)
        else:
            failed += 1

        await asyncio.sleep(2)  # Rate limiting

    print()
    print("=" * 70)
    print("📊 TEST RESULTS WITHOUT COOKIES")
    print("=" * 70)
    print(f"✅ Successful: {successful}/5 ({successful/5*100:.0f}%)")
    print(f"❌ Failed: {failed}/5 ({failed/5*100:.0f}%)")
    print()

    if successful > 0:
        print("✅ CONCLUSION: Cookies are NOT required!")
        print("   The cookie loading is NOT the problem.")
        print("   Something else is preventing data extraction.")
    else:
        print("⚠️ CONCLUSION: Cookies might be required")
        print("   All accounts failed without cookies too.")

    print("=" * 70)

    return successful, failed


if __name__ == "__main__":
    asyncio.run(main())
