"""
Production TikTok Scraper for 237 URLs
Matches target CSV structure with 43 columns
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path
import logging
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionTikTokScraper:
    """Enhanced scraper matching target CSV structure"""

    def __init__(self, cookie_file="tiktok_cookies.json", headless=True):
        self.cookie_file = Path(cookie_file)
        self.headless = headless
        self.browser = None
        self.context = None
        self.playwright = None
        self.api_responses = []

    async def __aenter__(self):
        """Initialize browser with cookies"""
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )

        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )

        # Load cookies
        if self.cookie_file.exists():
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)
                logger.info(f"✅ Loaded {len(cookies)} cookies")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_video(self, url: str, index: int, total: int) -> dict:
        """Scrape single video with full data extraction"""
        page = await self.context.new_page()
        self.api_responses = []

        try:
            # Network interception
            async def handle_response(response):
                if '/api/' in response.url or '/item/' in response.url:
                    try:
                        if response.status == 200:
                            data = await response.json()
                            self.api_responses.append({
                                'url': response.url,
                                'data': data
                            })
                    except:
                        pass

            page.on('response', handle_response)

            logger.info(f"[{index}/{total}] Scraping: {url}")

            # Navigate
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(5000)

            # Extract comprehensive metrics
            metrics = await self._extract_all_fields(page, url)

            await page.close()
            return metrics

        except Exception as e:
            logger.error(f"[{index}/{total}] Error: {e}")
            await page.close()
            return self._empty_row(url, error=str(e))

    async def _extract_all_fields(self, page, url: str) -> dict:
        """Extract all 43 fields matching target CSV"""

        # Initialize with empty structure
        row = self._empty_row(url)

        # Try API extraction first
        api_data = self._extract_from_api()
        if api_data:
            row.update(api_data)
            row['scraping_method'] = 'api_response'
            row['scraping_success'] = True
            row['data_quality'] = 'Complete'
            logger.info(f"   ✅ API: Views={row['views']:,}, Likes={row['likes']:,}, Slides={row['slide_count']}")
            return row

        # Fallback to JavaScript
        js_data = await self._extract_from_javascript(page)
        if js_data:
            row.update(js_data)
            row['scraping_method'] = 'javascript'
            row['scraping_success'] = True
            row['data_quality'] = 'Partial'
            logger.info(f"   ⚠️ JS: Views={row['views']:,}")
            return row

        logger.warning(f"   ❌ No data extracted")
        return row

    def _extract_from_api(self) -> dict:
        """Extract all fields from API responses"""
        for response in self.api_responses:
            try:
                data = response['data']

                if 'itemInfo' in data and 'itemStruct' in data['itemInfo']:
                    item = data['itemInfo']['itemStruct']
                    stats = item.get('stats', {})
                    author = item.get('author', {})
                    music = item.get('music', {})
                    desc_obj = item.get('desc', '')

                    # Extract hashtags from description
                    hashtags = self._extract_hashtags(desc_obj)

                    # Extract slides
                    slides = self._extract_slide_urls(item)

                    result = {
                        # Metrics
                        'views': stats.get('playCount', 0),
                        'likes': stats.get('diggCount', 0),
                        'comments': stats.get('commentCount', 0),
                        'shares': stats.get('shareCount', 0),
                        'bookmarks': stats.get('collectCount', 0),

                        # Account info
                        'account_username': author.get('uniqueId', 'Unknown'),
                        'account_followers': author.get('stats', {}).get('followerCount', 0),
                        'account_following': author.get('stats', {}).get('followingCount', 0),
                        'account_posts': author.get('stats', {}).get('videoCount', 0),
                        'account_likes': author.get('stats', {}).get('heartCount', 0),
                        'account_verified': author.get('verified', False),

                        # Content details
                        'post_description': desc_obj,
                        'hashtags': hashtags,
                        'mentions': self._extract_mentions(desc_obj),
                        'content_length': len(desc_obj) if desc_obj else 0,

                        # Sound/Music
                        'sound_title': music.get('title', ''),
                        'sound_url': music.get('playUrl', ''),
                        'sound_author': music.get('authorName', ''),
                        'has_sound': bool(music.get('id')),

                        # Slides
                        'slide_count': len(slides),
                        **{f'slide_{i+1}': url for i, url in enumerate(slides[:12])}
                    }

                    # Calculate engagement
                    total_eng = result['likes'] + result['comments'] + result['shares'] + result['bookmarks']
                    result['engagement'] = total_eng
                    if result['views'] > 0:
                        result['engagement_rate'] = round((total_eng / result['views']) * 100, 2)

                    return result

            except Exception as e:
                logger.debug(f"API parse error: {e}")
                continue

        return None

    def _extract_hashtags(self, text: str) -> str:
        """Extract hashtags from description"""
        if not text:
            return ''
        hashtags = re.findall(r'#(\w+)', text)
        return ', '.join(hashtags) if hashtags else ''

    def _extract_mentions(self, text: str) -> str:
        """Extract @mentions from description"""
        if not text:
            return ''
        mentions = re.findall(r'@(\w+)', text)
        return ', '.join(mentions) if mentions else ''

    def _extract_slide_urls(self, item: dict) -> list:
        """Extract slide image URLs"""
        slides = []

        # Check imagePost structure
        if 'imagePost' in item and 'images' in item['imagePost']:
            for img in item['imagePost']['images']:
                # Get highest quality URL
                if 'imageURL' in img:
                    if 'urlList' in img['imageURL'] and img['imageURL']['urlList']:
                        slides.append(img['imageURL']['urlList'][0])

        return slides

    async def _extract_from_javascript(self, page) -> dict:
        """Fallback JavaScript extraction"""
        try:
            data = await page.evaluate("""
                () => {
                    const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
                    if (el) return JSON.parse(el.textContent);
                    return null;
                }
            """)

            if data:
                return self._parse_universal_data(data)
        except:
            pass

        return None

    def _parse_universal_data(self, data: dict) -> dict:
        """Parse universal data structure"""
        try:
            if 'ItemModule' in data:
                items = data['ItemModule']
                for item_id, item in items.items():
                    if isinstance(item, dict) and 'stats' in item:
                        stats = item['stats']
                        return {
                            'views': stats.get('playCount', 0),
                            'likes': stats.get('diggCount', 0),
                            'comments': stats.get('commentCount', 0),
                            'shares': stats.get('shareCount', 0),
                            'bookmarks': stats.get('collectCount', 0)
                        }
        except:
            pass

        return None

    def _empty_row(self, url: str, error: str = None) -> dict:
        """Create empty row with all 43 columns"""
        row = {
            'post_url': url,
            'creator': '',
            'set_id': '',
            'va': '',
            'type': '',
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
            'post_description': '',
            'hashtags': '',
            'mentions': '',
            'content_length': 0,
            'sound_title': '',
            'sound_url': '',
            'sound_author': '',
            'has_sound': False,
            'slide_count': 0,
            'scraped_at': datetime.now().isoformat(),
            'scraping_method': 'failed',
            'scraping_success': False,
            'data_quality': 'No Data'
        }

        # Add slide columns
        for i in range(1, 13):
            row[f'slide_{i}'] = ''

        if error:
            row['error'] = error

        return row

    async def scrape_batch(self, urls: list, batch_size: int = 10, delay: int = 2) -> pd.DataFrame:
        """Scrape URLs in batches with progress tracking"""
        all_results = []
        total = len(urls)

        for i in range(0, total, batch_size):
            batch = urls[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            logger.info(f"\n{'='*70}")
            logger.info(f"BATCH {batch_num}/{total_batches} - URLs {i+1} to {min(i+batch_size, total)}")
            logger.info(f"{'='*70}")

            for j, url in enumerate(batch):
                global_index = i + j + 1
                result = await self.scrape_video(url, global_index, total)
                all_results.append(result)

                # Delay between videos
                if global_index < total:
                    await asyncio.sleep(delay)

            # Progress summary
            successful = sum(1 for r in all_results if r['views'] > 0)
            logger.info(f"\n📊 Progress: {len(all_results)}/{total} completed, {successful} successful ({successful/len(all_results)*100:.1f}%)")

        return pd.DataFrame(all_results)


async def main():
    """Main execution"""
    print("🎯 PRODUCTION TIKTOK SCRAPER - 237 URLs")
    print("=" * 70)

    # Load URLs
    urls_file = Path("urls_to_scrape_237.txt")
    if not urls_file.exists():
        print(f"❌ URLs file not found: {urls_file}")
        return

    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    # Remove duplicates
    unique_urls = list(dict.fromkeys(urls))

    print(f"📋 Total URLs: {len(urls)}")
    print(f"📋 Unique URLs: {len(unique_urls)}")
    print(f"🍪 Using cookies: tiktok_cookies.json")
    print(f"⚙️ Batch size: 10 URLs")
    print(f"⏱️ Delay: 2 seconds between videos")
    print(f"⏱️ Estimated time: ~{len(unique_urls) * 10 / 60:.0f} minutes")
    print()

    # Scrape
    async with ProductionTikTokScraper(headless=True) as scraper:
        results_df = await scraper.scrape_batch(unique_urls, batch_size=10, delay=2)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"COMPLETE_SCRAPED_DATA_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)

    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)

    total = len(results_df)
    successful = len(results_df[results_df['views'] > 0])
    success_rate = (successful / total) * 100 if total > 0 else 0

    complete_data = len(results_df[
        (results_df['views'] > 0) &
        (results_df['likes'] > 0) &
        (results_df['account_username'] != 'Unknown')
    ])

    print(f"Total URLs Processed: {total}")
    print(f"Successful Extractions: {successful}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Complete Data (Views + Likes + Account): {complete_data} ({complete_data/total*100:.1f}%)")
    print(f"\nTotal Views: {results_df['views'].sum():,}")
    print(f"Total Likes: {results_df['likes'].sum():,}")
    print(f"Total Comments: {results_df['comments'].sum():,}")
    print(f"Total Shares: {results_df['shares'].sum():,}")
    print(f"Total Bookmarks: {results_df['bookmarks'].sum():,}")
    print(f"Total Engagement: {results_df['engagement'].sum():,}")
    print(f"Average Engagement Rate: {results_df['engagement_rate'].mean():.2f}%")

    print(f"\n💾 Results saved to: {output_file}")

    # Data quality breakdown
    print(f"\n📊 DATA QUALITY BREAKDOWN:")
    quality_counts = results_df['data_quality'].value_counts()
    for quality, count in quality_counts.items():
        print(f"   {quality}: {count} ({count/total*100:.1f}%)")

    if success_rate >= 80:
        print("\n✅ EXCELLENT! High success rate achieved!")
    elif success_rate >= 60:
        print("\n✅ GOOD! Acceptable success rate")
    elif success_rate >= 40:
        print("\n⚠️ MODERATE - Consider checking cookies")
    else:
        print("\n❌ LOW SUCCESS - Check cookies and rate limiting")

    return results_df


if __name__ == "__main__":
    asyncio.run(main())
