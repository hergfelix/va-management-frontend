#!/usr/bin/env python3
"""
Agent 2: Playwright Direct Scraping Implementation
TikTok Metrics Scraper using Playwright with minimal overhead
"""

import asyncio
import re
import time
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Browser, Page
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaywrightTikTokScraper:
    """
    Direct TikTok scraping using Playwright
    Focus: Only metrics extraction, no video downloads
    """
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.cost_per_post = 0.0001  # Minimal cost (just compute time)
        
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
    
    async def scrape_post_metrics(self, post_url: str) -> Dict:
        """
        Scrape metrics for a single TikTok post
        """
        page = await self.browser.new_page()
        
        try:
            # Set user agent and viewport
            await page.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to post
            logger.info(f"Scraping: {post_url}")
            await page.goto(post_url, timeout=self.timeout)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Extract metrics using CSS selectors
            metrics = await self._extract_metrics(page)
            metrics["post_url"] = post_url
            metrics["scraped_at"] = time.time()
            
            logger.info(f"Successfully scraped: {post_url}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to scrape {post_url}: {str(e)}")
            return {
                "post_url": post_url,
                "error": str(e),
                "scraped_at": time.time()
            }
        finally:
            await page.close()
    
    async def _extract_metrics(self, page: Page) -> Dict:
        """
        Extract metrics from TikTok page using CSS selectors
        """
        metrics = {}
        
        try:
            # Wait for metrics to load
            await page.wait_for_selector('[data-e2e="video-views"]', timeout=10000)
            
            # Extract views
            views_element = await page.query_selector('[data-e2e="video-views"]')
            if views_element:
                views_text = await views_element.text_content()
                metrics["views"] = self._parse_metric(views_text)
            
            # Extract likes
            likes_element = await page.query_selector('[data-e2e="like-count"]')
            if likes_element:
                likes_text = await likes_element.text_content()
                metrics["likes"] = self._parse_metric(likes_text)
            
            # Extract comments
            comments_element = await page.query_selector('[data-e2e="comment-count"]')
            if comments_element:
                comments_text = await comments_element.text_content()
                metrics["comments"] = self._parse_metric(comments_text)
            
            # Extract shares
            shares_element = await page.query_selector('[data-e2e="share-count"]')
            if shares_element:
                shares_text = await shares_element.text_content()
                metrics["shares"] = self._parse_metric(shares_text)
            
            # Extract bookmarks (if available)
            bookmarks_element = await page.query_selector('[data-e2e="bookmark-count"]')
            if bookmarks_element:
                bookmarks_text = await bookmarks_element.text_content()
                metrics["bookmarks"] = self._parse_metric(bookmarks_text)
            else:
                metrics["bookmarks"] = 0
            
            # Calculate engagement rate
            if metrics.get("views", 0) > 0:
                total_engagement = (
                    metrics.get("likes", 0) + 
                    metrics.get("comments", 0) + 
                    metrics.get("shares", 0) + 
                    metrics.get("bookmarks", 0)
                )
                metrics["engagement_rate"] = round(
                    (total_engagement / metrics["views"]) * 100, 2
                )
            else:
                metrics["engagement_rate"] = 0.0
            
        except Exception as e:
            logger.warning(f"Error extracting metrics: {str(e)}")
            # Set default values
            metrics.update({
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "bookmarks": 0,
                "engagement_rate": 0.0
            })
        
        return metrics
    
    def _parse_metric(self, value: str) -> int:
        """
        Parse TikTok metric format (e.g., '10.5K' -> 10500)
        """
        if not value:
            return 0
        
        # Remove any non-numeric characters except K, M, B
        value = re.sub(r'[^\d.KMB]', '', str(value).upper())
        
        if 'K' in value:
            return int(float(value.replace('K', '')) * 1000)
        elif 'M' in value:
            return int(float(value.replace('M', '')) * 1000000)
        elif 'B' in value:
            return int(float(value.replace('B', '')) * 1000000000)
        else:
            try:
                return int(value)
            except ValueError:
                return 0
    
    async def scrape_batch(self, post_urls: List[str], delay: float = 2.0) -> List[Dict]:
        """
        Scrape multiple posts with rate limiting
        """
        results = []
        
        for i, url in enumerate(post_urls):
            try:
                result = await self.scrape_post_metrics(url)
                results.append(result)
                
                # Rate limiting
                if i < len(post_urls) - 1:
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Batch scraping error for {url}: {str(e)}")
                results.append({
                    "post_url": url,
                    "error": str(e),
                    "scraped_at": time.time()
                })
        
        return results

# Test function
async def test_playwright_scraper():
    """
    Test the Playwright scraper with sample URLs
    """
    test_urls = [
        "https://www.tiktok.com/@miriamrollqueen/video/7502407048114605354",
        "https://www.tiktok.com/@miriglow/video/7502422163824151851",
        # Add more test URLs here
    ]
    
    async with PlaywrightTikTokScraper(headless=True) as scraper:
        print("Testing Playwright TikTok Scraper...")
        
        start_time = time.time()
        results = await scraper.scrape_batch(test_urls, delay=1.0)
        end_time = time.time()
        
        # Calculate metrics
        successful_scrapes = [r for r in results if "error" not in r]
        success_rate = len(successful_scrapes) / len(test_urls) * 100
        total_time = end_time - start_time
        posts_per_minute = len(test_urls) / (total_time / 60)
        
        print(f"\n=== Playwright Scraper Test Results ===")
        print(f"Posts tested: {len(test_urls)}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Speed: {posts_per_minute:.1f} posts/minute")
        print(f"Cost: ${len(test_urls) * scraper.cost_per_post:.4f}")
        
        # Show sample results
        for result in results[:2]:  # Show first 2 results
            if "error" not in result:
                print(f"\nSample result:")
                print(f"  URL: {result['post_url']}")
                print(f"  Views: {result.get('views', 0):,}")
                print(f"  Likes: {result.get('likes', 0):,}")
                print(f"  Comments: {result.get('comments', 0):,}")
                print(f"  Shares: {result.get('shares', 0):,}")
                print(f"  Engagement Rate: {result.get('engagement_rate', 0):.2f}%")
        
        return results

if __name__ == "__main__":
    asyncio.run(test_playwright_scraper())
