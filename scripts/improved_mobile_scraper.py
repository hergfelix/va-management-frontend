"""
Improved Mobile Scraper for Your 3 Links
SuperClaude Improved Mobile TikTok Scraper

This improves the mobile scraper to extract likes, comments, and followers
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

class ImprovedMobileScraper:
    """
    Improved mobile-optimized TikTok scraper
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
        Improved mobile scraping with better metric extraction
        """
        try:
            # Create new page
            page = await self.browser.new_page()
            
            # Set MOBILE user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
            })
            
            # Set MOBILE viewport
            await page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
            
            logger.info(f"📱 Improved mobile scraping: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Debug: Save page content for analysis
            if self.debug:
                page_content = await page.content()
                account_name = creator.lower().replace(" ", "")
                with open(f'improved_mobile_debug_{account_name}_{set_id}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"📱 Improved mobile debug: Saved page content to improved_mobile_debug_{account_name}_{set_id}.html")
            
            # Extract metrics with improved methods
            metrics = await self._extract_metrics_improved(page, post_url, creator, set_id, va, post_type)
            
            await page.close()
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Improved mobile scraping failed {post_url}: {e}")
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

    async def _extract_metrics_improved(self, page, post_url, creator, set_id, va, post_type):
        """
        Improved metrics extraction with multiple methods
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
            # Extract views - we know this works
            views = await self._extract_views_improved(page)
            metrics["views"] = views
            
            # Extract likes with improved methods
            likes = await self._extract_likes_improved(page)
            metrics["likes"] = likes

            # Extract comments with improved methods
            comments = await self._extract_comments_improved(page)
            metrics["comments"] = comments

            # Extract shares with improved methods
            shares = await self._extract_shares_improved(page)
            metrics["shares"] = shares

            # Extract bookmarks with improved methods
            bookmarks = await self._extract_bookmarks_improved(page)
            metrics["bookmarks"] = bookmarks

            # Calculate engagement
            total_engagement = metrics["likes"] + metrics["comments"] + metrics["shares"] + metrics["bookmarks"]
            metrics["engagement"] = total_engagement
            
            if metrics["views"] > 0:
                metrics["engagement_rate"] = round((total_engagement / metrics["views"]) * 100, 2)
            else:
                metrics["engagement_rate"] = 0.0
            
            # Extract account details with improved methods
            account_data = await self._extract_account_details_improved(page, post_url)
            metrics.update(account_data)
            
            logger.info(f"📱 Improved mobile success: {post_url} - Views: {metrics['views']:,}, Likes: {metrics['likes']:,}, Comments: {metrics['comments']:,}")

        except Exception as e:
            logger.error(f"❌ Error extracting improved mobile metrics for {post_url}: {e}")
            # Fallback to default values if extraction fails
            metrics.update({
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0,
                "engagement_rate": 0.0,
                "account_username": "Unknown",
                "account_followers": 0
            })
        
        return metrics
    
    async def _extract_views_improved(self, page):
        """
        Improved view extraction (we know this works)
        """
        try:
            page_content = await page.content()
            
            # Look for playCount in the JSON data
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"📱 Improved: Found views in JSON data: {views}")
                return views
        except Exception as e:
            logger.debug(f"📱 Improved JSON extraction failed: {e}")
        
        return 0
    
    async def _extract_likes_improved(self, page):
        """
        Improved likes extraction with multiple methods
        """
        # Method 1: Try all possible like selectors
        like_selectors = [
            '[data-e2e="like-count"]',
            'strong[data-e2e="like-count"]',
            'div[data-e2e="like-count"]',
            'span[data-e2e="like-count"]',
            '[class*="like"] strong',
            '[class*="Like"] strong',
            '[class*="heart"] strong',
            '[class*="Heart"] strong',
            'button[data-e2e="like-button"] strong',
            'button[data-e2e="like-button"] span'
        ]
        
        for selector in like_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_metric(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 Improved: Found likes with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 2: Look for like patterns in page content
        try:
            page_content = await page.content()
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
                    logger.info(f"📱 Improved: Found likes in JSON pattern '{pattern}': {likes}")
                    return likes
        except Exception:
            pass
        
        # Method 3: Look for any element containing numbers and "like" or "heart"
        try:
            all_elements = await page.query_selector_all('span, div, strong, p')
            for element in all_elements:
                text = await element.text_content()
                if text and ('like' in text.lower() or 'heart' in text.lower()):
                    parsed = self._parse_metric(text)
                    if parsed > 0:
                        logger.info(f"📱 Improved: Found likes in text: {text} -> {parsed}")
                        return parsed
        except Exception:
            pass
        
        logger.warning("📱 Improved: Could not extract likes with any method")
        return 0
    
    async def _extract_comments_improved(self, page):
        """
        Improved comments extraction with multiple methods
        """
        # Method 1: Try all possible comment selectors
        comment_selectors = [
            '[data-e2e="comment-count"]',
            'strong[data-e2e="comment-count"]',
            'div[data-e2e="comment-count"]',
            'span[data-e2e="comment-count"]',
            '[class*="comment"] strong',
            '[class*="Comment"] strong',
            'button[data-e2e="comment-button"] strong',
            'button[data-e2e="comment-button"] span'
        ]
        
        for selector in comment_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_metric(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 Improved: Found comments with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 2: Look for comment patterns in page content
        try:
            page_content = await page.content()
            comment_patterns = [
                r'"commentCount":(\d+)',
                r'"comments":(\d+)',
                r'"replyCount":(\d+)'
            ]
            
            for pattern in comment_patterns:
                match = re.search(pattern, page_content)
                if match:
                    comments = int(match.group(1))
                    logger.info(f"📱 Improved: Found comments in JSON pattern '{pattern}': {comments}")
                    return comments
        except Exception:
            pass
        
        # Method 3: Look for any element containing numbers and "comment"
        try:
            all_elements = await page.query_selector_all('span, div, strong, p')
            for element in all_elements:
                text = await element.text_content()
                if text and 'comment' in text.lower():
                    parsed = self._parse_metric(text)
                    if parsed > 0:
                        logger.info(f"📱 Improved: Found comments in text: {text} -> {parsed}")
                        return parsed
        except Exception:
            pass
        
        logger.warning("📱 Improved: Could not extract comments with any method")
        return 0
    
    async def _extract_shares_improved(self, page):
        """
        Improved shares extraction with multiple methods
        """
        # Method 1: Try all possible share selectors
        share_selectors = [
            '[data-e2e="share-count"]',
            'strong[data-e2e="share-count"]',
            'div[data-e2e="share-count"]',
            'span[data-e2e="share-count"]',
            '[class*="share"] strong',
            '[class*="Share"] strong',
            'button[data-e2e="share-button"] strong',
            'button[data-e2e="share-button"] span'
        ]
        
        for selector in share_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_metric(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 Improved: Found shares with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 2: Look for share patterns in page content
        try:
            page_content = await page.content()
            share_patterns = [
                r'"shareCount":(\d+)',
                r'"shares":(\d+)',
                r'"forwardCount":(\d+)'
            ]
            
            for pattern in share_patterns:
                match = re.search(pattern, page_content)
                if match:
                    shares = int(match.group(1))
                    logger.info(f"📱 Improved: Found shares in JSON pattern '{pattern}': {shares}")
                    return shares
        except Exception:
            pass
        
        logger.warning("📱 Improved: Could not extract shares with any method")
        return 0
    
    async def _extract_bookmarks_improved(self, page):
        """
        Improved bookmarks extraction with multiple methods
        """
        # Method 1: Try all possible bookmark selectors
        bookmark_selectors = [
            '[data-e2e="collect-count"]',
            'strong[data-e2e="collect-count"]',
            'div[data-e2e="collect-count"]',
            'span[data-e2e="collect-count"]',
            '[class*="collect"] strong',
            '[class*="Collect"] strong',
            '[class*="bookmark"] strong',
            '[class*="Bookmark"] strong',
            'button[data-e2e="collect-button"] strong',
            'button[data-e2e="collect-button"] span'
        ]
        
        for selector in bookmark_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_metric(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 Improved: Found bookmarks with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 2: Look for bookmark patterns in page content
        try:
            page_content = await page.content()
            bookmark_patterns = [
                r'"collectCount":(\d+)',
                r'"bookmarkCount":(\d+)',
                r'"saves":(\d+)'
            ]
            
            for pattern in bookmark_patterns:
                match = re.search(pattern, page_content)
                if match:
                    bookmarks = int(match.group(1))
                    logger.info(f"📱 Improved: Found bookmarks in JSON pattern '{pattern}': {bookmarks}")
                    return bookmarks
        except Exception:
            pass
        
        logger.warning("📱 Improved: Could not extract bookmarks with any method")
        return 0
    
    async def _extract_account_details_improved(self, page, post_url: str) -> dict:
        """
        Improved account details extraction with multiple methods
        """
        try:
            logger.info(f"📱 Improved: Extracting account details from: {post_url}")
            
            # Extract username from URL or page
            username = await self._extract_username_improved(page, post_url)
            
            # Extract followers with improved methods
            followers = await self._extract_followers_improved(page)
            
            return {
                "account_username": username,
                "account_followers": followers
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting improved account details: {e}")
            return {
                "account_username": "Unknown",
                "account_followers": 0
            }
    
    async def _extract_username_improved(self, page, post_url: str) -> str:
        """Improved username extraction"""
        try:
            # Try to extract from URL
            url_match = re.search(r'@([^/]+)', post_url)
            if url_match:
                return url_match.group(1)
            
            # Try to extract from page - multiple selectors
            username_selectors = [
                '[data-e2e="user-title"]',
                '[class*="username"]',
                '[class*="Username"]',
                '[class*="user-name"]',
                '[class*="User-name"]'
            ]
            
            for selector in username_selectors:
                try:
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
    
    async def _extract_followers_improved(self, page):
        """
        Improved followers extraction with multiple methods
        """
        # Method 1: Try all possible follower selectors
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
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_metric(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 Improved: Found followers with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 2: Look for follower patterns in page content
        try:
            page_content = await page.content()
            follower_patterns = [
                r'"followerCount":(\d+)',
                r'"followers":(\d+)',
                r'"fans":(\d+)'
            ]
            
            for pattern in follower_patterns:
                match = re.search(pattern, page_content)
                if match:
                    followers = int(match.group(1))
                    logger.info(f"📱 Improved: Found followers in JSON pattern '{pattern}': {followers}")
                    return followers
        except Exception:
            pass
        
        logger.warning("📱 Improved: Could not extract followers with any method")
        return 0
    
    def _looks_like_metric(self, text):
        """Check if text looks like a metric"""
        text = str(text).strip()
        if not text:
            return False
        
        # Should contain at least one digit
        if not any(char.isdigit() for char in text):
            return False
        
        # Should be a reasonable length
        if len(text) > 20:
            return False
        
        # Try to parse it
        try:
            parsed = self._parse_metric(text)
            return parsed >= 0
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

    async def scrape_posts(self, posts_data: list) -> pd.DataFrame:
        """
        Improved mobile scraping of multiple posts
        """
        results = []
        for i, post_data in enumerate(posts_data, 1):
            logger.info(f"📱 Improved mobile scraping post {i}/{len(posts_data)}: {post_data['creator']} - Set #{post_data['set_id']}")
            
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
    print("📱 IMPROVED MOBILE SCRAPER FOR YOUR 3 LINKS")
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
    
    print(f"📱 Improved mobile scraping: {len(posts_data)} posts")
    print("📊 Improvements:")
    print("   • Multiple extraction methods for each metric")
    print("   • JSON pattern matching")
    print("   • Text pattern matching")
    print("   • Enhanced selectors")
    print("   • Better error handling")
    print()
    
    # Scrape all posts with improved mobile optimization
    async with ImprovedMobileScraper(headless=True, debug=True) as scraper:
        results_df = await scraper.scrape_posts(posts_data)
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"IMPROVED_MOBILE_YOUR_3_LINKS_SCRAPED_DATA_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n📱 IMPROVED MOBILE SCRAPING RESULTS:")
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
        print(f"   Bookmarks: {row['bookmarks']:,}")
        print(f"   Engagement Rate: {row['engagement_rate']:.2f}%")
        print(f"   Account: @{row['account_username']}")
        print(f"   Followers: {row['account_followers']:,}")
    
    print(f"\n💾 Improved mobile results saved to: {output_file}")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(main())
