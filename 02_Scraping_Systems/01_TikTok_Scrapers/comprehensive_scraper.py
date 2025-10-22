"""
Comprehensive TikTok Scraper - Video + Account Data
Combines video metrics scraping with account profile enrichment
For large-scale dataset processing (10 → 50 → 200+ videos)
"""

import asyncio
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright
import logging
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


class ComprehensiveTikTokScraper:
    """Scrapes both video metrics and account data in one pass"""

    def __init__(self, headless=True):
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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_video_and_account(self, url: str, index: int, total: int, metadata: dict) -> dict:
        """Scrape BOTH video data and account data (requires 2 page loads)"""
        page = await self.context.new_page()
        self.api_responses = []

        try:
            # Setup API interception
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

            logger.info(f"[{index}/{total}] 🔍 Scraping: {url}")
            sys.stdout.flush()

            # STEP 1: Navigate to video to get video metrics and username
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)

            # Extract video data and username from video page
            video_universal_data = await page.evaluate("""
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

            # Extract video metrics and username
            video_data = self._extract_video_data(video_universal_data, url, metadata)
            if not video_data or video_data.get('views', 0) == 0:
                # Try API fallback
                video_data = self._extract_from_api(url, metadata)
                if not video_data or video_data.get('views', 0) == 0:
                    logger.warning(f"   ⚠️ No video data found for {url}")
                    sys.stdout.flush()
                    await page.close()
                    return self._empty_row(url, metadata)

            username = video_data.get('account_username', 'Unknown')

            # STEP 2: Navigate to profile page to get complete account data
            if username and username != 'Unknown':
                profile_url = f"https://www.tiktok.com/@{username}"
                await page.goto(profile_url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(2000)

                # Extract account data from profile page
                profile_universal_data = await page.evaluate("""
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

                account_data = self._extract_account_data(profile_universal_data, username)
                if account_data:
                    # Merge video data with account data
                    video_data.update(account_data)

            logger.info(f"   ✅ Video: {video_data['views']:,} views, {video_data['likes']:,} likes | "
                      f"Account: {video_data.get('account_followers', 0):,} followers")
            sys.stdout.flush()
            await page.close()
            return video_data

        except Exception as e:
            logger.error(f"   ❌ Error: {str(e)[:50]}")
            sys.stdout.flush()
            await page.close()
            return self._empty_row(url, metadata, error=str(e))

    def _extract_video_data(self, universal_data: dict, url: str, metadata: dict) -> Optional[dict]:
        """Extract ONLY video metrics and username from video page"""
        if not universal_data:
            return None

        try:
            default_scope = universal_data.get('__DEFAULT_SCOPE__', {})
            video_detail = default_scope.get('webapp.video-detail', {})
            if not video_detail or 'itemInfo' not in video_detail:
                return None

            item_info = video_detail['itemInfo']['itemStruct']
            stats = item_info.get('stats', {})
            author = item_info.get('author', {})
            music = item_info.get('music', {})
            desc = item_info.get('desc', '')

            # Extract slides for carousel posts
            slides = []
            if 'imagePost' in item_info and 'images' in item_info['imagePost']:
                for img in item_info['imagePost']['images']:
                    if 'imageURL' in img and 'urlList' in img['imageURL']:
                        slides.append(img['imageURL']['urlList'][0])

            return {
                # Metadata from CSV
                'post_url': url,
                'creator': metadata.get('creator', ''),
                'set_id': metadata.get('set_id', ''),
                'va': metadata.get('va', ''),
                'type': metadata.get('type', ''),

                # Video metrics
                'views': stats.get('playCount', 0),
                'likes': stats.get('diggCount', 0),
                'comments': stats.get('commentCount', 0),
                'shares': stats.get('shareCount', 0),
                'bookmarks': stats.get('collectCount', 0),
                'engagement': (stats.get('diggCount', 0) + stats.get('commentCount', 0) +
                             stats.get('shareCount', 0) + stats.get('collectCount', 0)),
                'engagement_rate': round(((stats.get('diggCount', 0) + stats.get('commentCount', 0) +
                                          stats.get('shareCount', 0) + stats.get('collectCount', 0)) /
                                         max(stats.get('playCount', 1), 1)) * 100, 2),

                # Username only (account stats filled later from profile page)
                'account_username': author.get('uniqueId', 'Unknown'),
                'account_followers': 0,
                'account_following': 0,
                'account_posts': 0,
                'account_likes': 0,
                'account_verified': author.get('verified', False),

                # Content details
                'post_description': desc,
                'hashtags': self._extract_hashtags(desc),
                'mentions': self._extract_mentions(desc),
                'content_length': len(desc),

                # Sound/Music
                'sound_title': music.get('title', ''),
                'sound_author': music.get('authorName', ''),
                'has_sound': bool(music.get('id')),

                # Slides
                'slide_count': len(slides),
                **{f'slide_{i+1}': url for i, url in enumerate(slides[:12])},

                # Metadata
                'scraped_at': datetime.now().isoformat(),
                'scraping_method': 'video_page',
                'scraping_success': True,
                'data_quality': 'Video Complete',
                'error': ''
            }

        except Exception as e:
            logger.debug(f"Video data extraction error: {e}")
            return None

    def _extract_account_data(self, universal_data: dict, username: str) -> Optional[dict]:
        """Extract ONLY account stats from profile page (same logic as enrich_dom_v3.py)"""
        if not universal_data:
            return None

        try:
            # Profile pages have webapp.user-detail section with complete stats
            default_scope = universal_data.get('__DEFAULT_SCOPE__', {})
            user_detail = default_scope.get('webapp.user-detail', {})

            if not user_detail or 'userInfo' not in user_detail:
                return None

            user_info = user_detail['userInfo']
            stats = user_info.get('stats', {})
            user = user_info.get('user', {})

            # Validate we got real data
            if stats.get('followerCount', 0) > 0 or stats.get('videoCount', 0) > 0:
                return {
                    'account_followers': stats.get('followerCount', 0),
                    'account_following': stats.get('followingCount', 0),
                    'account_posts': stats.get('videoCount', 0),
                    'account_likes': stats.get('heartCount', 0),
                    'account_verified': user.get('verified', False),
                    'data_quality': 'Complete'  # Now we have both video + account
                }

            return None

        except Exception as e:
            logger.debug(f"Account data extraction error: {e}")
            return None

    def _extract_from_api(self, url: str, metadata: dict) -> Optional[dict]:
        """Fallback: Extract video data from API responses (account stats set to 0)"""
        for response in self.api_responses:
            try:
                data = response['data']

                # Check for itemInfo/itemStruct
                if 'itemInfo' in data and 'itemStruct' in data['itemInfo']:
                    item = data['itemInfo']['itemStruct']
                    stats = item.get('stats', {})
                    author = item.get('author', {})
                    music = item.get('music', {})
                    desc = item.get('desc', '')

                    # Extract slides for carousel posts
                    slides = []
                    if 'imagePost' in item and 'images' in item['imagePost']:
                        for img in item['imagePost']['images']:
                            if 'imageURL' in img and 'urlList' in img['imageURL']:
                                slides.append(img['imageURL']['urlList'][0])

                    return {
                        'post_url': url,
                        'creator': metadata.get('creator', ''),
                        'set_id': metadata.get('set_id', ''),
                        'va': metadata.get('va', ''),
                        'type': metadata.get('type', ''),
                        'views': stats.get('playCount', 0),
                        'likes': stats.get('diggCount', 0),
                        'comments': stats.get('commentCount', 0),
                        'shares': stats.get('shareCount', 0),
                        'bookmarks': stats.get('collectCount', 0),
                        'engagement': stats.get('diggCount', 0) + stats.get('commentCount', 0) + stats.get('shareCount', 0),
                        'engagement_rate': round((stats.get('diggCount', 0) + stats.get('commentCount', 0) + stats.get('shareCount', 0)) / max(stats.get('playCount', 1), 1) * 100, 2),

                        # Username only, stats filled later from profile page
                        'account_username': author.get('uniqueId', 'Unknown'),
                        'account_followers': 0,
                        'account_following': 0,
                        'account_posts': 0,
                        'account_likes': 0,
                        'account_verified': author.get('verified', False),

                        # Content details
                        'post_description': desc,
                        'hashtags': self._extract_hashtags(desc),
                        'mentions': self._extract_mentions(desc),
                        'content_length': len(desc),

                        # Sound/Music
                        'sound_title': music.get('title', ''),
                        'sound_author': music.get('authorName', ''),
                        'has_sound': bool(music.get('id')),

                        # Slides
                        'slide_count': len(slides),
                        **{f'slide_{i+1}': url for i, url in enumerate(slides[:12])},

                        'scraped_at': datetime.now().isoformat(),
                        'scraping_method': 'api_response',
                        'scraping_success': True,
                        'data_quality': 'Video Complete',
                        'error': ''
                    }
            except:
                continue

        return None

    def _extract_hashtags(self, text: str) -> str:
        """Extract hashtags from description"""
        import re
        if not text:
            return ''
        hashtags = re.findall(r'#(\w+)', text)
        return ', '.join(hashtags) if hashtags else ''

    def _extract_mentions(self, text: str) -> str:
        """Extract mentions from description"""
        import re
        if not text:
            return ''
        mentions = re.findall(r'@(\w+)', text)
        return ', '.join(mentions) if mentions else ''

    def _empty_row(self, url: str, metadata: dict, error: str = '') -> dict:
        """Create empty row with metadata"""
        return {
            'post_url': url,
            'creator': metadata.get('creator', ''),
            'set_id': metadata.get('set_id', ''),
            'va': metadata.get('va', ''),
            'type': metadata.get('type', ''),
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
            'sound_author': '',
            'has_sound': False,
            'slide_count': 0,
            'slide_1': '',
            'slide_2': '',
            'slide_3': '',
            'slide_4': '',
            'slide_5': '',
            'slide_6': '',
            'slide_7': '',
            'slide_8': '',
            'slide_9': '',
            'slide_10': '',
            'slide_11': '',
            'slide_12': '',
            'scraped_at': datetime.now().isoformat(),
            'scraping_method': 'failed',
            'scraping_success': False,
            'data_quality': 'Failed',
            'error': error[:100]
        }


async def main(num_videos: int):
    """Run comprehensive scraper on specified number of videos"""
    print("=" * 80)
    print(f"🚀 COMPREHENSIVE TIKTOK SCRAPER - {num_videos} VIDEOS")
    print("=" * 80)
    print("📊 Extracting: Video Metrics + Account Data")
    print("=" * 80)
    sys.stdout.flush()

    # Load proof log CSV
    df = pd.read_csv('/Users/felixhergenroeder/Downloads/Proof Log v2 - Proof_Log (1).csv')

    # Select first N videos
    df_subset = df.head(num_videos).copy()

    print(f"📋 Total videos in CSV: {len(df)}")
    print(f"📋 Scraping first: {len(df_subset)}")
    print()
    print("🚀 Starting scraper...")
    print("=" * 80)
    sys.stdout.flush()

    results = []
    start_time = datetime.now()

    async with ComprehensiveTikTokScraper(headless=True) as scraper:
        for idx, row in df_subset.iterrows():
            url = row['Post URL']
            metadata = {
                'creator': row.get('Creator', ''),
                'set_id': row.get('Set ID', ''),
                'va': row.get('VA', ''),
                'type': row.get('Type', '')
            }

            result = await scraper.scrape_video_and_account(url, idx + 1, len(df_subset), metadata)
            results.append(result)

            # Rate limiting
            if idx < len(df_subset) - 1:
                await asyncio.sleep(2)

            # Progress checkpoint every 10 videos
            if (idx + 1) % 10 == 0:
                successful = sum(1 for r in results if r['scraping_success'])
                success_rate = (successful / len(results)) * 100
                print()
                print(f"📊 CHECKPOINT - Video {idx + 1}/{len(df_subset)}")
                print(f"   ✅ Successful: {successful}/{len(results)} ({success_rate:.1f}%)")
                print(f"   ⏱️ Elapsed: {(datetime.now() - start_time).total_seconds() / 60:.1f} min")
                print("=" * 80)
                sys.stdout.flush()

    # Save results
    elapsed = (datetime.now() - start_time).total_seconds()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"COMPREHENSIVE_SCRAPED_{num_videos}_VIDEOS_{timestamp}.csv"

    df_results = pd.DataFrame(results)
    df_results.to_csv(output_file, index=False)

    # Summary
    successful = sum(1 for r in results if r['scraping_success'])
    with_account = sum(1 for r in results if r['account_followers'] > 0)

    print()
    print("=" * 80)
    print("✅ SCRAPING COMPLETE!")
    print("=" * 80)
    print(f"⏱️ Time: {elapsed / 60:.1f} minutes ({elapsed / len(results):.1f} sec/video)")
    print(f"📊 Videos scraped: {len(results)}")
    print(f"   ✅ Successful: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"   ❌ Failed: {len(results) - successful}")
    print(f"   👤 With account data: {with_account} ({with_account/len(results)*100:.1f}%)")
    print()
    print(f"💾 Saved to: {output_file}")
    print("=" * 80)
    sys.stdout.flush()


if __name__ == "__main__":
    import sys
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(main(num))
