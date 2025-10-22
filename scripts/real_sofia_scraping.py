"""
Real TikTok Scraping - Sofia's Post
SuperClaude Real Data Extraction Agent

Real scraping of Sofia's TikTok post:
- URL: https://www.tiktok.com/t/ZTMure1j4/
- Creator: Sofia
- Set #86
- VA: Almira
- Type: NEW
"""

import asyncio
import pandas as pd
import time
import re
from datetime import datetime
from playwright.async_api import async_playwright
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealSofiaScraper:
    """
    Real TikTok scraper for Sofia's post using Playwright
    """
    
    def __init__(self, headless=True, debug=True):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_sofia_post(self, post_url: str) -> dict:
        """
        Scrape Sofia's TikTok post for REAL metrics
        """
        try:
            # Create new page
            page = await self.browser.new_page()
            
            # Set realistic user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info(f"🔍 Scraping Sofia's post: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(5000)
            
            # Debug: Save page content for analysis
            if self.debug:
                page_content = await page.content()
                with open('sofia_post_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info("💾 Debug: Saved page content to sofia_post_debug.html")
            
            # Extract ALL possible data
            scraped_data = await self._extract_all_data(page, post_url)
            
            await page.close()
            return scraped_data
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape Sofia's post: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False
            }

    async def _extract_all_data(self, page, post_url):
        """
        Extract ALL possible data from Sofia's post
        """
        data = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat(),
            "success": True
        }
        
        try:
            # Extract post metrics
            logger.info("📊 Extracting post metrics...")
            data.update(await self._extract_post_metrics(page))
            
            # Extract account information
            logger.info("👤 Extracting account information...")
            data.update(await self._extract_account_info(page))
            
            # Extract content analysis
            logger.info("🎨 Extracting content analysis...")
            data.update(await self._extract_content_analysis(page))
            
            # Extract additional metadata
            logger.info("📋 Extracting additional metadata...")
            data.update(await self._extract_additional_metadata(page))
            
            logger.info("✅ All data extraction completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error extracting data: {e}")
            data["extraction_error"] = str(e)
            data["success"] = False
        
        return data

    async def _extract_post_metrics(self, page):
        """Extract post performance metrics"""
        metrics = {}
        
        try:
            # Extract views - try multiple methods
            views = await self._extract_views_comprehensive(page)
            metrics["views"] = views
            
            # Extract likes
            likes = await self._extract_metric(page, [
                '[data-e2e="like-count"]',
                'strong[data-e2e="like-count"]',
                'div[data-e2e="like-count"]',
                'span[data-e2e="like-count"]',
                '[class*="like"] strong',
                '[class*="Like"] strong'
            ])
            metrics["likes"] = likes

            # Extract comments
            comments = await self._extract_metric(page, [
                '[data-e2e="comment-count"]',
                'strong[data-e2e="comment-count"]',
                'div[data-e2e="comment-count"]',
                'span[data-e2e="comment-count"]',
                '[class*="comment"] strong',
                '[class*="Comment"] strong'
            ])
            metrics["comments"] = comments

            # Extract shares
            shares = await self._extract_metric(page, [
                '[data-e2e="share-count"]',
                'strong[data-e2e="share-count"]',
                'div[data-e2e="share-count"]',
                'span[data-e2e="share-count"]',
                '[class*="share"] strong',
                '[class*="Share"] strong'
            ])
            metrics["shares"] = shares

            # Extract bookmarks
            bookmarks = await self._extract_metric(page, [
                '[data-e2e="collect-count"]',
                'strong[data-e2e="collect-count"]',
                'div[data-e2e="collect-count"]',
                'span[data-e2e="collect-count"]',
                '[class*="collect"] strong',
                '[class*="Collect"] strong'
            ])
            metrics["bookmarks"] = bookmarks

            # Calculate engagement
            total_engagement = metrics["likes"] + metrics["comments"] + metrics["shares"] + metrics["bookmarks"]
            metrics["engagement"] = total_engagement
            
            if metrics["views"] > 0:
                metrics["engagement_rate"] = round((total_engagement / metrics["views"]) * 100, 2)
            else:
                metrics["engagement_rate"] = 0.0
            
            logger.info(f"📊 Post metrics: {metrics['views']:,} views, {metrics['likes']:,} likes, {metrics['engagement_rate']:.2f}% engagement")
            
        except Exception as e:
            logger.error(f"❌ Error extracting post metrics: {e}")
            metrics["metrics_error"] = str(e)
        
        return metrics

    async def _extract_account_info(self, page):
        """Extract account information"""
        account_info = {}
        
        try:
            # Extract username
            username = await self._extract_text(page, [
                '[data-e2e="browse-username"]',
                'h1[data-e2e="browse-username"]',
                '[class*="username"]',
                '[class*="Username"]'
            ])
            account_info["username"] = username.replace('@', '') if username else ""
            
            # Extract followers
            followers = await self._extract_metric(page, [
                '[data-e2e="followers-count"] strong',
                'strong[data-e2e="followers-count"]',
                '[class*="follower"] strong',
                '[class*="Follower"] strong'
            ])
            account_info["followers"] = followers
            
            # Extract following
            following = await self._extract_metric(page, [
                '[data-e2e="following-count"] strong',
                'strong[data-e2e="following-count"]',
                '[class*="following"] strong',
                '[class*="Following"] strong'
            ])
            account_info["following"] = following
            
            # Extract bio
            bio = await self._extract_text(page, [
                '[data-e2e="browse-desc"]',
                '[class*="bio"]',
                '[class*="Bio"]',
                '[class*="description"]'
            ])
            account_info["bio"] = bio
            
            # Extract verification status
            verified_element = await page.query_selector('[data-e2e="browse-verified"]')
            account_info["verified"] = verified_element is not None
            
            logger.info(f"👤 Account: @{account_info['username']}, {account_info['followers']:,} followers")
            
        except Exception as e:
            logger.error(f"❌ Error extracting account info: {e}")
            account_info["account_error"] = str(e)
        
        return account_info

    async def _extract_content_analysis(self, page):
        """Extract content analysis"""
        content = {}
        
        try:
            # Extract hashtags
            hashtags = await self._extract_hashtags(page)
            content["hashtags"] = hashtags
            
            # Extract sound/music info
            sound_title = await self._extract_text(page, [
                '[data-e2e="browse-music"]',
                '[class*="music"]',
                '[class*="sound"]',
                '[class*="Music"]',
                '[class*="Sound"]'
            ])
            content["sound_title"] = sound_title
            
            # Extract description
            description = await self._extract_text(page, [
                '[data-e2e="browse-desc"]',
                '[class*="description"]',
                '[class*="caption"]'
            ])
            content["description"] = description
            
            # Count slides (look for slide indicators)
            slide_elements = await page.query_selector_all('[class*="slide"], [class*="dot"], [class*="indicator"]')
            content["slides_count"] = len(slide_elements) if slide_elements else 1
            
            logger.info(f"🎨 Content: {len(hashtags)} hashtags, {content['slides_count']} slides")
            
        except Exception as e:
            logger.error(f"❌ Error extracting content analysis: {e}")
            content["content_error"] = str(e)
        
        return content

    async def _extract_additional_metadata(self, page):
        """Extract additional metadata"""
        metadata = {}
        
        try:
            # Extract page title
            title = await page.title()
            metadata["page_title"] = title
            
            # Extract URL after redirects
            current_url = page.url
            metadata["final_url"] = current_url
            
            # Extract any additional data from page content
            page_content = await page.content()
            
            # Look for any JSON data in the page
            json_matches = re.findall(r'<script[^>]*>.*?({.*?}).*?</script>', page_content, re.DOTALL)
            if json_matches:
                metadata["found_json_data"] = len(json_matches)
            
            # Extract any additional metrics that might be in the page
            all_numbers = re.findall(r'\b(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\b', page_content)
            metadata["all_numbers_found"] = all_numbers[:10]  # First 10 numbers found
            
        except Exception as e:
            logger.error(f"❌ Error extracting additional metadata: {e}")
            metadata["metadata_error"] = str(e)
        
        return metadata

    async def _extract_views_comprehensive(self, page):
        """Comprehensive view extraction"""
        # Method 1: Extract from JSON data in page
        try:
            page_content = await page.content()
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"✅ Found views in JSON: {views:,}")
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
            '[class*="view"]',
            '[class*="View"]'
        ]
        
        for selector in view_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_views(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"✅ Found views with selector '{selector}': {parsed:,}")
                            return parsed
            except Exception:
                continue
        
        logger.warning("⚠️ Could not extract views with any method")
        return 0

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

    async def _extract_text(self, page, selectors):
        """Try multiple selectors to extract text"""
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

    async def _extract_hashtags(self, page):
        """Extract hashtags from the page"""
        hashtags = []
        try:
            # Look for hashtag elements
            hashtag_elements = await page.query_selector_all('a[href*="/tag/"], [class*="hashtag"], [class*="Hashtag"]')
            for element in hashtag_elements:
                text = await element.text_content()
                if text and text.startswith('#'):
                    hashtags.append(text)
            
            # Also look for hashtags in description
            description = await self._extract_text(page, ['[data-e2e="browse-desc"]'])
            if description:
                hashtag_matches = re.findall(r'#\w+', description)
                hashtags.extend(hashtag_matches)
            
            # Remove duplicates
            hashtags = list(set(hashtags))
            
        except Exception as e:
            logger.error(f"Error extracting hashtags: {e}")
        
        return hashtags

    def _looks_like_views(self, text):
        """Check if text looks like view count"""
        text = str(text).lower().strip()
        return (
            'view' in text and 
            any(char.isdigit() for char in text) and
            len(text) < 20
        )

    def _parse_metric(self, text: str) -> int:
        """Parse a metric string into an integer"""
        text = text.replace(',', '').strip()
        text = text.lower()

        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        elif 'b' in text:
            return int(float(text.replace('b', '')) * 1000000000)
        else:
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

async def main():
    """Main execution function"""
    print("🎯 REAL TIKTOK SCRAPING - SOFIA'S POST")
    print("=" * 60)
    
    # Sofia's post details
    post_url = "https://www.tiktok.com/t/ZTMure1j4/"
    creator = "Sofia"
    set_id = 86
    va = "Almira"
    post_type = "NEW"
    
    print(f"🔍 Target: {post_url}")
    print(f"👤 Creator: {creator}")
    print(f"📦 Set: #{set_id}")
    print(f"👥 VA: {va}")
    print(f"📝 Type: {post_type}")
    print()
    
    # Run real scraping
    async with RealSofiaScraper(headless=True, debug=True) as scraper:
        scraped_data = await scraper.scrape_sofia_post(post_url)
    
    # Add metadata
    scraped_data.update({
        "creator": creator,
        "set_id": set_id,
        "va": va,
        "post_type": post_type,
        "extraction_method": "Real Playwright Scraping"
    })
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"sofia_real_scraping_results_{timestamp}.json"
    
    import json
    with open(output_file, 'w') as f:
        json.dump(scraped_data, f, indent=2, default=str)
    
    print("\n📊 REAL SCRAPING RESULTS:")
    print("=" * 60)
    
    if scraped_data.get("success", False):
        print("✅ Scraping successful!")
        print(f"📊 Views: {scraped_data.get('views', 0):,}")
        print(f"❤️ Likes: {scraped_data.get('likes', 0):,}")
        print(f"💬 Comments: {scraped_data.get('comments', 0):,}")
        print(f"📤 Shares: {scraped_data.get('shares', 0):,}")
        print(f"🔖 Bookmarks: {scraped_data.get('bookmarks', 0):,}")
        print(f"📈 Engagement Rate: {scraped_data.get('engagement_rate', 0):.2f}%")
        print(f"👤 Username: @{scraped_data.get('username', 'N/A')}")
        print(f"👥 Followers: {scraped_data.get('followers', 0):,}")
        print(f"🎨 Hashtags: {', '.join(scraped_data.get('hashtags', []))}")
        print(f"🎵 Sound: {scraped_data.get('sound_title', 'N/A')}")
        print(f"📱 Slides: {scraped_data.get('slides_count', 0)}")
    else:
        print("❌ Scraping failed!")
        print(f"Error: {scraped_data.get('error', 'Unknown error')}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return scraped_data

if __name__ == "__main__":
    asyncio.run(main())
