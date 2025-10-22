"""
Working Mobile Scraper for 5 Videos
SuperClaude Working Mobile TikTok Scraper

Uses the PROVEN mobile method that extracted real views before
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

class WorkingMobileScraper:
    """
    Working mobile scraper using the PROVEN method
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

    async def _scrape_single_post(self, post_url: str) -> dict:
        """
        Scrape single post using PROVEN mobile method
        """
        try:
            # Create new page
            page = await self.browser.new_page()
            
            # Set MOBILE user agent (PROVEN METHOD)
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
            })
            
            # Set MOBILE viewport (PROVEN METHOD)
            await page.set_viewport_size({"width": 375, "height": 667})
            
            logger.info(f"📱 Working mobile scraping: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Debug: Save page content for analysis
            if self.debug:
                page_content = await page.content()
                url_id = post_url.split('/')[-2] if '/' in post_url else 'unknown'
                with open(f'working_mobile_debug_{url_id}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"📱 Working mobile debug: Saved page content to working_mobile_debug_{url_id}.html")
            
            # Extract metrics using PROVEN METHOD
            metrics = await self._extract_metrics_proven(page, post_url)
            
            await page.close()
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Working mobile scraping failed {post_url}: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0, "engagement_rate": 0.0,
                "account_username": "Unknown", "account_followers": 0,
                "error": str(e)
            }

    async def _extract_metrics_proven(self, page, post_url):
        """
        Extract metrics using the PROVEN method that worked before
        """
        metrics = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat()
        }
        
        try:
            # Extract views - PROVEN METHOD (JSON data)
            views = await self._extract_views_proven(page)
            metrics["views"] = views
            
            # Extract likes - try multiple methods
            likes = await self._extract_likes_proven(page)
            metrics["likes"] = likes

            # Extract comments - try multiple methods
            comments = await self._extract_comments_proven(page)
            metrics["comments"] = comments

            # Extract shares - try multiple methods
            shares = await self._extract_shares_proven(page)
            metrics["shares"] = shares

            # Extract bookmarks - try multiple methods
            bookmarks = await self._extract_bookmarks_proven(page)
            metrics["bookmarks"] = bookmarks

            # Calculate engagement
            total_engagement = metrics["likes"] + metrics["comments"] + metrics["shares"] + metrics["bookmarks"]
            metrics["engagement"] = total_engagement
            
            if metrics["views"] > 0:
                metrics["engagement_rate"] = round((total_engagement / metrics["views"]) * 100, 2)
            else:
                metrics["engagement_rate"] = 0.0
            
            # Extract account details
            account_data = await self._extract_account_details_proven(page, post_url)
            metrics.update(account_data)
            
            logger.info(f"📱 Working mobile success: {post_url} - Views: {metrics['views']:,}, Likes: {metrics['likes']:,}, Comments: {metrics['comments']:,}")

        except Exception as e:
            logger.error(f"❌ Error extracting proven metrics for {post_url}: {e}")
            # Fallback to default values if extraction fails
            metrics.update({
                "views": 0, "likes": 0, "comments": 0, "shares": 0, "bookmarks": 0,
                "engagement": 0.0,
                "engagement_rate": 0.0,
                "account_username": "Unknown",
                "account_followers": 0
            })
        
        return metrics
    
    async def _extract_views_proven(self, page):
        """
        Extract views using PROVEN method (JSON data)
        """
        try:
            page_content = await page.content()
            
            # PROVEN METHOD: Look for playCount in the JSON data
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"📱 PROVEN: Found views in JSON data: {views}")
                return views
        except Exception as e:
            logger.debug(f"📱 PROVEN JSON extraction failed: {e}")
        
        # Fallback: Try selectors
        view_selectors = [
            '[data-e2e="video-views"]',
            'strong[data-e2e="video-views"]',
            'span[data-e2e="video-views"]',
            '[class*="view"] strong',
            '[class*="View"] strong'
        ]
        
        for selector in view_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 PROVEN: Found views with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        logger.warning("📱 PROVEN: Could not extract views with any method")
        return 0
    
    async def _extract_likes_proven(self, page):
        """
        Extract likes using multiple methods
        """
        # Method 1: JSON data
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
                    logger.info(f"📱 PROVEN: Found likes in JSON pattern '{pattern}': {likes}")
                    return likes
        except Exception:
            pass
        
        # Method 2: Selectors
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
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 PROVEN: Found likes with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_comments_proven(self, page):
        """
        Extract comments using multiple methods
        """
        # Method 1: JSON data
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
                    logger.info(f"📱 PROVEN: Found comments in JSON pattern '{pattern}': {comments}")
                    return comments
        except Exception:
            pass
        
        # Method 2: Selectors
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
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 PROVEN: Found comments with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_shares_proven(self, page):
        """
        Extract shares using multiple methods
        """
        # Method 1: JSON data
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
                    logger.info(f"📱 PROVEN: Found shares in JSON pattern '{pattern}': {shares}")
                    return shares
        except Exception:
            pass
        
        # Method 2: Selectors
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
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 PROVEN: Found shares with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_bookmarks_proven(self, page):
        """
        Extract bookmarks using multiple methods
        """
        # Method 1: JSON data
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
                    logger.info(f"📱 PROVEN: Found bookmarks in JSON pattern '{pattern}': {bookmarks}")
                    return bookmarks
        except Exception:
            pass
        
        # Method 2: Selectors
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
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 PROVEN: Found bookmarks with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        return 0
    
    async def _extract_account_details_proven(self, page, post_url: str) -> dict:
        """
        Extract account details using multiple methods
        """
        try:
            logger.info(f"📱 PROVEN: Extracting account details from: {post_url}")
            
            # Extract username from URL or page
            username = await self._extract_username_proven(page, post_url)
            
            # Extract followers
            followers = await self._extract_followers_proven(page)
            
            return {
                "account_username": username,
                "account_followers": followers
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting proven account details: {e}")
            return {
                "account_username": "Unknown",
                "account_followers": 0
            }
    
    async def _extract_username_proven(self, page, post_url: str) -> str:
        """Extract username using multiple methods"""
        try:
            # Method 1: From URL
            url_match = re.search(r'@([^/]+)', post_url)
            if url_match:
                return url_match.group(1)
            
            # Method 2: From page
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
    
    async def _extract_followers_proven(self, page):
        """
        Extract followers using multiple methods
        """
        # Method 1: JSON data
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
                    logger.info(f"📱 PROVEN: Found followers in JSON pattern '{pattern}': {followers}")
                    return followers
        except Exception:
            pass
        
        # Method 2: Selectors
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
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"📱 PROVEN: Found followers with selector '{selector}': {text} -> {parsed}")
                            return parsed
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
            # Extract only digits, handle cases like "22 comments"
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

    async def scrape_posts(self, urls: list) -> pd.DataFrame:
        """
        Scrape multiple posts using PROVEN method
        """
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"📱 Working mobile scraping post {i}/{len(urls)}: {url}")
            
            result = await self._scrape_single_post(url)
            results.append(result)
            
            # Add delay between posts
            if i < len(urls):
                await asyncio.sleep(2)
        
        return pd.DataFrame(results)

async def main():
    """Main execution"""
    print("📱 WORKING MOBILE SCRAPER - 5 VIDEOS TEST")
    print("=" * 60)
    
    # First 5 URLs from your list
    test_urls = [
        "https://www.tiktok.com/t/ZTMuUscW9/",
        "https://www.tiktok.com/t/ZTMuUEG3c/",
        "https://www.tiktok.com/t/ZTMuyRh5a/",
        "https://www.tiktok.com/t/ZP8A7kX4w/",
        "https://www.tiktok.com/t/ZP8A7L74E/"
    ]
    
    print(f"📱 Working mobile scraping: {len(test_urls)} URLs")
    print("📊 Using PROVEN method that extracted real views before")
    print("🎯 Goal: Extract ALL metrics (views, likes, comments, shares, followers)")
    print()
    
    # Scrape all posts with PROVEN method
    async with WorkingMobileScraper(headless=True, debug=True) as scraper:
        results_df = await scraper.scrape_posts(test_urls)
    
    # Save results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"WORKING_MOBILE_5_VIDEOS_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    
    print("\n📱 WORKING MOBILE SCRAPING RESULTS:")
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
        print("\n❌ FAILED! Need to improve extraction methods!")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(main())
