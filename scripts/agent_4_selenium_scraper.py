#!/usr/bin/env python3
"""
Agent 4: Selenium Grid Approach
Multi-browser parallel scraping with proxy rotation and anti-detection
"""

import asyncio
import time
import random
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumTikTokScraper:
    """
    Selenium-based TikTok scraper with multi-browser support
    """
    
    def __init__(self, max_workers: int = 3, headless: bool = True):
        self.max_workers = max_workers
        self.headless = headless
        self.cost_per_post = 0.0002  # Slightly higher due to browser overhead
        self.drivers = []
        self.lock = threading.Lock()
        
    def _create_driver(self, proxy: Optional[str] = None) -> webdriver.Chrome:
        """
        Create a Chrome driver with anti-detection measures
        """
        options = Options()
        
        if self.headless:
            options.add_argument("--headless")
        
        # Anti-detection measures
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent spoofing
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Window size
        options.add_argument("--window-size=1920,1080")
        
        # Proxy configuration
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        
        # Performance optimizations
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")  # We'll enable it selectively
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")
        
        # Create driver
        driver = webdriver.Chrome(options=options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _extract_metrics(self, driver: webdriver.Chrome, post_url: str) -> Dict:
        """
        Extract metrics from TikTok page using Selenium
        """
        metrics = {
            "post_url": post_url,
            "scraped_at": time.time()
        }
        
        try:
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Extract views
            try:
                views_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-e2e="video-views"]'))
                )
                views_text = views_element.text
                metrics["views"] = self._parse_metric(views_text)
            except TimeoutException:
                metrics["views"] = 0
            
            # Extract likes
            try:
                likes_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="like-count"]')
                likes_text = likes_element.text
                metrics["likes"] = self._parse_metric(likes_text)
            except NoSuchElementException:
                metrics["likes"] = 0
            
            # Extract comments
            try:
                comments_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="comment-count"]')
                comments_text = comments_element.text
                metrics["comments"] = self._parse_metric(comments_text)
            except NoSuchElementException:
                metrics["comments"] = 0
            
            # Extract shares
            try:
                shares_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="share-count"]')
                shares_text = shares_element.text
                metrics["shares"] = self._parse_metric(shares_text)
            except NoSuchElementException:
                metrics["shares"] = 0
            
            # Extract bookmarks (if available)
            try:
                bookmarks_element = driver.find_element(By.CSS_SELECTOR, '[data-e2e="bookmark-count"]')
                bookmarks_text = bookmarks_element.text
                metrics["bookmarks"] = self._parse_metric(bookmarks_text)
            except NoSuchElementException:
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
            
            logger.info(f"Successfully scraped: {post_url}")
            
        except Exception as e:
            logger.error(f"Error extracting metrics from {post_url}: {str(e)}")
            metrics["error"] = str(e)
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
        
        import re
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
    
    def scrape_post(self, post_url: str, proxy: Optional[str] = None) -> Dict:
        """
        Scrape a single post using Selenium
        """
        driver = None
        try:
            # Create driver
            driver = self._create_driver(proxy)
            
            # Navigate to post
            logger.info(f"Scraping: {post_url}")
            driver.get(post_url)
            
            # Extract metrics
            metrics = self._extract_metrics(driver, post_url)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to scrape {post_url}: {str(e)}")
            return {
                "post_url": post_url,
                "error": str(e),
                "scraped_at": time.time()
            }
        finally:
            if driver:
                driver.quit()
    
    def scrape_batch_parallel(self, post_urls: List[str], proxies: Optional[List[str]] = None) -> List[Dict]:
        """
        Scrape multiple posts in parallel using ThreadPoolExecutor
        """
        results = []
        
        # Prepare proxy list
        if proxies:
            proxy_cycle = proxies * (len(post_urls) // len(proxies) + 1)
        else:
            proxy_cycle = [None] * len(post_urls)
        
        # Create tasks
        tasks = []
        for i, url in enumerate(post_urls):
            proxy = proxy_cycle[i] if i < len(proxy_cycle) else None
            tasks.append((url, proxy))
        
        # Execute in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.scrape_post, url, proxy): url 
                for url, proxy in tasks
            }
            
            # Collect results
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Add delay between requests to avoid rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Task failed for {url}: {str(e)}")
                    results.append({
                        "post_url": url,
                        "error": str(e),
                        "scraped_at": time.time()
                    })
        
        return results
    
    def scrape_batch_sequential(self, post_urls: List[str], delay: float = 2.0) -> List[Dict]:
        """
        Scrape multiple posts sequentially with delays
        """
        results = []
        
        for i, url in enumerate(post_urls):
            try:
                result = self.scrape_post(url)
                results.append(result)
                
                # Rate limiting
                if i < len(post_urls) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Sequential scraping error for {url}: {str(e)}")
                results.append({
                    "post_url": url,
                    "error": str(e),
                    "scraped_at": time.time()
                })
        
        return results

# Test function
def test_selenium_scraper():
    """
    Test the Selenium scraper
    """
    test_urls = [
        "https://www.tiktok.com/@miriamrollqueen/video/7502407048114605354",
        "https://www.tiktok.com/@miriglow/video/7502422163824151851",
        # Add more test URLs here
    ]
    
    scraper = SeleniumTikTokScraper(max_workers=2, headless=True)
    
    print("Testing Selenium TikTok Scraper...")
    
    # Test sequential scraping
    start_time = time.time()
    results = scraper.scrape_batch_sequential(test_urls, delay=2.0)
    end_time = time.time()
    
    # Calculate metrics
    successful_scrapes = [r for r in results if "error" not in r]
    success_rate = len(successful_scrapes) / len(test_urls) * 100
    total_time = end_time - start_time
    posts_per_minute = len(test_urls) / (total_time / 60)
    
    print(f"\n=== Selenium Scraper Test Results ===")
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
        else:
            print(f"\nError result:")
            print(f"  URL: {result['post_url']}")
            print(f"  Error: {result['error']}")
    
    return results

if __name__ == "__main__":
    test_selenium_scraper()
