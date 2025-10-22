"""
Working Real Scraper for 5 Videos
SuperClaude Working Real TikTok Scraper

Uses the EXACT SAME method that extracted real views 4 hours ago
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

class WorkingRealScraper:
    """
    Working real scraper using the EXACT SAME method that worked 4 hours ago
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

    async def scrape_post(self, post_url, baseline_data=None):
        """
        Scrape a single TikTok post using the EXACT SAME method that worked
        """
        try:
            # Create new page
            page = await self.browser.new_page()
            
            # Set realistic user agent (EXACT SAME as working method)
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Set viewport (EXACT SAME as working method)
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info(f"🎯 Working real scraping: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Debug: Save page content for analysis
            if self.debug:
                page_content = await page.content()
                url_id = post_url.split('/')[-2] if '/' in post_url else 'unknown'
                with open(f'working_real_debug_{url_id}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"🎯 Working real debug: Saved page content to working_real_debug_{url_id}.html")
            
            # Extract metrics using EXACT SAME method
            metrics = await self._extract_metrics(page, post_url, baseline_data)
            
            await page.close()
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Working real scraping failed {post_url}: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0, "engagement_rate": 0.0,
                "account_username": "Unknown", "account_followers": 0,
                "error": str(e)
            }

    async def _extract_metrics(self, page, post_url, baseline_data=None):
        """
        Extract metrics using the EXACT SAME method that worked 4 hours ago
        """
        metrics = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat()
        }
        
        try:
            # Extract views - EXACT SAME method that worked
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

            # Calculate engagement
            total_engagement = metrics["likes"] + metrics["comments"] + metrics["shares"] + metrics["bookmarks"]
            metrics["engagement"] = total_engagement
            
            if metrics["views"] > 0:
                metrics["engagement_rate"] = round((total_engagement / metrics["views"]) * 100, 2)
            else:
                metrics["engagement_rate"] = 0.0
            
            # Extract account details - EXACT SAME method
            account_data = await self._extract_account_details(page, post_url)
            metrics.update(account_data)
            
            logger.info(f"🎯 Working real success: {post_url} - Views: {metrics['views']:,}, Likes: {metrics['likes']:,}, Comments: {metrics['comments']:,}")

        except Exception as e:
            logger.error(f"❌ Error extracting working real metrics for {post_url}: {e}")
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
        Extract views using the EXACT SAME comprehensive method that worked
        """
        # Method 1: Extract from JSON data in page (most reliable) - EXACT SAME
        try:
            page_content = await page.content()
            
            # Look for playCount in the JSON data - EXACT SAME
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"🎯 Working real: Found views in JSON data: {views}")
                return views
        except Exception as e:
            logger.debug(f"🎯 Working real JSON extraction failed: {e}")
        
        # Method 2: Try all possible view selectors - EXACT SAME
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
            'strong:has-text("views")',
            'span[class*="count"]',
            'div[class*="count"]',
            'strong[class*="count"]'
        ]
        
        for selector in view_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text and self._looks_like_views(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"🎯 Working real: Found views with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 3: Look for any element containing numbers and "views" - EXACT SAME
        try:
            all_elements = await page.query_selector_all('span, div, strong, p, h1, h2, h3')
            for element in all_elements:
                text = await element.text_content()
                if text and ('views' in text.lower() or 'view' in text.lower()):
                    parsed = self._parse_metric(text)
                    if parsed > 0:
                        logger.info(f"🎯 Working real: Found views in text: {text} -> {parsed}")
                        return parsed
        except Exception:
            pass
        
        # Method 4: Look for large numbers that could be views - EXACT SAME
        try:
            all_elements = await page.query_selector_all('span, div, strong')
            for element in all_elements:
                text = await element.text_content()
                if text and self._looks_like_large_number(text):
                    parsed = self._parse_metric(text)
                    if parsed > 100:  # Views should be at least 100
                        logger.info(f"🎯 Working real: Found potential views (large number): {text} -> {parsed}")
                        return parsed
        except Exception:
            pass
        
        logger.warning("🎯 Working real: Could not extract views with any method")
        return 0
    
    def _looks_like_views(self, text):
        """Check if text looks like view count - EXACT SAME"""
        text = str(text).lower().strip()
        return (
            'view' in text and 
            any(char.isdigit() for char in text) and
            len(text) < 20
        )
    
    def _looks_like_large_number(self, text):
        """Check if text looks like a large number (could be views) - EXACT SAME"""
        text = str(text).strip()
        
        # Skip obvious non-view text
        skip_patterns = [
            'copyright', '©', 'tiktok', 'privacy', 'terms', 'policy',
            'follow', 'subscribe', 'share', 'download', 'app',
            'login', 'sign', 'account', 'profile', 'settings'
        ]
        
        text_lower = text.lower()
        for pattern in skip_patterns:
            if pattern in text_lower:
                return False
        
        # Should contain only numbers, K, M, B, and common separators
        clean_text = re.sub(r'[^\d.KMB,]', '', text.upper())
        if not clean_text:
            return False
        
        # Should be a reasonable length for a number
        if len(clean_text) > 15:
            return False
        
        # Should contain at least one digit
        if not any(char.isdigit() for char in clean_text):
            return False
        
        # Try to parse it
        try:
            parsed = self._parse_metric(clean_text)
            # Views should be reasonable (not too high, not too low)
            return 100 <= parsed <= 10000000  # Between 100 and 10M views
        except:
            return False

    async def _extract_metric(self, page, selectors):
        """Try multiple selectors to extract a metric - EXACT SAME"""
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
        """Parse a metric string (e.g., "10.5K", "1.2M") into an integer - EXACT SAME"""
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
        Extract account details - EXACT SAME method
        """
        try:
            logger.info(f"🎯 Working real: Extracting account details from: {post_url}")
            
            # Extract username from URL or page
            username = await self._extract_username(page, post_url)
            
            # Extract followers
            followers = await self._extract_metric(page, [
                '[data-e2e="followers-count"] strong',
                'strong[data-e2e="followers-count"]',
                'div[data-e2e="followers-count"]',
                'span[data-e2e="followers-count"]',
                '[class*="follower"] strong',
                '[class*="Follower"] strong'
            ])
            
            return {
                "account_username": username,
                "account_followers": followers
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting working real account details: {e}")
            return {
                "account_username": "Unknown",
                "account_followers": 0
            }

    async def _extract_username(self, page, post_url: str) -> str:
        """Extract username - EXACT SAME method"""
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

    async def scrape_posts(self, urls: list) -> pd.DataFrame:
        """
        Scrape multiple posts using EXACT SAME method that worked
        """
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"🎯 Working real scraping post {i}/{len(urls)}: {url}")
            
            result = await self.scrape_post(url)
            results.append(result)
            
            # Add delay between posts
            if i < len(urls):
                await asyncio.sleep(2)
        
        return pd.DataFrame(results)

async def main():
    """Main execution"""
    print("🎯 WORKING REAL SCRAPER - 5 VIDEOS TEST")
    print("=" * 60)
    print("🚀 Using EXACT SAME method that extracted real views 4 hours ago!")
    print()
    
    # First 5 URLs from your list
    test_urls = [
        "https://www.tiktok.com/t/ZTMuUscW9/",
        "https://www.tiktok.com/t/ZTMuUEG3c/",
        "https://www.tiktok.com/t/ZTMuyRh5a/",
        "https://www.tiktok.com/t/ZP8A7kX4w/",
        "https://www.tiktok.com/t/ZP8A7L74E/"
    ]
    
    print(f"🎯 Working real scraping: {len(test_urls)} URLs")
    print("📊 Using EXACT SAME method that worked before:")
    print("   • Same user agent")
    print("   • Same viewport")
    print("   • Same selectors")
    print("   • Same JSON extraction")
    print("   • Same comprehensive methods")
    print()
    
    # Scrape all posts with EXACT SAME method
    async with WorkingRealScraper(headless=True, debug=True) as scraper:
        results_df = await scraper.scrape_posts(test_urls)
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"WORKING_REAL_5_VIDEOS_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n🎯 WORKING REAL SCRAPING RESULTS:")
    print("=" * 60)
    
    for i, row in results_df.iterrows():
        print(f"\n📹 POST {i+1}: {row['post_url']}")
        print(f"   Views: {row['views']:,}")
        print(f"   Likes: {row['likes']:,}")
        print(f"   Comments: {row['comments']:,}")
        print(f"   Shares: {row['shares']:,}")
        print(f"   Bookmarks: {row['bookmarks']:,}")
        print(f"   Engagement Rate: {row['engagement_rate']:.2f}%")
        print(f"   Account: @{row['account_username']}")
        print(f"   Followers: {row['account_followers']:,}")
    
    # Summary
    total_views = results_df['views'].sum()
    total_likes = results_df['likes'].sum()
    total_comments = results_df['comments'].sum()
    total_shares = results_df['shares'].sum()
    total_bookmarks = results_df['bookmarks'].sum()
    total_engagement = results_df['engagement'].sum()
    avg_engagement_rate = results_df['engagement_rate'].mean()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Views: {total_views:,}")
    print(f"   Total Likes: {total_likes:,}")
    print(f"   Total Comments: {total_comments:,}")
    print(f"   Total Shares: {total_shares:,}")
    print(f"   Total Bookmarks: {total_bookmarks:,}")
    print(f"   Total Engagement: {total_engagement:,}")
    print(f"   Average Engagement Rate: {avg_engagement_rate:.2f}%")
    
    # Data quality analysis
    complete_data = len(results_df[(results_df['views'] > 0) & (results_df['likes'] > 0) & (results_df['comments'] > 0)])
    partial_data = len(results_df[(results_df['views'] > 0) & ((results_df['likes'] == 0) | (results_df['comments'] == 0))])
    no_data = len(results_df[results_df['views'] == 0])
    
    print(f"\n📊 DATA QUALITY:")
    print(f"   Complete Data: {complete_data}/{len(results_df)} ({complete_data/len(results_df)*100:.1f}%)")
    print(f"   Partial Data: {partial_data}/{len(results_df)} ({partial_data/len(results_df)*100:.1f}%)")
    print(f"   No Data: {no_data}/{len(results_df)} ({no_data/len(results_df)*100:.1f}%)")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    if complete_data >= 3:
        print("\n✅ SUCCESS! Ready for 20 videos test!")
    elif partial_data >= 3:
        print("\n⚠️ PARTIAL SUCCESS! Some data extracted, ready for 20 videos test!")
    else:
        print("\n❌ FAILED! Need to investigate why the same method doesn't work!")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(main())
