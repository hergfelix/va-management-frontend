"""
Enrich Account Data - Fill Missing Follower Counts
Scrapes account profiles to get followers, following, posts, likes, verified status
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AccountEnricher:
    """Scrapes account profiles to enrich data"""

    def __init__(self, cookie_file="tiktok_cookies.json", headless=True):
        self.cookie_file = Path(cookie_file)
        self.headless = headless
        self.browser = None
        self.context = None
        self.playwright = None
        self.api_responses = []

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

        if self.cookie_file.exists():
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)
                logger.info(f"✅ Loaded {len(cookies)} cookies")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def enrich_account(self, username: str, index: int, total: int) -> dict:
        """Scrape account profile for follower data"""
        if username == 'Unknown' or not username:
            return None

        page = await self.context.new_page()
        self.api_responses = []

        try:
            # Setup API interception
            async def handle_response(response):
                if '/api/' in response.url:
                    try:
                        if response.status == 200:
                            data = await response.json()
                            self.api_responses.append({'url': response.url, 'data': data})
                    except:
                        pass

            page.on('response', handle_response)

            logger.info(f"[{index}/{total}] Scraping @{username}")

            # Navigate to profile
            profile_url = f"https://www.tiktok.com/@{username}"
            await page.goto(profile_url, wait_until='networkidle', timeout=20000)
            await page.wait_for_timeout(4000)

            # Extract account data from API
            account_data = self._extract_account_data()

            if account_data:
                logger.info(f"   ✅ Followers: {account_data['account_followers']:,}, Posts: {account_data['account_posts']}")
                await page.close()
                return account_data

            logger.warning(f"   ⚠️ No data found")
            await page.close()
            return None

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            await page.close()
            return None

    def _extract_account_data(self) -> dict:
        """Extract account data from API responses"""
        for response in self.api_responses:
            try:
                data = response['data']

                # Check userInfo structure
                if 'userInfo' in data:
                    user = data['userInfo'].get('user', {})
                    stats = data['userInfo'].get('stats', {})

                    return {
                        'account_username': user.get('uniqueId', ''),
                        'account_followers': stats.get('followerCount', 0),
                        'account_following': stats.get('followingCount', 0),
                        'account_posts': stats.get('videoCount', 0),
                        'account_likes': stats.get('heartCount', 0),
                        'account_verified': user.get('verified', False)
                    }

                # Check UserModule structure
                if 'UserModule' in data:
                    for user_id, user_data in data['UserModule'].items():
                        if isinstance(user_data, dict) and 'stats' in user_data:
                            return {
                                'account_username': user_data.get('uniqueId', ''),
                                'account_followers': user_data.get('stats', {}).get('followerCount', 0),
                                'account_following': user_data.get('stats', {}).get('followingCount', 0),
                                'account_posts': user_data.get('stats', {}).get('videoCount', 0),
                                'account_likes': user_data.get('stats', {}).get('heartCount', 0),
                                'account_verified': user_data.get('verified', False)
                            }

            except Exception as e:
                logger.debug(f"Parse error: {e}")
                continue

        return None


async def main():
    """Enrich account data for all videos"""
    print("📊 ACCOUNT DATA ENRICHMENT")
    print("=" * 70)

    # Load data
    df = pd.read_csv('COMPLETE_SCRAPED_DATA_WITH_RETRIES_20251022_163305.csv')

    # Find accounts needing enrichment
    need_enrichment = df[
        (df['account_username'] != 'Unknown') &
        (df['account_followers'] == 0)
    ].copy()

    # Get unique usernames
    unique_usernames = need_enrichment['account_username'].unique()

    print(f"📋 Total videos: {len(df)}")
    print(f"📋 Videos needing account data: {len(need_enrichment)}")
    print(f"📋 Unique accounts to scrape: {len(unique_usernames)}")
    print()

    # Scrape accounts
    async with AccountEnricher(headless=True) as scraper:
        account_data_map = {}

        for i, username in enumerate(unique_usernames, 1):
            account_data = await scraper.enrich_account(username, i, len(unique_usernames))

            if account_data:
                account_data_map[username] = account_data

            # Rate limiting
            if i < len(unique_usernames):
                await asyncio.sleep(2)

            # Progress update every 20 accounts
            if i % 20 == 0:
                logger.info(f"\n📊 Progress: {i}/{len(unique_usernames)} accounts ({i/len(unique_usernames)*100:.1f}%)\n")

    # Update dataframe with enriched data
    print("\n" + "=" * 70)
    print("📝 UPDATING DATAFRAME")
    print("=" * 70)

    updated_count = 0
    for idx, row in df.iterrows():
        username = row['account_username']
        if username in account_data_map:
            account_info = account_data_map[username]

            # Update account fields
            df.at[idx, 'account_followers'] = account_info['account_followers']
            df.at[idx, 'account_following'] = account_info['account_following']
            df.at[idx, 'account_posts'] = account_info['account_posts']
            df.at[idx, 'account_likes'] = account_info['account_likes']
            df.at[idx, 'account_verified'] = account_info['account_verified']

            updated_count += 1

    # Save enriched data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"COMPLETE_ENRICHED_DATA_{timestamp}.csv"
    df.to_csv(output_file, index=False)

    # Summary
    print(f"\n✅ Updated {updated_count} videos with account data")
    print(f"✅ Enriched {len(account_data_map)} unique accounts")

    # Final stats
    complete_data = len(df[
        (df['views'] > 0) &
        (df['account_followers'] > 0)
    ])

    print(f"\n📊 FINAL ENRICHED DATA:")
    print(f"Total Videos: {len(df)}")
    print(f"With Complete Data (Views + Account): {complete_data} ({complete_data/len(df)*100:.1f}%)")
    print(f"Total Followers Tracked: {df['account_followers'].sum():,}")
    print(f"Average Followers per Account: {df[df['account_followers'] > 0]['account_followers'].mean():.0f}")

    print(f"\n💾 Enriched data saved to: {output_file}")

    return df


if __name__ == "__main__":
    asyncio.run(main())
