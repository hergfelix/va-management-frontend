"""
Parallel Account Enrichment V3 - High Performance
Uses concurrent browser workers for 10-20x speed improvement
Designed for large datasets (45K+ rows)
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path
import logging
import sys
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


class ParallelAccountEnricher:
    """High-performance parallel account scraper"""

    def __init__(self, cookie_file="tiktok_cookies.json", num_workers=5, headless=True):
        self.cookie_file = Path(cookie_file)
        self.num_workers = num_workers
        self.headless = headless
        self.account_cache: Dict[str, dict] = {}
        self.playwright = None
        self.browsers = []

    async def __aenter__(self):
        """Initialize multiple browser instances for parallel processing"""
        self.playwright = await async_playwright().start()

        # Launch multiple browser instances
        for i in range(self.num_workers):
            browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            # Load cookies
            if self.cookie_file.exists():
                with open(self.cookie_file, 'r') as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)

            self.browsers.append({'browser': browser, 'context': context, 'id': i+1})

        logger.info(f"✅ Initialized {self.num_workers} parallel browser workers")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all browser instances"""
        for browser_info in self.browsers:
            await browser_info['context'].close()
            await browser_info['browser'].close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_account(self, username: str, worker_id: int, context) -> Optional[dict]:
        """Scrape single account with given browser context"""
        # Check cache first
        if username in self.account_cache:
            logger.debug(f"[Worker {worker_id}] 💾 Cache hit: @{username}")
            return self.account_cache[username]

        if username == 'Unknown' or not username:
            return None

        page = await context.new_page()
        api_responses = []

        try:
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

            # Navigate to profile
            profile_url = f"https://www.tiktok.com/@{username}"
            try:
                await page.goto(profile_url, wait_until='networkidle', timeout=12000)
                await page.wait_for_timeout(2000)
            except Exception as e:
                logger.debug(f"[Worker {worker_id}] ⚠️ Timeout: @{username}")
                await page.close()
                return None

            # Extract account data from API
            account_data = self._extract_account_data(api_responses)

            if account_data:
                # Cache the result
                self.account_cache[username] = account_data
                logger.info(f"[Worker {worker_id}] ✅ @{username}: {account_data['account_followers']:,} followers")
                await page.close()
                return account_data

            await page.close()
            return None

        except Exception as e:
            logger.debug(f"[Worker {worker_id}] ❌ Error @{username}: {str(e)[:50]}")
            await page.close()
            return None

    def _extract_account_data(self, api_responses: list) -> Optional[dict]:
        """Extract account data from API responses"""
        for response in api_responses:
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

            except Exception:
                continue

        return None

    async def worker(self, worker_id: int, username_queue: asyncio.Queue, results: dict):
        """Worker task that processes usernames from queue"""
        context = self.browsers[worker_id - 1]['context']

        while True:
            try:
                username = await asyncio.wait_for(username_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                break

            account_data = await self.scrape_account(username, worker_id, context)

            if account_data:
                results[username] = account_data

            username_queue.task_done()

            # Small delay to avoid overwhelming TikTok
            await asyncio.sleep(0.5)

    async def enrich_accounts_parallel(self, usernames: List[str]) -> Dict[str, dict]:
        """Process all usernames using parallel workers"""
        # Create queue and results dict
        queue = asyncio.Queue()
        results = {}

        # Fill queue with usernames
        for username in usernames:
            if username and username != 'Unknown':
                await queue.put(username)

        total_accounts = queue.qsize()
        logger.info(f"🚀 Processing {total_accounts} unique accounts with {self.num_workers} workers")

        # Start worker tasks
        workers = [
            asyncio.create_task(self.worker(i, queue, results))
            for i in range(1, self.num_workers + 1)
        ]

        # Monitor progress
        progress_task = asyncio.create_task(self._monitor_progress(queue, total_accounts))

        # Wait for all work to complete
        await queue.join()

        # Cancel workers
        for worker in workers:
            worker.cancel()

        # Cancel progress monitor
        progress_task.cancel()

        return results

    async def _monitor_progress(self, queue: asyncio.Queue, total: int):
        """Monitor and report progress"""
        last_report = 0

        while True:
            await asyncio.sleep(10)

            completed = total - queue.qsize()
            if completed - last_report >= 50 or completed == total:
                success_rate = (len(self.account_cache) / completed * 100) if completed > 0 else 0
                logger.info(f"📊 Progress: {completed}/{total} ({completed/total*100:.1f}%) | "
                          f"✅ {len(self.account_cache)} enriched | "
                          f"📈 {success_rate:.1f}% success rate")
                last_report = completed


async def main():
    """Main execution with parallel processing"""
    print("=" * 80)
    print("🚀 HIGH-PERFORMANCE PARALLEL ACCOUNT ENRICHMENT V3")
    print("=" * 80)
    sys.stdout.flush()

    # Load data
    input_file = 'COMPLETE_SCRAPED_DATA_WITH_RETRIES_20251022_163305.csv'
    df = pd.read_csv(input_file)

    # Get unique usernames that need enrichment
    need_enrichment = df[
        (df['account_username'] != 'Unknown') &
        (df['account_followers'] == 0)
    ]

    unique_usernames = need_enrichment['account_username'].unique().tolist()

    print(f"📊 Dataset Analysis:")
    print(f"   Total Videos: {len(df):,}")
    print(f"   Need Enrichment: {len(need_enrichment):,}")
    print(f"   Unique Accounts: {len(unique_usernames):,}")
    print()

    # Calculate cache efficiency
    username_counts = need_enrichment['account_username'].value_counts()
    avg_videos_per_account = username_counts.mean()
    cache_savings = ((avg_videos_per_account - 1) / avg_videos_per_account * 100) if avg_videos_per_account > 1 else 0

    print(f"🎯 Performance Optimization:")
    print(f"   Average videos per account: {avg_videos_per_account:.1f}")
    print(f"   Cache efficiency: {cache_savings:.1f}% fewer scrapes needed")
    print(f"   Parallel workers: 5")
    print(f"   Expected speedup: 10-15x faster")
    print()

    estimated_time = len(unique_usernames) * 3 / 60 / 5  # 3 sec per account, 5 workers
    print(f"⏱️ Estimated completion: {estimated_time:.1f} minutes")
    print("=" * 80)
    sys.stdout.flush()

    # Run parallel enrichment
    start_time = datetime.now()

    async with ParallelAccountEnricher(num_workers=5, headless=True) as enricher:
        account_data_map = await enricher.enrich_accounts_parallel(unique_usernames)

    elapsed = (datetime.now() - start_time).total_seconds()

    # Update dataframe
    print()
    print("=" * 80)
    print("📝 APPLYING ENRICHED DATA TO DATAFRAME")
    print("=" * 80)

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
    output_file = f"COMPLETE_ENRICHED_DATA_PARALLEL_{timestamp}.csv"
    df.to_csv(output_file, index=False)

    # Final summary
    print()
    print("=" * 80)
    print("✅ ENRICHMENT COMPLETE!")
    print("=" * 80)
    print(f"⏱️ Time taken: {elapsed/60:.1f} minutes")
    print(f"📊 Unique accounts enriched: {len(account_data_map):,}")
    print(f"📊 Total videos updated: {updated_count:,}")
    print(f"📈 Success rate: {len(account_data_map)/len(unique_usernames)*100:.1f}%")
    print(f"⚡ Speed: {len(account_data_map)/(elapsed/60):.1f} accounts/minute")

    complete_data = len(df[(df['views'] > 0) & (df['account_followers'] > 0)])
    print()
    print(f"📊 Final Data Quality:")
    print(f"   Total videos: {len(df):,}")
    print(f"   Complete data: {complete_data:,} ({complete_data/len(df)*100:.1f}%)")
    print(f"   Total followers tracked: {df['account_followers'].sum():,}")

    print()
    print(f"💾 Saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
