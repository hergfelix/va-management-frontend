"""
Account Enrichment V3 - DOM-Based Scraping
Extracts account data directly from visible HTML/DOM instead of API responses
FIXES: Issue #17 - Account enrichment failing with 0% success rate
"""

import asyncio
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path
import logging
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


class DOMAccountEnricher:
    """Scrapes account data from DOM/HTML elements"""

    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.playwright = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def enrich_account(self, username: str, index: int, total: int) -> Optional[dict]:
        """Scrape account data from DOM elements"""
        if username == 'Unknown' or not username:
            return None

        page = await self.context.new_page()

        try:
            logger.info(f"[{index}/{total}] 🔍 Scraping @{username}")
            sys.stdout.flush()

            profile_url = f"https://www.tiktok.com/@{username}"
            await page.goto(profile_url, wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_timeout(3000)  # Wait for dynamic content

            # Extract data from DOM using multiple strategies
            account_data = await self._extract_from_dom(page, username)

            if account_data and account_data.get('account_followers', 0) > 0:
                logger.info(f"   ✅ Followers: {account_data['account_followers']:,}, Posts: {account_data['account_posts']}")
                sys.stdout.flush()
                await page.close()
                return account_data

            logger.warning(f"   ⚠️ No data extracted for @{username}")
            sys.stdout.flush()
            await page.close()
            return None

        except Exception as e:
            logger.error(f"   ❌ Error for @{username}: {str(e)[:50]}")
            sys.stdout.flush()
            await page.close()
            return None

    async def _extract_from_dom(self, page, username: str) -> Optional[dict]:
        """Extract account data from DOM using JavaScript"""
        try:
            # Strategy 1: Extract from visible page elements
            data = await page.evaluate("""
                () => {
                    // Try to find follower count in various possible locations
                    const findNumber = (text) => {
                        if (!text) return 0;
                        // Handle K, M, B suffixes
                        text = text.trim().toUpperCase();
                        let multiplier = 1;
                        if (text.includes('K')) multiplier = 1000;
                        if (text.includes('M')) multiplier = 1000000;
                        if (text.includes('B')) multiplier = 1000000000;
                        const num = parseFloat(text.replace(/[^0-9.]/g, ''));
                        return Math.floor(num * multiplier);
                    };

                    // Look for data-e2e attributes (TikTok's test IDs)
                    const followerEl = document.querySelector('[data-e2e="followers-count"]');
                    const followingEl = document.querySelector('[data-e2e="following-count"]');
                    const likesEl = document.querySelector('[data-e2e="likes-count"]');

                    // Alternative: Look for strong tags with specific patterns
                    const strongTags = document.querySelectorAll('strong');
                    let followers = 0, following = 0, likes = 0, posts = 0;

                    if (followerEl) followers = findNumber(followerEl.textContent);
                    if (followingEl) following = findNumber(followingEl.textContent);
                    if (likesEl) likes = findNumber(likesEl.textContent);

                    // Try to count videos from DOM
                    const videoElements = document.querySelectorAll('[data-e2e="user-post-item"]');
                    if (videoElements.length > 0) posts = videoElements.length;

                    // Look for verified badge
                    const verifiedBadge = document.querySelector('[data-e2e="verified-icon"]');
                    const verified = !!verifiedBadge;

                    return {
                        followers,
                        following,
                        likes,
                        posts,
                        verified
                    };
                }
            """)

            if data and data.get('followers', 0) > 0:
                return {
                    'account_username': username,
                    'account_followers': data.get('followers', 0),
                    'account_following': data.get('following', 0),
                    'account_posts': data.get('posts', 0),
                    'account_likes': data.get('likes', 0),
                    'account_verified': data.get('verified', False)
                }

            # Strategy 2: Try __UNIVERSAL_DATA_FOR_REHYDRATION__ fallback
            universal_data = await page.evaluate("""
                () => {
                    const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
                    if (el) {
                        try {
                            return JSON.parse(el.textContent);
                        } catch (e) {
                            return null;
                        }
                    }
                    return null;
                }
            """)

            if universal_data:
                # Try to extract from universal data structure
                user_detail = universal_data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
                if user_detail and 'userInfo' in user_detail:
                    user_info = user_detail['userInfo']
                    stats = user_info.get('stats', {})
                    user = user_info.get('user', {})

                    return {
                        'account_username': user.get('uniqueId', username),
                        'account_followers': stats.get('followerCount', 0),
                        'account_following': stats.get('followingCount', 0),
                        'account_posts': stats.get('videoCount', 0),
                        'account_likes': stats.get('heartCount', 0),
                        'account_verified': user.get('verified', False)
                    }

            return None

        except Exception as e:
            logger.debug(f"DOM extraction error: {e}")
            return None


async def main():
    """Enrich account data using DOM scraping"""
    print("=" * 70)
    print("📊 ACCOUNT ENRICHMENT V3 - DOM-BASED SCRAPING")
    print("=" * 70)
    sys.stdout.flush()

    # Load data
    df = pd.read_csv('COMPLETE_SCRAPED_DATA_WITH_RETRIES_20251022_163305.csv')

    # Find accounts needing enrichment
    need_enrichment = df[
        (df['account_username'] != 'Unknown') &
        (df['account_followers'] == 0)
    ].copy()

    # Get unique usernames
    unique_usernames = need_enrichment['account_username'].unique().tolist()

    print(f"📋 Total videos: {len(df)}")
    print(f"📋 Videos needing account data: {len(need_enrichment)}")
    print(f"📋 Unique accounts to scrape: {len(unique_usernames)}")
    print()
    print("🚀 Starting DOM-based enrichment...")
    print("=" * 70)
    sys.stdout.flush()

    # Scrape accounts
    async with DOMAccountEnricher(headless=True) as scraper:
        account_data_map = {}
        successful = 0
        failed = 0

        for i, username in enumerate(unique_usernames, 1):
            account_data = await scraper.enrich_account(username, i, len(unique_usernames))

            if account_data:
                account_data_map[username] = account_data
                successful += 1
            else:
                failed += 1

            # Rate limiting
            if i < len(unique_usernames):
                await asyncio.sleep(2)

            # Progress update every 10 accounts
            if i % 10 == 0:
                success_rate = (successful / i) * 100
                print()
                print(f"📊 PROGRESS CHECKPOINT - Account {i}/{len(unique_usernames)}")
                print(f"   ✅ Successful: {successful}")
                print(f"   ❌ Failed: {failed}")
                print(f"   📈 Success Rate: {success_rate:.1f}%")
                print(f"   ⏱️ Estimated Remaining: {(len(unique_usernames) - i) * 5 / 60:.1f} minutes")
                print("=" * 70)
                sys.stdout.flush()

    # Update dataframe
    print()
    print("=" * 70)
    print("📝 UPDATING DATAFRAME")
    print("=" * 70)
    sys.stdout.flush()

    updated_count = 0
    for idx, row in df.iterrows():
        username = row['account_username']
        if username in account_data_map:
            account_info = account_data_map[username]
            df.at[idx, 'account_followers'] = account_info['account_followers']
            df.at[idx, 'account_following'] = account_info['account_following']
            df.at[idx, 'account_posts'] = account_info['account_posts']
            df.at[idx, 'account_likes'] = account_info['account_likes']
            df.at[idx, 'account_verified'] = account_info['account_verified']
            updated_count += 1

    # Save enriched data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ENRICHED_DOM_DATA_{timestamp}.csv"
    df.to_csv(output_file, index=False)

    # Summary
    print()
    print("=" * 70)
    print("✅ ENRICHMENT COMPLETE!")
    print("=" * 70)
    print(f"Updated {updated_count} videos with account data")
    print(f"Enriched {len(account_data_map)} unique accounts")
    print(f"Success Rate: {len(account_data_map)/len(unique_usernames)*100:.1f}%")

    complete_data = len(df[(df['views'] > 0) & (df['account_followers'] > 0)])
    print()
    print(f"📊 FINAL DATA QUALITY:")
    print(f"   Total Videos: {len(df)}")
    print(f"   Complete Data: {complete_data} ({complete_data/len(df)*100:.1f}%)")
    print(f"   Total Followers Tracked: {df['account_followers'].sum():,}")

    print()
    print(f"💾 Enriched data saved to: {output_file}")
    print("=" * 70)
    sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
