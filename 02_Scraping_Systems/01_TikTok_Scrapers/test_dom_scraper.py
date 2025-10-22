"""Quick test of DOM-based account scraper on 3 accounts"""

import asyncio
import sys
sys.path.insert(0, '.')
from enrich_dom_v3 import DOMAccountEnricher


async def test_dom_scraper():
    """Test DOM scraping on 3 sample accounts"""
    print("=" * 70)
    print("🧪 Testing DOM-Based Account Scraper")
    print("=" * 70)
    print()

    test_accounts = ['megannprime', 'tyrabugged', 'sofiathighs']

    async with DOMAccountEnricher(headless=False) as scraper:  # Visible for debugging
        results = []
        for i, username in enumerate(test_accounts, 1):
            print(f"\n🔍 Test {i}/3: @{username}")
            result = await scraper.enrich_account(username, i, len(test_accounts))
            results.append((username, result))
            await asyncio.sleep(2)

    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)

    successful = sum(1 for _, r in results if r is not None)

    for username, result in results:
        if result:
            print(f"✅ @{username}: {result['account_followers']:,} followers, {result['account_posts']} posts")
        else:
            print(f"❌ @{username}: Failed to extract data")

    print()
    print(f"Success Rate: {successful}/{len(test_accounts)} ({successful/len(test_accounts)*100:.0f}%)")
    print("=" * 70)

    if successful > 0:
        print("\n✅ DOM scraping WORKS! Ready to deploy.")
    else:
        print("\n⚠️ DOM scraping needs adjustment. Check selectors.")


if __name__ == "__main__":
    asyncio.run(test_dom_scraper())
