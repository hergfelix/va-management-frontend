"""
Scrape Your 3 Specific Links
SuperClaude Your 3 Links Scraper

This uses the EXACT SAME scraper that worked for the other videos
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

class Your3LinksScraper:
    """
    EXACT SAME scraper that worked for the other videos
    """
    
    def __init__(self, headless=True, debug=False):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.playwright = None
        
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

    async def _scrape_single_post(self, post_url: str, creator: str, set_id: int, va: str, post_type: str) -> dict:
        """
        EXACT SAME method that worked for the other videos
        """
        try:
            # Create new page
            page = await self.browser.new_page()
            
            # Set realistic user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info(f"Scraping: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Debug: Save page content for analysis
            if self.debug:
                page_content = await page.content()
                account_name = creator.lower().replace(" ", "")
                with open(f'debug_page_{account_name}_{set_id}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"Debug: Saved page content to debug_page_{account_name}_{set_id}.html")
            
            # Extract metrics - EXACT SAME method
            metrics = await self._extract_metrics(page, post_url, creator, set_id, va, post_type)
            
            await page.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to scrape {post_url}: {e}")
            return {
                "post_url": post_url,
                "creator": creator,
                "set_id": set_id,
                "va": va,
                "type": post_type,
                "scraped_at": datetime.now().isoformat(),
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0, "engagement_rate": 0.0,
                "account_username": "Unknown", "account_followers": 0,
                "error": str(e)
            }

    async def _extract_metrics(self, page, post_url, creator, set_id, va, post_type):
        """
        EXACT SAME extraction method that worked
        """
        metrics = {
            "post_url": post_url,
            "creator": creator,
            "set_id": set_id,
            "va": va,
            "type": post_type,
            "scraped_at": datetime.now().isoformat()
        }
        
        try:
            # Extract views - EXACT SAME method that found 988, 1973, 307, 717, 404 views
            views = await self._extract_views_comprehensive(page)
            metrics["views"] = views
            
            # Extract likes - EXACT SAME method
            likes = await self._extract_metric(page, [
                '[data-e2e="like-count"]',
                '.tiktok-1ceb17a-DivActionItem.e1p3s28g10 > strong',
                'strong[data-e2e="like-count"]',
                'div[data-e2e="like-count"]',
                'span[data-e2e="like-count"]'
            ])
            metrics["likes"] = likes

            # Extract comments - EXACT SAME method
            comments = await self._extract_metric(page, [
                '[data-e2e="comment-count"]',
                '.tiktok-1ceb17a-DivActionItem.e1p3s28g10 > strong',
                'strong[data-e2e="comment-count"]',
                'div[data-e2e="comment-count"]',
                'span[data-e2e="comment-count"]'
            ])
            metrics["comments"] = comments

            # Extract shares - EXACT SAME method
            shares = await self._extract_metric(page, [
                '[data-e2e="share-count"]',
                '.tiktok-1ceb17a-DivActionItem.e1p3s28g10 > strong',
                'strong[data-e2e="share-count"]',
                'div[data-e2e="share-count"]',
                'span[data-e2e="share-count"]'
            ])
            metrics["shares"] = shares

            # Extract bookmarks - EXACT SAME method
            bookmarks = await self._extract_metric(page, [
                '[data-e2e="collect-count"]',
                'strong[data-e2e="collect-count"]',
                'div[data-e2e="collect-count"]',
                'span[data-e2e="collect-count"]'
            ])
            metrics["bookmarks"] = bookmarks

            # Calculate engagement - EXACT SAME method
            total_engagement = metrics["likes"] + metrics["comments"] + metrics["shares"] + metrics["bookmarks"]
            metrics["engagement"] = total_engagement
            
            if metrics["views"] > 0:
                metrics["engagement_rate"] = round((total_engagement / metrics["views"]) * 100, 2)
            else:
                metrics["engagement_rate"] = 0.0
            
            # Extract account details - EXACT SAME method
            account_data = await self._extract_account_details(page, post_url)
            metrics.update(account_data)
            
            logger.info(f"Successfully scraped: {post_url} - Views: {metrics['views']:,}, Likes: {metrics['likes']:,}")

        except Exception as e:
            logger.error(f"Error extracting metrics for {post_url}: {e}")
            # Fallback to default values if extraction fails
            metrics.update({
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0,
                "engagement_rate": 0.0,
                "account_username": "Unknown",
                "account_followers": 0
            })
        
        return metrics
    
    async def _extract_views_comprehensive(self, page):
        """
        EXACT SAME comprehensive view extraction that worked
        """
        # Method 1: Extract from JSON data in page (most reliable) - THIS WORKED!
        try:
            page_content = await page.content()
            
            # Look for playCount in the JSON data - THIS FOUND 988, 1973, 307, 717, 404!
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"Found views in JSON data: {views}")
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
            '.view-count',
            '[class*="view"]',
            '[class*="View"]',
            'span:has-text("views")',
            'div:has-text("views")',
            'strong:has-text("views")'
        ]
        
        for selector in view_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text and self._looks_like_views(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"Found views with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        logger.warning("Could not extract views with any method")
        return 0
    
    def _looks_like_views(self, text):
        """
        EXACT SAME method that worked
        """
        text = str(text).lower().strip()
        return (
            'view' in text and 
            any(char.isdigit() for char in text) and
            len(text) < 20  # View counts are usually short
        )

    async def _extract_metric(self, page, selectors):
        """
        EXACT SAME method that worked
        """
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
        """
        EXACT SAME parsing method that worked
        """
        text = text.replace(',', '').strip()
        text = text.lower()

        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        elif 'b' in text:
            return int(float(text.replace('b', '')) * 1000000000)
        else:
            # Extract only digits, handle cases like "22 comments"
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

    async def _extract_account_details(self, page, post_url: str) -> dict:
        """
        EXACT SAME account extraction method that worked
        """
        try:
            logger.info(f"👤 Extracting account details from: {post_url}")
            
            # Extract username from URL or page
            username = await self._extract_username(page, post_url)
            
            # Extract followers - EXACT SAME method that found 8612, 5984, 3895, 7242, 2575
            followers = await self._extract_metric(page, [
                '[data-e2e="followers-count"] strong',
                'strong[data-e2e="followers-count"]',
                'div[data-e2e="followers-count"]',
                'span[data-e2e="followers-count"]'
            ])
            
            return {
                "account_username": username,
                "account_followers": followers
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting account details: {e}")
            return {
                "account_username": "Unknown",
                "account_followers": 0
            }

    async def _extract_username(self, page, post_url: str) -> str:
        """EXACT SAME username extraction method"""
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

    async def scrape_posts(self, posts_data: list) -> pd.DataFrame:
        """
        EXACT SAME scraping method that worked
        """
        results = []
        for i, post_data in enumerate(posts_data, 1):
            logger.info(f"📊 Scraping post {i}/{len(posts_data)}: {post_data['creator']} - Set #{post_data['set_id']}")
            
            result = await self._scrape_single_post(
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
    print("🎯 SCRAPING YOUR 3 SPECIFIC LINKS")
    print("=" * 60)
    
    # YOUR 3 SPECIFIC LINKS
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
    print("📊 Using EXACT SAME scraper that found:")
    print("   • 988, 1,973, 307, 717, 404 views")
    print("   • 40, 119, 37, 63, 22 likes")
    print("   • 8,612, 5,984, 3,895, 7,242, 2,575 followers")
    print()
    
    # Scrape all posts with EXACT SAME method
    async with Your3LinksScraper(headless=True, debug=True) as scraper:
        results_df = await scraper.scrape_posts(posts_data)
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"YOUR_3_LINKS_SCRAPED_DATA_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n🎯 YOUR 3 LINKS SCRAPING RESULTS:")
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
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(main())
