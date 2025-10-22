"""
Reliable TikTok Scraper - Cookie-Based with Network Interception
Production-ready scraper that handles TikTok's anti-bot protection

Strategy:
- Load real user cookies for authentication
- Wait for JavaScript to execute fully
- Intercept API network requests for data
- Extract metrics from loaded React components
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReliableTikTokScraper:
    """
    Production TikTok scraper with cookie authentication and network interception
    """

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

        # Launch browser with anti-detection
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )

        # Create context and load cookies
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )

        # Load cookies if they exist
        if self.cookie_file.exists():
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
                await self.context.add_cookies(cookies)
                logger.info(f"✅ Loaded {len(cookies)} cookies")
        else:
            logger.warning(f"⚠️ Cookie file not found: {self.cookie_file}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_video(self, url: str) -> dict:
        """
        Scrape a single TikTok video with network interception
        """
        page = await self.context.new_page()
        self.api_responses = []

        try:
            # Setup network interception
            async def handle_response(response):
                # Capture API responses containing video data
                if '/api/' in response.url or '/item/' in response.url:
                    try:
                        if response.status == 200:
                            data = await response.json()
                            self.api_responses.append({
                                'url': response.url,
                                'data': data
                            })
                            logger.debug(f"📡 Captured API response: {response.url[:100]}")
                    except:
                        pass

            page.on('response', handle_response)

            logger.info(f"🎯 Scraping: {url}")

            # Navigate to video
            await page.goto(url, wait_until='networkidle', timeout=30000)

            # Wait for React app to load
            await page.wait_for_timeout(5000)

            # Try to extract data from multiple sources
            metrics = await self._extract_metrics_comprehensive(page, url)

            await page.close()
            return metrics

        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            await page.close()
            return self._empty_metrics(url, error=str(e))

    async def _extract_metrics_comprehensive(self, page, url: str) -> dict:
        """
        Extract metrics using multiple fallback methods
        """
        metrics = {
            'post_url': url,
            'scraped_at': datetime.now().isoformat(),
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'bookmarks': 0,
            'account_username': 'Unknown',
            'account_followers': 0,
            'extraction_method': 'none'
        }

        # Method 1: Try API responses (most reliable)
        api_data = self._extract_from_api_responses()
        if api_data:
            metrics.update(api_data)
            metrics['extraction_method'] = 'api_response'
            logger.info(f"✅ API extraction: Views={metrics['views']:,}, Likes={metrics['likes']:,}")
            return metrics

        # Method 2: Try JavaScript evaluation
        js_data = await self._extract_from_javascript(page)
        if js_data:
            metrics.update(js_data)
            metrics['extraction_method'] = 'javascript'
            logger.info(f"✅ JS extraction: Views={metrics['views']:,}, Likes={metrics['likes']:,}")
            return metrics

        # Method 3: Try DOM selectors (fallback)
        dom_data = await self._extract_from_dom(page)
        if dom_data:
            metrics.update(dom_data)
            metrics['extraction_method'] = 'dom'
            logger.info(f"✅ DOM extraction: Views={metrics['views']:,}, Likes={metrics['likes']:,}")
            return metrics

        logger.warning(f"⚠️ No data extracted for {url}")
        return metrics

    def _extract_from_api_responses(self) -> dict:
        """Extract metrics from captured API responses"""
        for response in self.api_responses:
            try:
                data = response['data']

                # Check for itemInfo structure
                if 'itemInfo' in data and 'itemStruct' in data['itemInfo']:
                    item = data['itemInfo']['itemStruct']
                    stats = item.get('stats', {})
                    author = item.get('author', {})

                    return {
                        'views': stats.get('playCount', 0),
                        'likes': stats.get('diggCount', 0),
                        'comments': stats.get('commentCount', 0),
                        'shares': stats.get('shareCount', 0),
                        'bookmarks': stats.get('collectCount', 0),
                        'account_username': author.get('uniqueId', 'Unknown'),
                        'account_followers': author.get('stats', {}).get('followerCount', 0)
                    }

                # Check for other API structures
                if 'stats' in data:
                    stats = data['stats']
                    if 'playCount' in stats or 'diggCount' in stats:
                        return {
                            'views': stats.get('playCount', 0),
                            'likes': stats.get('diggCount', 0),
                            'comments': stats.get('commentCount', 0),
                            'shares': stats.get('shareCount', 0),
                            'bookmarks': stats.get('collectCount', 0)
                        }

            except Exception as e:
                logger.debug(f"Error parsing API response: {e}")
                continue

        return None

    async def _extract_from_javascript(self, page) -> dict:
        """Extract metrics from JavaScript window object"""
        try:
            # Try to access React app data
            data = await page.evaluate("""
                () => {
                    // Try to find data in window.__UNIVERSAL_DATA_FOR_REHYDRATION__
                    const universalData = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
                    if (universalData) {
                        const data = JSON.parse(universalData.textContent);
                        return data;
                    }

                    // Try window.SIGI_STATE
                    if (window.SIGI_STATE) {
                        return window.SIGI_STATE;
                    }

                    return null;
                }
            """)

            if data:
                # Parse the data structure
                return self._parse_universal_data(data)

        except Exception as e:
            logger.debug(f"JavaScript extraction failed: {e}")

        return None

    def _parse_universal_data(self, data: dict) -> dict:
        """Parse TikTok's universal data structure"""
        try:
            # Navigate through the data structure to find video info
            # This structure may vary, add more paths as discovered

            # Check for ItemModule
            if 'ItemModule' in data:
                items = data['ItemModule']
                for item_id, item in items.items():
                    if isinstance(item, dict) and 'stats' in item:
                        stats = item['stats']
                        author = item.get('author', {})
                        return {
                            'views': stats.get('playCount', 0),
                            'likes': stats.get('diggCount', 0),
                            'comments': stats.get('commentCount', 0),
                            'shares': stats.get('shareCount', 0),
                            'bookmarks': stats.get('collectCount', 0),
                            'account_username': author.get('uniqueId', 'Unknown'),
                            'account_followers': author.get('stats', {}).get('followerCount', 0)
                        }

            # Add more parsing logic as needed

        except Exception as e:
            logger.debug(f"Error parsing universal data: {e}")

        return None

    async def _extract_from_dom(self, page) -> dict:
        """Extract metrics from DOM elements (least reliable)"""
        try:
            # Try strong tags with data-e2e attributes
            selectors = {
                'likes': '[data-e2e="like-count"] strong',
                'comments': '[data-e2e="comment-count"] strong',
                'shares': '[data-e2e="share-count"] strong',
                'bookmarks': '[data-e2e="browse-collect-count"] strong'
            }

            result = {}
            for metric, selector in selectors.items():
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        result[metric] = self._parse_count(text)
                except:
                    result[metric] = 0

            if any(result.values()):
                return result

        except Exception as e:
            logger.debug(f"DOM extraction failed: {e}")

        return None

    def _parse_count(self, text: str) -> int:
        """Parse count strings like '10.5K' into integers"""
        if not text:
            return 0

        text = text.strip().upper().replace(',', '')

        try:
            if 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            elif 'B' in text:
                return int(float(text.replace('B', '')) * 1000000000)
            else:
                return int(text)
        except:
            return 0

    def _empty_metrics(self, url: str, error: str = None) -> dict:
        """Return empty metrics structure"""
        return {
            'post_url': url,
            'scraped_at': datetime.now().isoformat(),
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'bookmarks': 0,
            'account_username': 'Unknown',
            'account_followers': 0,
            'extraction_method': 'failed',
            'error': error
        }

    async def scrape_multiple(self, urls: list, delay: int = 3) -> pd.DataFrame:
        """Scrape multiple videos with delay between requests"""
        results = []

        for i, url in enumerate(urls, 1):
            logger.info(f"📹 Scraping video {i}/{len(urls)}")
            metrics = await self.scrape_video(url)
            results.append(metrics)

            # Add delay between requests (except last one)
            if i < len(urls):
                await asyncio.sleep(delay)

        return pd.DataFrame(results)


async def main():
    """Test the scraper with sample URLs"""
    print("🎯 RELIABLE TIKTOK SCRAPER - Cookie-Based with Network Interception")
    print("=" * 70)

    # Test URLs
    test_urls = [
        "https://www.tiktok.com/t/ZTMuUscW9/",
        "https://www.tiktok.com/t/ZTMuUEG3c/",
        "https://www.tiktok.com/t/ZTMuyRh5a/",
        "https://www.tiktok.com/t/ZP8A7kX4w/",
        "https://www.tiktok.com/t/ZP8A7L74E/"
    ]

    print(f"📋 Testing with {len(test_urls)} URLs")
    print(f"🍪 Using cookies from: tiktok_cookies.json")
    print()

    # Run scraper
    async with ReliableTikTokScraper(headless=True) as scraper:
        results_df = await scraper.scrape_multiple(test_urls)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"reliable_scraper_results_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)

    # Display results
    print("\n" + "=" * 70)
    print("📊 SCRAPING RESULTS")
    print("=" * 70)

    for i, row in results_df.iterrows():
        print(f"\n📹 VIDEO {i+1}: {row['post_url']}")
        print(f"   Method: {row['extraction_method']}")
        print(f"   Views: {row['views']:,}")
        print(f"   Likes: {row['likes']:,}")
        print(f"   Comments: {row['comments']:,}")
        print(f"   Shares: {row['shares']:,}")
        print(f"   Bookmarks: {row['bookmarks']:,}")
        print(f"   Account: @{row['account_username']}")
        print(f"   Followers: {row['account_followers']:,}")

    # Summary
    successful = len(results_df[results_df['views'] > 0])
    success_rate = (successful / len(results_df)) * 100

    print(f"\n📊 SUMMARY:")
    print(f"   Total Videos: {len(results_df)}")
    print(f"   Successful Extractions: {successful}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Total Views: {results_df['views'].sum():,}")
    print(f"   Total Engagement: {(results_df['likes'] + results_df['comments']).sum():,}")

    print(f"\n💾 Results saved to: {output_file}")

    if success_rate >= 60:
        print("\n✅ SUCCESS! Scraper is working reliably!")
    elif success_rate >= 20:
        print("\n⚠️ PARTIAL SUCCESS - Needs optimization")
    else:
        print("\n❌ FAILED - Investigate blocking mechanisms")

    return results_df


if __name__ == "__main__":
    asyncio.run(main())
