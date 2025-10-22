"""
Retry Failed URLs with Account-Level Scraping
For videos that failed, try to extract account data from the profile page
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AccountFallbackScraper:
    """Scraper that falls back to account profile when video scraping fails"""

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

    async def scrape_video_with_fallback(self, url: str, index: int, total: int) -> dict:
        """Try video scraping, fall back to account scraping if it fails"""
        logger.info(f"[{index}/{total}] Retrying: {url}")

        # Try video first
        video_data = await self._scrape_video(url)
        if video_data and video_data.get('views', 0) > 0:
            logger.info(f"   ✅ Video data found: Views={video_data['views']:,}")
            return video_data

        # Video failed, try to resolve and scrape account
        logger.warning(f"   ⚠️ Video failed, trying account fallback...")
        account_data = await self._scrape_account_fallback(url)

        if account_data and account_data.get('account_username') != 'Unknown':
            logger.info(f"   ✅ Account data: @{account_data['account_username']}, Followers={account_data.get('account_followers', 0):,}")
            return account_data

        logger.error(f"   ❌ Both methods failed")
        return self._empty_row(url)

    async def _scrape_video(self, url: str) -> dict:
        """Try to scrape video directly"""
        page = await self.context.new_page()
        self.api_responses = []

        try:
            async def handle_response(response):
                if '/api/' in response.url:
                    try:
                        if response.status == 200:
                            data = await response.json()
                            self.api_responses.append({'url': response.url, 'data': data})
                    except:
                        pass

            page.on('response', handle_response)

            # Navigate with shorter timeout
            await page.goto(url, wait_until='networkidle', timeout=20000)
            await page.wait_for_timeout(3000)

            # Try to extract from API
            for response in self.api_responses:
                try:
                    data = response['data']
                    if 'itemInfo' in data and 'itemStruct' in data['itemInfo']:
                        item = data['itemInfo']['itemStruct']
                        result = self._extract_video_data(item)
                        await page.close()
                        return result
                except:
                    continue

            await page.close()
            return None

        except Exception as e:
            await page.close()
            return None

    async def _scrape_account_fallback(self, video_url: str) -> dict:
        """Scrape account profile as fallback"""
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

            # First, try to resolve the short URL to get username
            logger.info(f"      Resolving redirect URL...")
            response = await page.goto(video_url, wait_until='domcontentloaded', timeout=15000)
            final_url = page.url

            # Extract username from final URL
            username_match = re.search(r'@([^/]+)', final_url)
            if not username_match:
                await page.close()
                return None

            username = username_match.group(1)
            logger.info(f"      Found account: @{username}")

            # Navigate to profile page
            profile_url = f"https://www.tiktok.com/@{username}"
            await page.goto(profile_url, wait_until='networkidle', timeout=20000)
            await page.wait_for_timeout(5000)

            # Extract account data from API responses
            account_data = self._extract_account_from_api()
            if account_data:
                account_data['post_url'] = video_url
                account_data['scraped_at'] = datetime.now().isoformat()
                account_data['scraping_method'] = 'account_fallback'
                account_data['scraping_success'] = True
                account_data['data_quality'] = 'Account Only'
                await page.close()
                return account_data

            await page.close()
            return None

        except Exception as e:
            logger.debug(f"      Account fallback error: {e}")
            await page.close()
            return None

    def _extract_account_from_api(self) -> dict:
        """Extract account data from API responses"""
        for response in self.api_responses:
            try:
                data = response['data']

                # Check for user module
                if 'userInfo' in data:
                    user = data['userInfo'].get('user', {})
                    stats = data['userInfo'].get('stats', {})

                    return {
                        'account_username': user.get('uniqueId', 'Unknown'),
                        'account_followers': stats.get('followerCount', 0),
                        'account_following': stats.get('followingCount', 0),
                        'account_posts': stats.get('videoCount', 0),
                        'account_likes': stats.get('heartCount', 0),
                        'account_verified': user.get('verified', False),
                        'views': 0,  # No video data
                        'likes': 0,
                        'comments': 0,
                        'shares': 0,
                        'bookmarks': 0,
                        'engagement': 0,
                        'engagement_rate': 0.0
                    }

                # Check for UserModule structure
                if 'UserModule' in data:
                    for user_id, user_data in data['UserModule'].items():
                        if isinstance(user_data, dict) and 'stats' in user_data:
                            return {
                                'account_username': user_data.get('uniqueId', 'Unknown'),
                                'account_followers': user_data.get('stats', {}).get('followerCount', 0),
                                'account_following': user_data.get('stats', {}).get('followingCount', 0),
                                'account_posts': user_data.get('stats', {}).get('videoCount', 0),
                                'account_likes': user_data.get('stats', {}).get('heartCount', 0),
                                'account_verified': user_data.get('verified', False),
                                'views': 0,
                                'likes': 0,
                                'comments': 0,
                                'shares': 0,
                                'bookmarks': 0,
                                'engagement': 0,
                                'engagement_rate': 0.0
                            }

            except Exception as e:
                logger.debug(f"API parse error: {e}")
                continue

        return None

    def _extract_video_data(self, item: dict) -> dict:
        """Extract full video data"""
        stats = item.get('stats', {})
        author = item.get('author', {})

        return {
            'post_url': '',  # Will be set by caller
            'views': stats.get('playCount', 0),
            'likes': stats.get('diggCount', 0),
            'comments': stats.get('commentCount', 0),
            'shares': stats.get('shareCount', 0),
            'bookmarks': stats.get('collectCount', 0),
            'account_username': author.get('uniqueId', 'Unknown'),
            'account_followers': author.get('stats', {}).get('followerCount', 0),
            'account_following': author.get('stats', {}).get('followingCount', 0),
            'account_posts': author.get('stats', {}).get('videoCount', 0),
            'account_likes': author.get('stats', {}).get('heartCount', 0),
            'account_verified': author.get('verified', False),
            'scraped_at': datetime.now().isoformat(),
            'scraping_method': 'video_retry',
            'scraping_success': True,
            'data_quality': 'Complete'
        }

    def _empty_row(self, url: str) -> dict:
        """Empty row for failed scraping"""
        return {
            'post_url': url,
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'bookmarks': 0,
            'engagement': 0,
            'engagement_rate': 0.0,
            'account_username': 'Unknown',
            'account_followers': 0,
            'account_following': 0,
            'account_posts': 0,
            'account_likes': 0,
            'account_verified': False,
            'scraped_at': datetime.now().isoformat(),
            'scraping_method': 'failed',
            'scraping_success': False,
            'data_quality': 'No Data'
        }


async def main():
    """Retry failed URLs"""
    print("🔄 RETRY FAILED URLS WITH ACCOUNT FALLBACK")
    print("=" * 70)

    # Load original scraped data
    df = pd.read_csv('COMPLETE_SCRAPED_DATA_20251022_061444.csv')
    failed = df[df['views'] == 0].copy()

    print(f"📊 Found {len(failed)} failed URLs to retry")
    print()

    failed_urls = failed['post_url'].tolist()

    # Retry with account fallback
    async with AccountFallbackScraper(headless=True) as scraper:
        results = []
        for i, url in enumerate(failed_urls, 1):
            result = await scraper.scrape_video_with_fallback(url, i, len(failed_urls))
            results.append(result)

            if i < len(failed_urls):
                await asyncio.sleep(3)

    # Create results dataframe
    retry_df = pd.DataFrame(results)

    # Update original dataframe
    for idx, row in retry_df.iterrows():
        url = row['post_url']
        mask = df['post_url'] == url

        # Update all columns from retry
        for col in retry_df.columns:
            if col in df.columns:
                df.loc[mask, col] = row[col]

    # Save updated results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"COMPLETE_SCRAPED_DATA_WITH_RETRIES_{timestamp}.csv"
    df.to_csv(output_file, index=False)

    # Summary
    print("\n" + "=" * 70)
    print("📊 RETRY RESULTS")
    print("=" * 70)

    retry_successful = len(retry_df[retry_df['scraping_success'] == True])
    print(f"Retry Attempts: {len(retry_df)}")
    print(f"Successful: {retry_successful}")
    print(f"Still Failed: {len(retry_df) - retry_successful}")

    # Final stats
    final_successful = len(df[df['views'] > 0]) + len(retry_df[
        (retry_df['scraping_success'] == True) & (retry_df['account_username'] != 'Unknown')
    ])
    total = len(df)

    print(f"\n📊 FINAL COMBINED RESULTS:")
    print(f"Total URLs: {total}")
    print(f"With Data: {final_successful}")
    print(f"Success Rate: {final_successful/total*100:.1f}%")

    print(f"\n💾 Updated results saved to: {output_file}")

    return df


if __name__ == "__main__":
    asyncio.run(main())
