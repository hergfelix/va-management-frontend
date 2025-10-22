"""
Ultimate Scraper for 100 Videos
SuperClaude Ultimate TikTok Scraper

Uses longer wait times and better methods to extract data from ALL 100 URLs
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

class UltimateScraper:
    """
    Ultimate scraper with longer wait times and better methods
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
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-extensions'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_post_ultimate(self, post_url, baseline_data=None):
        """
        Ultimate scraping with longer wait times and better methods
        """
        try:
            # Create new page
            page = await self.browser.new_page()
            
            # Set realistic user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info(f"🚀 Ultimate scraping: {post_url}")
            
            # Navigate to post with longer timeout
            await page.goto(post_url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for initial load
            await page.wait_for_timeout(5000)
            
            # Wait for network to be idle
            try:
                await page.wait_for_load_state('networkidle', timeout=30000)
            except:
                logger.warning("Network idle timeout, continuing...")
            
            # Wait for JavaScript to load
            await page.wait_for_timeout(10000)
            
            # Try to wait for specific elements
            try:
                await page.wait_for_selector('body', timeout=10000)
            except:
                logger.warning("Body selector timeout, continuing...")
            
            # Debug: Save page content for analysis
            if self.debug:
                page_content = await page.content()
                url_id = post_url.split('/')[-2] if '/' in post_url else 'unknown'
                with open(f'ultimate_debug_{url_id}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"🚀 Ultimate debug: Saved page content to ultimate_debug_{url_id}.html")
            
            # Extract metrics with ultimate methods
            metrics = await self._extract_metrics_ultimate(page, post_url, baseline_data)
            
            await page.close()
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Ultimate scraping failed {post_url}: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0, "engagement_rate": 0.0,
                "account_username": "Unknown", "account_followers": 0,
                "error": str(e)
            }

    async def _extract_metrics_ultimate(self, page, post_url, baseline_data=None):
        """
        Ultimate metrics extraction with multiple methods and longer waits
        """
        metrics = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat()
        }
        
        try:
            # Wait for page to fully load
            await page.wait_for_timeout(5000)
            
            # Extract views with ultimate methods
            views = await self._extract_views_ultimate(page)
            metrics["views"] = views
            
            # Extract likes with ultimate methods
            likes = await self._extract_likes_ultimate(page)
            metrics["likes"] = likes

            # Extract comments with ultimate methods
            comments = await self._extract_comments_ultimate(page)
            metrics["comments"] = comments

            # Extract shares with ultimate methods
            shares = await self._extract_shares_ultimate(page)
            metrics["shares"] = shares

            # Extract bookmarks with ultimate methods
            bookmarks = await self._extract_bookmarks_ultimate(page)
            metrics["bookmarks"] = bookmarks

            # Calculate engagement
            total_engagement = metrics["likes"] + metrics["comments"] + metrics["shares"] + metrics["bookmarks"]
            metrics["engagement"] = total_engagement
            
            if metrics["views"] > 0:
                metrics["engagement_rate"] = round((total_engagement / metrics["views"]) * 100, 2)
            else:
                metrics["engagement_rate"] = 0.0
            
            # Extract account details with ultimate methods
            account_data = await self._extract_account_details_ultimate(page, post_url)
            metrics.update(account_data)
            
            logger.info(f"🚀 Ultimate success: {post_url} - Views: {metrics['views']:,}, Likes: {metrics['likes']:,}, Comments: {metrics['comments']:,}")

        except Exception as e:
            logger.error(f"❌ Error extracting ultimate metrics for {post_url}: {e}")
            # Fallback to default values if extraction fails
            metrics.update({
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0,
                "engagement_rate": 0.0,
                "account_username": "Unknown",
                "account_followers": 0
            })
        
        return metrics
    
    async def _extract_views_ultimate(self, page):
        """
        Ultimate view extraction with multiple methods and longer waits
        """
        # Method 1: Wait for page to load and extract from JSON data
        try:
            await page.wait_for_timeout(3000)
            page_content = await page.content()
            
            # Look for playCount in the JSON data
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"🚀 Ultimate: Found views in JSON data: {views}")
                return views
        except Exception as e:
            logger.debug(f"🚀 Ultimate JSON extraction failed: {e}")
        
        # Method 2: Try to wait for specific elements and extract
        try:
            # Wait for video elements to load
            await page.wait_for_timeout(5000)
            
            # Try multiple selectors with waits
            view_selectors = [
                '[data-e2e="video-views"]',
                '[data-e2e="video-view-count"]',
                '[data-e2e="browse-video-view-count"]',
                'strong[data-e2e="video-views"]',
                'span[data-e2e="video-views"]',
                '.video-count',
                '.view-count',
                '[class*="view"] strong',
                '[class*="View"] strong',
                'span:has-text("views")',
                'div:has-text("views")',
                'strong:has-text("views")',
                '[class*="count"] strong',
                '[class*="Count"] strong'
            ]
            
            for selector in view_selectors:
                try:
                    # Wait for element to appear
                    await page.wait_for_selector(selector, timeout=5000)
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text:
                            parsed = self._parse_metric(text)
                            if parsed > 0:
                                logger.info(f"🚀 Ultimate: Found views with selector '{selector}': {text} -> {parsed}")
                                return parsed
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"🚀 Ultimate selector extraction failed: {e}")
        
        # Method 3: Look for any element containing numbers and "views"
        try:
            await page.wait_for_timeout(3000)
            all_elements = await page.query_selector_all('span, div, strong, p, h1, h2, h3')
            for element in all_elements:
                text = await element.text_content()
                if text and ('views' in text.lower() or 'view' in text.lower()):
                    parsed = self._parse_metric(text)
                    if parsed > 0:
                        logger.info(f"🚀 Ultimate: Found views in text: {text} -> {parsed}")
                        return parsed
        except Exception as e:
            logger.debug(f"🚀 Ultimate text extraction failed: {e}")
        
        # Method 4: Look for large numbers that could be views
        try:
            await page.wait_for_timeout(3000)
            all_elements = await page.query_selector_all('span, div, strong')
            for element in all_elements:
                text = await element.text_content()
                if text and self._looks_like_large_number(text):
                    parsed = self._parse_metric(text)
                    if parsed > 100:  # Views should be at least 100
                        logger.info(f"🚀 Ultimate: Found potential views (large number): {text} -> {parsed}")
                        return parsed
        except Exception as e:
            logger.debug(f"🚀 Ultimate large number extraction failed: {e}")
        
        logger.warning("🚀 Ultimate: Could not extract views with any method")
        return 0
    
    async def _extract_likes_ultimate(self, page):
        """Ultimate likes extraction"""
        try:
            await page.wait_for_timeout(3000)
            page_content = await page.content()
            
            # JSON patterns
            like_patterns = [
                r'"diggCount":(\d+)',
                r'"likeCount":(\d+)',
                r'"likes":(\d+)',
                r'"heartCount":(\d+)'
            ]
            
            for pattern in like_patterns:
                match = re.search(pattern, page_content)
                if match:
                    likes = int(match.group(1))
                    logger.info(f"🚀 Ultimate: Found likes in JSON pattern '{pattern}': {likes}")
                    return likes
        except Exception:
            pass
        
        # Selectors
        like_selectors = [
            '[data-e2e="like-count"]',
            'strong[data-e2e="like-count"]',
            'div[data-e2e="like-count"]',
            'span[data-e2e="like-count"]',
            '[class*="like"] strong',
            '[class*="Like"] strong',
            '[class*="heart"] strong',
            '[class*="Heart"] strong'
        ]
        
        for selector in like_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"🚀 Ultimate: Found likes with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_comments_ultimate(self, page):
        """Ultimate comments extraction"""
        try:
            await page.wait_for_timeout(3000)
            page_content = await page.content()
            
            # JSON patterns
            comment_patterns = [
                r'"commentCount":(\d+)',
                r'"comments":(\d+)',
                r'"replyCount":(\d+)'
            ]
            
            for pattern in comment_patterns:
                match = re.search(pattern, page_content)
                if match:
                    comments = int(match.group(1))
                    logger.info(f"🚀 Ultimate: Found comments in JSON pattern '{pattern}': {comments}")
                    return comments
        except Exception:
            pass
        
        # Selectors
        comment_selectors = [
            '[data-e2e="comment-count"]',
            'strong[data-e2e="comment-count"]',
            'div[data-e2e="comment-count"]',
            'span[data-e2e="comment-count"]',
            '[class*="comment"] strong',
            '[class*="Comment"] strong'
        ]
        
        for selector in comment_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"🚀 Ultimate: Found comments with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_shares_ultimate(self, page):
        """Ultimate shares extraction"""
        try:
            await page.wait_for_timeout(3000)
            page_content = await page.content()
            
            # JSON patterns
            share_patterns = [
                r'"shareCount":(\d+)',
                r'"shares":(\d+)',
                r'"forwardCount":(\d+)'
            ]
            
            for pattern in share_patterns:
                match = re.search(pattern, page_content)
                if match:
                    shares = int(match.group(1))
                    logger.info(f"🚀 Ultimate: Found shares in JSON pattern '{pattern}': {shares}")
                    return shares
        except Exception:
            pass
        
        # Selectors
        share_selectors = [
            '[data-e2e="share-count"]',
            'strong[data-e2e="share-count"]',
            'div[data-e2e="share-count"]',
            'span[data-e2e="share-count"]',
            '[class*="share"] strong',
            '[class*="Share"] strong'
        ]
        
        for selector in share_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"🚀 Ultimate: Found shares with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_bookmarks_ultimate(self, page):
        """Ultimate bookmarks extraction"""
        try:
            await page.wait_for_timeout(3000)
            page_content = await page.content()
            
            # JSON patterns
            bookmark_patterns = [
                r'"collectCount":(\d+)',
                r'"bookmarkCount":(\d+)',
                r'"saves":(\d+)'
            ]
            
            for pattern in bookmark_patterns:
                match = re.search(pattern, page_content)
                if match:
                    bookmarks = int(match.group(1))
                    logger.info(f"🚀 Ultimate: Found bookmarks in JSON pattern '{pattern}': {bookmarks}")
                    return bookmarks
        except Exception:
            pass
        
        # Selectors
        bookmark_selectors = [
            '[data-e2e="collect-count"]',
            'strong[data-e2e="collect-count"]',
            'div[data-e2e="collect-count"]',
            'span[data-e2e="collect-count"]',
            '[class*="collect"] strong',
            '[class*="Collect"] strong',
            '[class*="bookmark"] strong',
            '[class*="Bookmark"] strong'
        ]
        
        for selector in bookmark_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"🚀 Ultimate: Found bookmarks with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_account_details_ultimate(self, page, post_url: str) -> dict:
        """Ultimate account details extraction"""
        try:
            logger.info(f"🚀 Ultimate: Extracting account details from: {post_url}")
            
            # Extract username
            username = await self._extract_username_ultimate(page, post_url)
            
            # Extract followers
            followers = await self._extract_followers_ultimate(page)
            
            return {
                "account_username": username,
                "account_followers": followers
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting ultimate account details: {e}")
            return {
                "account_username": "Unknown",
                "account_followers": 0
            }
    
    async def _extract_username_ultimate(self, page, post_url: str) -> str:
        """Ultimate username extraction"""
        try:
            # From URL
            url_match = re.search(r'@([^/]+)', post_url)
            if url_match:
                return url_match.group(1)
            
            # From page
            await page.wait_for_timeout(3000)
            username_selectors = [
                '[data-e2e="user-title"]',
                '[class*="username"]',
                '[class*="Username"]',
                '[class*="user-name"]',
                '[class*="User-name"]'
            ]
            
            for selector in username_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text:
                            return text.replace('@', '').strip()
                except Exception:
                    continue
            
            return "Unknown"
            
        except Exception:
            return "Unknown"
    
    async def _extract_followers_ultimate(self, page):
        """Ultimate followers extraction"""
        try:
            await page.wait_for_timeout(3000)
            page_content = await page.content()
            
            # JSON patterns
            follower_patterns = [
                r'"followerCount":(\d+)',
                r'"followers":(\d+)',
                r'"fans":(\d+)'
            ]
            
            for pattern in follower_patterns:
                match = re.search(pattern, page_content)
                if match:
                    followers = int(match.group(1))
                    logger.info(f"🚀 Ultimate: Found followers in JSON pattern '{pattern}': {followers}")
                    return followers
        except Exception:
            pass
        
        # Selectors
        follower_selectors = [
            '[data-e2e="followers-count"] strong',
            'strong[data-e2e="followers-count"]',
            'div[data-e2e="followers-count"]',
            'span[data-e2e="followers-count"]',
            '[class*="follower"] strong',
            '[class*="Follower"] strong',
            '[class*="follow"] strong',
            '[class*="Follow"] strong'
        ]
        
        for selector in follower_selectors:
            try:
                await page.wait_for_selector(selector, timeout=3000)
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"🚀 Ultimate: Found followers with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    def _looks_like_large_number(self, text):
        """Check if text looks like a large number (could be views)"""
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
            # Extract only digits, handle cases like "22 comments"
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

    async def scrape_posts_ultimate(self, urls: list) -> pd.DataFrame:
        """
        Ultimate scraping of multiple posts with better error handling
        """
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"🚀 Ultimate scraping post {i}/{len(urls)}: {url}")
            
            result = await self.scrape_post_ultimate(url)
            results.append(result)
            
            # Add delay between posts
            if i < len(urls):
                await asyncio.sleep(3)
        
        return pd.DataFrame(results)

async def main():
    """Main execution"""
    print("🚀 ULTIMATE SCRAPER - 100 VIDEOS")
    print("=" * 60)
    print("🎯 Using ultimate methods with longer wait times!")
    print()
    
    # Your 100 URLs
    urls = [
        "https://www.tiktok.com/t/ZTMuUscW9/",
        "https://www.tiktok.com/t/ZTMuUEG3c/",
        "https://www.tiktok.com/t/ZTMuyRh5a/",
        "https://www.tiktok.com/t/ZP8A7kX4w/",
        "https://www.tiktok.com/t/ZP8A7L74E/",
        "https://www.tiktok.com/t/ZP8AWKSmF/",
        "https://www.tiktok.com/t/ZP8AWE7sA/",
        "https://www.tiktok.com/t/ZP8A7eWtL/",
        "https://www.tiktok.com/t/ZTMumCAUk/",
        "https://www.tiktok.com/t/ZTMuuY6RG/",
        "https://www.tiktok.com/t/ZTMuuuUWY/",
        "https://www.tiktok.com/t/ZTMuuvqtk/",
        "https://www.tiktok.com/t/ZTMuHX9Bv/",
        "https://www.tiktok.com/t/ZP8AWKcBJ/",
        "https://www.tiktok.com/t/ZP8A7ymPT/",
        "https://www.tiktok.com/t/ZP8A7Sj5N/",
        "https://www.tiktok.com/t/ZP8A7egj8/",
        "https://www.tiktok.com/t/ZP8A74CCt/",
        "https://www.tiktok.com/t/ZP8A7t8Ch/",
        "https://www.tiktok.com/t/ZP8A7bXhw/",
        "https://www.tiktok.com/t/ZP8A7fLcC/",
        "https://www.tiktok.com/t/ZP8A7bj6f/",
        "https://www.tiktok.com/t/ZP8A7Ctk7/",
        "https://www.tiktok.com/t/ZTMuQ5W1q/",
        "https://www.tiktok.com/t/ZTMuXq7EW/",
        "https://www.tiktok.com/t/ZP8A7xhj5/",
        "https://www.tiktok.com/t/ZTMuX3oSU/",
        "https://www.tiktok.com/t/ZTMu4JN1Y/",
        "https://www.tiktok.com/t/ZTMu42n2V/",
        "https://www.tiktok.com/t/ZTMu4aCUa/",
        "https://www.tiktok.com/t/ZTMu4D8Kw/",
        "https://www.tiktok.com/t/ZP8A77Lec/",
        "https://www.tiktok.com/t/ZP8A74dd6/",
        "https://www.tiktok.com/t/ZP8A7gYvo/",
        "https://www.tiktok.com/t/ZP8A7pfce/",
        "https://www.tiktok.com/t/ZTMuV2Wxk/",
        "https://www.tiktok.com/t/ZP8A7xTtY/",
        "https://www.tiktok.com/t/ZP8A7ay5o/",
        "https://www.tiktok.com/t/ZTMuVm5Jm/",
        "https://www.tiktok.com/t/ZP8A7gUkm/",
        "https://www.tiktok.com/t/ZTMuV2gC9/",
        "https://www.tiktok.com/t/ZP8A7qJ7f/",
        "https://www.tiktok.com/t/ZTMuVqtCG/",
        "https://vt.tiktok.com/ZSUGHkc9j/",
        "https://www.tiktok.com/t/ZP8A7VCuu/",
        "https://www.tiktok.com/t/ZP8A7XmFu/",
        "https://www.tiktok.com/t/ZTMuV9UxR/",
        "https://www.tiktok.com/t/ZTMuVn2Ex/",
        "https://www.tiktok.com/t/ZTMuVXXyb/",
        "https://www.tiktok.com/t/ZTMuV9b55/",
        "https://www.tiktok.com/t/ZTMuVKabr/",
        "https://www.tiktok.com/t/ZTMuVWAYj/",
        "https://www.tiktok.com/t/ZP8A754BD/",
        "https://www.tiktok.com/t/ZTMuVTj13/",
        "https://vt.tiktok.com/ZSUGHmYun/",
        "https://www.tiktok.com/t/ZTMuqMdfm/",
        "https://www.tiktok.com/t/ZP8A7QdkT/",
        "https://www.tiktok.com/t/ZTMuqApVw/",
        "https://www.tiktok.com/t/ZTMuqkTK9/",
        "https://www.tiktok.com/t/ZTMuq8QpU/",
        "https://www.tiktok.com/t/ZP8A7fmgp/",
        "https://www.tiktok.com/t/ZP8A7CT3q/",
        "https://www.tiktok.com/t/ZTMuqJ6Hx/",
        "https://www.tiktok.com/t/ZTMuqSj7G/",
        "https://www.tiktok.com/t/ZTMuqjS1e/",
        "https://www.tiktok.com/t/ZTMuqY5Xj/",
        "https://www.tiktok.com/t/ZP8A7PJ72/",
        "https://www.tiktok.com/t/ZTMuqNbXK/",
        "https://www.tiktok.com/t/ZTMuqn9hg/",
        "https://www.tiktok.com/t/ZTMuqHBws/",
        "https://www.tiktok.com/t/ZP8A7xxS8/",
        "https://www.tiktok.com/t/ZTMuqWNwt/",
        "https://www.tiktok.com/t/ZTMuqaukV/",
        "https://www.tiktok.com/t/ZP8A778mN/",
        "https://www.tiktok.com/t/ZP8A7b11C/",
        "https://www.tiktok.com/t/ZTMuq9Xjj/",
        "https://www.tiktok.com/t/ZTMuqxDdV/",
        "https://www.tiktok.com/t/ZP8A7XrN7/",
        "https://www.tiktok.com/t/ZTMuqQjqE/",
        "https://www.tiktok.com/t/ZP8A7VwsM/",
        "https://www.tiktok.com/t/ZTMuqbRjn/",
        "https://www.tiktok.com/t/ZP8A7Ccwv/",
        "https://www.tiktok.com/t/ZTMuqxjnC/",
        "https://www.tiktok.com/t/ZTMuq7CnX/",
        "https://www.tiktok.com/t/ZTMuqQjqE/",
        "https://www.tiktok.com/t/ZP8A7mVAH/",
        "https://www.tiktok.com/t/ZTMub6bbM/",
        "https://www.tiktok.com/t/ZP8A7xEHa/",
        "https://www.tiktok.com/t/ZTMuqKXmB/",
        "https://www.tiktok.com/t/ZTMubRucf/",
        "https://www.tiktok.com/t/ZTMubjtfY/",
        "https://www.tiktok.com/t/ZTMubdJPp/",
        "https://www.tiktok.com/t/ZTMuqEX44/",
        "https://www.tiktok.com/t/ZP8A7uELk/",
        "https://www.tiktok.com/t/ZTMuqwRmw/",
        "https://www.tiktok.com/t/ZP8A7qrSk/",
        "https://www.tiktok.com/t/ZP8A7vY59/",
        "https://www.tiktok.com/t/ZTMubAWvv/",
        "https://www.tiktok.com/t/ZTMubggAH/",
        "https://www.tiktok.com/t/ZP8A7mJAD/"
    ]
    
    print(f"🚀 Ultimate scraping: {len(urls)} URLs")
    print("📊 Ultimate optimizations:")
    print("   • Longer wait times (10+ seconds)")
    print("   • Multiple extraction methods")
    print("   • Better error handling")
    print("   • Network idle waiting")
    print("   • Element waiting")
    print()
    
    # Test with first 5 URLs first
    test_urls = urls[:5]
    print(f"🎯 Testing with first 5 URLs first...")
    
    # Scrape with ultimate method
    async with UltimateScraper(headless=True, debug=True) as scraper:
        results_df = await scraper.scrape_posts_ultimate(test_urls)
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ULTIMATE_5_VIDEOS_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n🚀 ULTIMATE SCRAPING RESULTS:")
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
        print("\n✅ SUCCESS! Ready for all 100 videos!")
    elif partial_data >= 3:
        print("\n⚠️ PARTIAL SUCCESS! Some data extracted, ready for all 100 videos!")
    else:
        print("\n❌ FAILED! Need to investigate further!")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(main())
