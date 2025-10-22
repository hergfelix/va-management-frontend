#!/usr/bin/env python3
"""
Real TikTok Scraper - Extract Actual Metrics
Uses Playwright to scrape real TikTok data and structure it like master_with_snaptik.csv
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

class RealTikTokScraper:
    """
    Real TikTok scraper using Playwright to extract actual metrics
    """
    
    def __init__(self, headless=True, debug=False):
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
        await self.playwright.stop()
    
    async def scrape_post(self, post_url, baseline_data=None):
        """
        Scrape a single TikTok post and extract real metrics
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
                account = baseline_data.get('account', 'unknown')
                with open(f'debug_page_{account}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"Debug: Saved page content to debug_page_{account}.html")
            
            # Extract metrics
            metrics = await self._extract_metrics(page, post_url, baseline_data)
            
            await page.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to scrape {post_url}: {str(e)}")
            return {
                "post_url": post_url,
                "error": str(e),
                "scraped_at": datetime.now().isoformat()
            }
    
    async def _extract_metrics(self, page, post_url, baseline_data=None):
        """
        Extract real metrics from TikTok page
        """
        metrics = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat()
        }
        
        try:
            # Extract views - try multiple selectors and methods
            views = await self._extract_views_comprehensive(page)
            metrics["views"] = views
            
            # Extract likes
            likes = await self._extract_metric(page, [
                '[data-e2e="like-count"]',
                '[data-e2e="browse-like-count"]',
                'strong[data-e2e="like-count"]',
                '.like-count',
                'span:has-text("likes")'
            ])
            metrics["likes"] = likes
            
            # Extract comments
            comments = await self._extract_metric(page, [
                '[data-e2e="comment-count"]',
                '[data-e2e="browse-comment-count"]',
                'strong[data-e2e="comment-count"]',
                '.comment-count',
                'span:has-text("comments")'
            ])
            metrics["comments"] = comments
            
            # Extract shares
            shares = await self._extract_metric(page, [
                '[data-e2e="share-count"]',
                '[data-e2e="browse-share-count"]',
                'strong[data-e2e="share-count"]',
                '.share-count',
                'span:has-text("shares")'
            ])
            metrics["shares"] = shares
            
            # Extract bookmarks (if available)
            bookmarks = await self._extract_metric(page, [
                '[data-e2e="bookmark-count"]',
                '[data-e2e="browse-bookmark-count"]',
                'strong[data-e2e="bookmark-count"]',
                '.bookmark-count'
            ])
            metrics["bookmarks"] = bookmarks
            
            # Calculate engagement
            total_engagement = likes + comments + shares + bookmarks
            engagement_rate = (total_engagement / views * 100) if views > 0 else 0
            metrics["engagement"] = total_engagement
            metrics["engagement_rate"] = round(engagement_rate, 2)
            
            # Extract additional data if baseline provided
            if baseline_data:
                metrics.update({
                    "va_url": baseline_data.get("va_url", ""),
                    "created_date": baseline_data.get("created_date", ""),
                    "creator": baseline_data.get("creator", ""),
                    "set_id": baseline_data.get("set_id", ""),
                    "set_code": baseline_data.get("set_code", ""),
                    "va": baseline_data.get("va", ""),
                    "post_type": baseline_data.get("post_type", ""),
                    "platform": baseline_data.get("platform", "tiktok"),
                    "account": baseline_data.get("account", ""),
                    "logged_at": datetime.now().isoformat(),
                    "first_scraped_at": baseline_data.get("first_scraped_at", datetime.now().isoformat()),
                    "followers": baseline_data.get("followers", 0),
                    "last_scraped_at": datetime.now().isoformat(),
                    "hashtags": baseline_data.get("hashtags", ""),
                    "sound": baseline_data.get("sound", ""),
                    "sound_url": baseline_data.get("sound_url", ""),
                    "slide_count": baseline_data.get("slide_count", 0),
                    "day1_views": baseline_data.get("day1_views", ""),
                    "day2_views": baseline_data.get("day2_views", ""),
                    "day3_views": baseline_data.get("day3_views", ""),
                    "day4_views": baseline_data.get("day4_views", ""),
                    "day5_views": baseline_data.get("day5_views", ""),
                    "scrape_status": "active",
                    "scrape_interval": "daily",
                    "scrape_count": (baseline_data.get("scrape_count", 0) or 0) + 1,
                    "days_since_posted": baseline_data.get("days_since_posted", 0),
                    "ocr_text": baseline_data.get("ocr_text", ""),
                    "slide_1": baseline_data.get("slide_1", ""),
                    "slide_2": baseline_data.get("slide_2", ""),
                    "slide_3": baseline_data.get("slide_3", ""),
                    "slide_4": baseline_data.get("slide_4", ""),
                    "slide_5": baseline_data.get("slide_5", ""),
                    "slide_6": baseline_data.get("slide_6", ""),
                    "slide_7": baseline_data.get("slide_7", ""),
                    "slide_8": baseline_data.get("slide_8", ""),
                    "slide_9": baseline_data.get("slide_9", ""),
                    "slide_10": baseline_data.get("slide_10", ""),
                    "slide_11": baseline_data.get("slide_11", ""),
                    "slide_12": baseline_data.get("slide_12", "")
                })
            
            logger.info(f"Successfully scraped: {post_url} - Views: {views:,}, Likes: {likes:,}")
            
        except Exception as e:
            logger.error(f"Error extracting metrics: {str(e)}")
            # Set default values
            metrics.update({
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "bookmarks": 0,
                "engagement": 0,
                "engagement_rate": 0.0
            })
        
        return metrics
    
    async def _extract_views_comprehensive(self, page):
        """
        Comprehensive view extraction with multiple methods
        """
        # Method 1: Extract from JSON data in page (most reliable)
        try:
            page_content = await page.content()
            import re
            
            # Look for playCount in the JSON data
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
            'strong:has-text("views")',
            # Try to find any element with numbers that might be views
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
                            logger.info(f"Found views with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 3: Look for any element containing numbers and "views"
        try:
            all_elements = await page.query_selector_all('span, div, strong, p, h1, h2, h3')
            for element in all_elements:
                text = await element.text_content()
                if text and ('views' in text.lower() or 'view' in text.lower()):
                    parsed = self._parse_metric(text)
                    if parsed > 0:
                        logger.info(f"Found views in text: {text} -> {parsed}")
                        return parsed
        except Exception:
            pass
        
        # Method 4: Look for large numbers that could be views
        try:
            all_elements = await page.query_selector_all('span, div, strong')
            for element in all_elements:
                text = await element.text_content()
                if text and self._looks_like_large_number(text):
                    parsed = self._parse_metric(text)
                    if parsed > 100:  # Views should be at least 100
                        logger.info(f"Found potential views (large number): {text} -> {parsed}")
                        return parsed
        except Exception:
            pass
        
        # Method 5: Try to find the main video stats area
        try:
            # Look for common video stats containers
            stats_containers = [
                '[class*="video-stats"]',
                '[class*="stats"]',
                '[class*="metrics"]',
                '[class*="count"]',
                '[data-e2e*="video"]'
            ]
            
            for container_selector in stats_containers:
                containers = await page.query_selector_all(container_selector)
                for container in containers:
                    # Look for numbers in this container
                    numbers = await container.query_selector_all('span, div, strong')
                    for number_elem in numbers:
                        text = await number_elem.text_content()
                        if text and self._looks_like_views(text):
                            parsed = self._parse_metric(text)
                            if parsed > 0:
                                logger.info(f"Found views in container: {text} -> {parsed}")
                                return parsed
        except Exception:
            pass
        
        logger.warning("Could not extract views with any method")
        return 0
    
    def _looks_like_views(self, text):
        """
        Check if text looks like view count
        """
        text = str(text).lower().strip()
        return (
            'view' in text and 
            any(char.isdigit() for char in text) and
            len(text) < 20  # View counts are usually short
        )
    
    def _looks_like_large_number(self, text):
        """
        Check if text looks like a large number (could be views)
        """
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
        """
        Try multiple selectors to extract a metric
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
        
        # If no selector works, try to find any element with numbers
        try:
            # Look for any element containing numbers that might be metrics
            elements = await page.query_selector_all('span, div, strong')
            for element in elements:
                text = await element.text_content()
                if text and self._looks_like_metric(text):
                    return self._parse_metric(text)
        except Exception:
            pass
        
        return 0
    
    def _parse_metric(self, text):
        """
        Parse TikTok metric format (e.g., '10.5K' -> 10500)
        """
        if not text:
            return 0
        
        # Clean the text
        text = str(text).strip().upper()
        
        # Remove any non-numeric characters except K, M, B
        text = re.sub(r'[^\d.KMB]', '', text)
        
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        elif 'B' in text:
            return int(float(text.replace('B', '')) * 1000000000)
        else:
            try:
                return int(text)
            except ValueError:
                return 0
    
    def _looks_like_metric(self, text):
        """
        Check if text looks like a metric (contains numbers and common metric words)
        """
        text = str(text).lower()
        metric_words = ['views', 'likes', 'comments', 'shares', 'bookmarks']
        has_number = any(char.isdigit() for char in text)
        has_metric_word = any(word in text for word in metric_words)
        return has_number and (has_metric_word or len(text) < 10)  # Short text with numbers

async def scrape_real_tiktok_posts():
    """
    Scrape real TikTok posts from master_with_snaptik.csv
    """
    # Load the CSV
    df = pd.read_csv('/Users/felixhergenroeder/Desktop/master_with_snaptik.csv')
    
    print("🎯 REAL TIKTOK SCRAPING")
    print("=" * 50)
    print(f"Found {len(df)} posts in master_with_snaptik.csv")
    print("Starting real scraping with Playwright...")
    print()
    
    # Take first 5 posts for testing
    test_posts = df.head(5)
    
    results = []
    
    async with RealTikTokScraper(headless=True, debug=True) as scraper:
        for i, (_, post) in enumerate(test_posts.iterrows(), 1):
            print(f"📊 Scraping post {i}/5: {post['account']}")
            
            # Convert row to dict for baseline data
            baseline_data = post.to_dict()
            
            # Scrape the post
            result = await scraper.scrape_post(post['post_url'], baseline_data)
            results.append(result)
            
            # Add delay between requests
            if i < len(test_posts):
                await asyncio.sleep(2)
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Save to CSV
    output_file = 'real_tiktok_scraping_results.csv'
    results_df.to_csv(output_file, index=False)
    
    print(f"\n✅ SCRAPING COMPLETE!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Successfully scraped: {len([r for r in results if 'error' not in r])}/{len(results)} posts")
    
    # Show results
    print(f"\n📈 RESULTS SUMMARY:")
    print("-" * 60)
    for i, result in enumerate(results, 1):
        if 'error' not in result:
            print(f"{i}. {result.get('account', 'Unknown')}: {result.get('views', 0):,} views, {result.get('likes', 0):,} likes")
        else:
            print(f"{i}. ERROR: {result.get('error', 'Unknown error')}")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(scrape_real_tiktok_posts())
