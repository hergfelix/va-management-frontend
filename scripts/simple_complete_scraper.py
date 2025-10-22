"""
Simple Complete TikTok Scraper
SuperClaude Simple Complete TikTok Scraper

This scraper extracts:
1. Post metrics (views, likes, comments, shares)
2. Account details (followers, likes, videos)
3. Individual slides (download & save)
4. Correct comment counts per video
"""

import asyncio
import pandas as pd
import time
import re
import os
import aiohttp
import aiofiles
from datetime import datetime
from playwright.async_api import async_playwright
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleCompleteTikTokScraper:
    """
    Simple complete TikTok scraper with slides download
    """
    
    def __init__(self, headless=True, debug=False):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.playwright = None
        self.slides_dir = "downloaded_slides"
        
        # Create slides directory
        os.makedirs(self.slides_dir, exist_ok=True)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_complete_post(self, post_url: str, creator: str, set_id: int, va: str, post_type: str) -> dict:
        """
        Scrape complete post data including slides
        """
        try:
            logger.info(f"🎯 Scraping complete post: {post_url}")
            
            # Create new page
            page = await self.browser.new_page()
            
            # Set realistic user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info(f"📱 Navigating to: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Debug: Save page content
            if self.debug:
                page_content = await page.content()
                account_name = creator.lower().replace(" ", "")
                with open(f'debug_page_{account_name}_{set_id}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"💾 Debug: Saved page content to debug_page_{account_name}_{set_id}.html")
            
            # Extract all data
            post_data = {
                "post_url": post_url,
                "creator": creator,
                "set_id": set_id,
                "va": va,
                "type": post_type,
                "scraped_at": datetime.now().isoformat()
            }
            
            # 1. Extract post metrics
            post_metrics = await self._extract_post_metrics(page, post_url)
            post_data.update(post_metrics)
            
            # 2. Extract account details
            account_data = await self._extract_account_details(page, post_url)
            post_data.update(account_data)
            
            # 3. Extract and download slides
            slides_data = await self._extract_and_download_slides(page, post_url, creator, set_id)
            post_data.update(slides_data)
            
            # 4. Extract post content
            content_data = await self._extract_post_content(page, post_url)
            post_data.update(content_data)
            
            # 5. Extract sound info
            sound_data = await self._extract_sound_info(page, post_url)
            post_data.update(sound_data)
            
            await page.close()
            
            logger.info(f"✅ Successfully scraped: {creator} - Set #{set_id}")
            return post_data
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape {post_url}: {e}")
            return {
                "post_url": post_url,
                "creator": creator,
                "set_id": set_id,
                "va": va,
                "type": post_type,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "scraping_success": False,
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0, "engagement_rate": 0.0,
                "account_username": "Unknown", "account_followers": 0, "account_following": 0,
                "account_posts": 0, "account_likes": 0, "account_verified": False,
                "slide_count": 0, "slide_urls": "", "slides_downloaded": False,
                "post_description": "", "hashtags": "", "mentions": "",
                "sound_title": "", "sound_url": "", "sound_author": "", "has_sound": False
            }

    async def _extract_post_metrics(self, page, post_url: str) -> dict:
        """
        Extract post metrics (views, likes, comments, shares)
        """
        try:
            logger.info(f"📊 Extracting post metrics from: {post_url}")
            
            # Extract views - try multiple methods
            views = await self._extract_views_comprehensive(page)
            
            # Extract likes
            likes = await self._extract_metric(page, [
                '[data-e2e="like-count"]',
                'strong[data-e2e="like-count"]',
                'div[data-e2e="like-count"]',
                'span[data-e2e="like-count"]'
            ])
            
            # Extract comments
            comments = await self._extract_metric(page, [
                '[data-e2e="comment-count"]',
                'strong[data-e2e="comment-count"]',
                'div[data-e2e="comment-count"]',
                'span[data-e2e="comment-count"]'
            ])
            
            # Extract shares
            shares = await self._extract_metric(page, [
                '[data-e2e="share-count"]',
                'strong[data-e2e="share-count"]',
                'div[data-e2e="share-count"]',
                'span[data-e2e="share-count"]'
            ])
            
            # Extract bookmarks
            bookmarks = await self._extract_metric(page, [
                '[data-e2e="collect-count"]',
                'strong[data-e2e="collect-count"]',
                'div[data-e2e="collect-count"]',
                'span[data-e2e="collect-count"]'
            ])
            
            # Calculate engagement
            total_engagement = likes + comments + shares + bookmarks
            engagement_rate = round((total_engagement / views) * 100, 2) if views > 0 else 0.0
            
            return {
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "bookmarks": bookmarks,
                "engagement": total_engagement,
                "engagement_rate": engagement_rate,
                "scraping_success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting post metrics: {e}")
            return {
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0, "engagement_rate": 0.0, "scraping_success": False
            }

    async def _extract_views_comprehensive(self, page):
        """
        Comprehensive view extraction with multiple methods
        """
        # Method 1: Extract from JSON data in page (most reliable)
        try:
            page_content = await page.content()
            
            # Look for playCount in the JSON data
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"✅ Found views in JSON data: {views}")
                return views
        except Exception as e:
            logger.debug(f"JSON extraction failed: {e}")
        
        # Method 2: Try all possible view selectors
        view_selectors = [
            '[data-e2e="video-views"]',
            '[data-e2e="video-view-count"]',
            '[data-e2e="browse-video-view-count"]',
            'strong[data-e2e="video-views"]',
            'span[data-e2e="video-views"]',
            '.video-count',
            '.view-count'
        ]
        
        for selector in view_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_views(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"✅ Found views with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        logger.warning("⚠️ Could not extract views with any method")
        return 0

    def _looks_like_views(self, text):
        """Check if text looks like view count"""
        text = str(text).lower().strip()
        return (
            'view' in text and 
            any(char.isdigit() for char in text) and
            len(text) < 20
        )

    async def _extract_metric(self, page, selectors):
        """Try multiple selectors to extract a metric"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        return self._parse_metric(text)
            except Exception:
                continue
        return 0

    def _parse_metric(self, text: str) -> int:
        """Parse a metric string (e.g., "10.5K", "1.2M") into an integer"""
        text = text.replace(',', '').strip()
        text = text.lower()

        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        elif 'b' in text:
            return int(float(text.replace('b', '')) * 1000000000)
        else:
            # Extract only digits
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

    async def _extract_account_details(self, page, post_url: str) -> dict:
        """
        Extract account details (followers, likes, videos)
        """
        try:
            logger.info(f"👤 Extracting account details from: {post_url}")
            
            # Extract username from URL or page
            username = await self._extract_username(page, post_url)
            
            # Extract followers
            followers = await self._extract_metric(page, [
                '[data-e2e="followers-count"] strong',
                'strong[data-e2e="followers-count"]',
                'div[data-e2e="followers-count"]',
                'span[data-e2e="followers-count"]'
            ])
            
            # Extract following
            following = await self._extract_metric(page, [
                '[data-e2e="following-count"] strong',
                'strong[data-e2e="following-count"]',
                'div[data-e2e="following-count"]',
                'span[data-e2e="following-count"]'
            ])
            
            # Extract videos/posts
            videos = await self._extract_metric(page, [
                '[data-e2e="video-count"] strong',
                'strong[data-e2e="video-count"]',
                'div[data-e2e="video-count"]',
                'span[data-e2e="video-count"]'
            ])
            
            # Extract likes (account total)
            account_likes = await self._extract_metric(page, [
                '[data-e2e="likes-count"] strong',
                'strong[data-e2e="likes-count"]',
                'div[data-e2e="likes-count"]',
                'span[data-e2e="likes-count"]'
            ])
            
            return {
                "account_username": username,
                "account_followers": followers,
                "account_following": following,
                "account_posts": videos,
                "account_likes": account_likes,
                "account_verified": False  # Would need additional logic to detect
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting account details: {e}")
            return {
                "account_username": "Unknown",
                "account_followers": 0,
                "account_following": 0,
                "account_posts": 0,
                "account_likes": 0,
                "account_verified": False
            }

    async def _extract_username(self, page, post_url: str) -> str:
        """Extract username from page or URL"""
        try:
            # Try to extract from URL
            url_match = re.search(r'@([^/]+)', post_url)
            if url_match:
                return url_match.group(1)
            
            # Try to extract from page
            username_element = await page.query_selector('[data-e2e="user-title"]')
            if username_element:
                text = await username_element.text_content()
                if text:
                    return text.replace('@', '').strip()
            
            return "Unknown"
            
        except Exception:
            return "Unknown"

    async def _extract_and_download_slides(self, page, post_url: str, creator: str, set_id: int) -> dict:
        """
        Extract and download all slides from the post
        """
        try:
            logger.info(f"🖼️ Extracting and downloading slides from: {post_url}")
            
            # Extract slide URLs
            slide_urls = await self._extract_slide_urls(page)
            
            if not slide_urls:
                logger.warning("⚠️ No slides found")
                return {
                    "slide_count": 0,
                    "slide_urls": "",
                    "slides_downloaded": False
                }
            
            # Download slides
            downloaded_slides = []
            for i, slide_url in enumerate(slide_urls):
                try:
                    slide_filename = f"{creator.lower()}_set_{set_id}_slide_{i+1}.jpg"
                    slide_path = os.path.join(self.slides_dir, slide_filename)
                    
                    # Download slide
                    async with aiohttp.ClientSession() as session:
                        async with session.get(slide_url) as response:
                            if response.status == 200:
                                async with aiofiles.open(slide_path, 'wb') as f:
                                    async for chunk in response.content.iter_chunked(8192):
                                        await f.write(chunk)
                                
                                downloaded_slides.append(slide_filename)
                                logger.info(f"✅ Downloaded slide {i+1}: {slide_filename}")
                            else:
                                logger.warning(f"⚠️ Failed to download slide {i+1}: HTTP {response.status}")
                                
                except Exception as e:
                    logger.error(f"❌ Error downloading slide {i+1}: {e}")
            
            return {
                "slide_count": len(slide_urls),
                "slide_urls": "|".join(slide_urls),
                "slides_downloaded": len(downloaded_slides) > 0,
                "downloaded_slides": "|".join(downloaded_slides)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting slides: {e}")
            return {
                "slide_count": 0,
                "slide_urls": "",
                "slides_downloaded": False,
                "downloaded_slides": ""
            }

    async def _extract_slide_urls(self, page) -> list:
        """Extract slide URLs from the page"""
        try:
            # Look for slide images in various selectors
            slide_selectors = [
                'img[data-e2e="slide-image"]',
                'img[class*="slide"]',
                'img[class*="image"]',
                'img[src*="tiktokcdn"]',
                'img[src*="photo"]'
            ]
            
            slide_urls = []
            for selector in slide_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        src = await element.get_attribute('src')
                        if src and 'tiktokcdn' in src and src not in slide_urls:
                            slide_urls.append(src)
                except Exception:
                    continue
            
            # Also try to extract from page content
            try:
                page_content = await page.content()
                # Look for image URLs in the page content
                image_patterns = [
                    r'https://[^"]*tiktokcdn[^"]*\.(?:jpg|jpeg|png|webp)',
                    r'https://[^"]*photo[^"]*\.(?:jpg|jpeg|png|webp)'
                ]
                
                for pattern in image_patterns:
                    matches = re.findall(pattern, page_content)
                    for match in matches:
                        if match not in slide_urls:
                            slide_urls.append(match)
            except Exception:
                pass
            
            logger.info(f"✅ Found {len(slide_urls)} slide URLs")
            return slide_urls
            
        except Exception as e:
            logger.error(f"❌ Error extracting slide URLs: {e}")
            return []

    async def _extract_post_content(self, page, post_url: str) -> dict:
        """
        Extract post content (description, hashtags, mentions)
        """
        try:
            logger.info(f"📝 Extracting post content from: {post_url}")
            
            # Extract description
            description = await self._extract_text(page, [
                '[data-e2e="video-desc"]',
                '.video-meta-caption',
                '.video-description',
                '[class*="description"]'
            ])
            
            # Extract hashtags
            hashtags = await self._extract_hashtags(page)
            
            # Extract mentions
            mentions = await self._extract_mentions(page)
            
            return {
                "post_description": description,
                "hashtags": hashtags,
                "mentions": mentions,
                "content_length": len(description) if description else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting post content: {e}")
            return {
                "post_description": "",
                "hashtags": "",
                "mentions": "",
                "content_length": 0
            }

    async def _extract_sound_info(self, page, post_url: str) -> dict:
        """
        Extract sound/music information
        """
        try:
            logger.info(f"🎵 Extracting sound info from: {post_url}")
            
            # Extract sound title
            sound_title = await self._extract_text(page, [
                '[data-e2e="video-music"]',
                '.music-title',
                '[class*="sound"]',
                '[class*="music"]'
            ])
            
            # Extract sound URL
            sound_url = await self._extract_attribute(page, [
                '[data-e2e="video-music"] a',
                '.music-title a',
                'a[href*="music"]'
            ], 'href')
            
            # Extract sound author
            sound_author = await self._extract_text(page, [
                '.music-author',
                '[class*="sound-author"]',
                '[class*="music-creator"]'
            ])
            
            return {
                "sound_title": sound_title,
                "sound_url": sound_url,
                "sound_author": sound_author,
                "has_sound": bool(sound_title)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting sound info: {e}")
            return {
                "sound_title": "",
                "sound_url": "",
                "sound_author": "",
                "has_sound": False
            }

    # Helper methods
    async def _extract_text(self, page, selectors: list) -> str:
        """Extract text from multiple selectors"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue
        return ""

    async def _extract_attribute(self, page, selectors: list, attribute: str) -> str:
        """Extract attribute from multiple selectors"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    attr_value = await element.get_attribute(attribute)
                    if attr_value:
                        return attr_value
            except Exception:
                continue
        return ""

    async def _extract_hashtags(self, page) -> str:
        """Extract hashtags from page"""
        try:
            hashtag_elements = await page.query_selector_all('a[href*="/tag/"]')
            hashtags = []
            for element in hashtag_elements:
                text = await element.text_content()
                if text and text.startswith('#'):
                    hashtags.append(text)
            return "|".join(hashtags)
        except Exception:
            return ""

    async def _extract_mentions(self, page) -> str:
        """Extract mentions from page"""
        try:
            mention_elements = await page.query_selector_all('a[href*="/@"]')
            mentions = []
            for element in mention_elements:
                text = await element.text_content()
                if text and text.startswith('@'):
                    mentions.append(text)
            return "|".join(mentions)
        except Exception:
            return ""

    async def scrape_multiple_posts(self, posts_data: list) -> pd.DataFrame:
        """
        Scrape multiple posts and return DataFrame
        """
        results = []
        
        for i, post_data in enumerate(posts_data, 1):
            logger.info(f"📊 Scraping post {i}/{len(posts_data)}: {post_data['creator']} - Set #{post_data['set_id']}")
            
            result = await self.scrape_complete_post(
                post_data['post_url'],
                post_data['creator'],
                post_data['set_id'],
                post_data['va'],
                post_data['type']
            )
            
            results.append(result)
            
            # Add delay between posts
            if i < len(posts_data):
                await asyncio.sleep(2)
        
        return pd.DataFrame(results)

async def main():
    """Main execution"""
    print("🎯 SIMPLE COMPLETE TIKTOK SCRAPER")
    print("=" * 60)
    
    # Test posts data
    posts_data = [
        {
            "post_url": "https://www.tiktok.com/t/ZTMmT78be/",
            "creator": "Mara",
            "set_id": 19,
            "va": "Leah",
            "type": "New"
        },
        {
            "post_url": "https://www.tiktok.com/t/ZTMmTvGqd/",
            "creator": "Sofia",
            "set_id": 89,
            "va": "Pilar",
            "type": "REPOST"
        },
        {
            "post_url": "https://www.tiktok.com/t/ZP8AWUGAJ/",
            "creator": "Tyra",
            "set_id": 4,
            "va": "Kyle",
            "type": "REPOST"
        }
    ]
    
    print(f"🎯 Target: {len(posts_data)} posts")
    print("📊 Data to extract:")
    print("   • Post metrics (views, likes, comments, shares)")
    print("   • Account details (followers, likes, videos)")
    print("   • Individual slides (download & save)")
    print("   • Post content (description, hashtags, mentions)")
    print("   • Sound information")
    print()
    
    # Scrape all posts
    async with SimpleCompleteTikTokScraper(headless=True, debug=True) as scraper:
        results_df = await scraper.scrape_multiple_posts(posts_data)
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"simple_complete_scraped_data_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n🎯 COMPLETE SCRAPING RESULTS:")
    print("=" * 60)
    
    for i, row in results_df.iterrows():
        print(f"\n📹 POST {i+1}: {row['creator']} - Set #{row['set_id']}")
        print(f"   URL: {row['post_url']}")
        print(f"   VA: {row['va']}")
        print(f"   Type: {row['type']}")
        print(f"   Views: {row['views']:,}")
        print(f"   Likes: {row['likes']:,}")
        print(f"   Comments: {row['comments']:,}")
        print(f"   Shares: {row['shares']:,}")
        print(f"   Engagement Rate: {row['engagement_rate']:.2f}%")
        print(f"   Account: @{row['account_username']}")
        print(f"   Followers: {row['account_followers']:,}")
        print(f"   Account Likes: {row['account_likes']:,}")
        print(f"   Slides: {row['slide_count']} (Downloaded: {row['slides_downloaded']})")
        print(f"   Description: {row['post_description'][:50]}..." if row['post_description'] else "   Description: None")
        print(f"   Hashtags: {row['hashtags']}")
        print(f"   Sound: {row['sound_title']}" if row['sound_title'] else "   Sound: None")
        print(f"   Success: {row['scraping_success']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"🖼️ Slides saved to: downloaded_slides/")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(main())
