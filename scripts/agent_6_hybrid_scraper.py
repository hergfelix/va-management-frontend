#!/usr/bin/env python3
"""
Agent 6: Hybrid Approach (Smart Routing)
Intelligent combination of multiple scraping methods with cost optimization
"""

import asyncio
import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingMethod(Enum):
    """Available scraping methods"""
    APIFY = "apify"
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    PUPPETEER = "puppeteer"
    API = "api"

@dataclass
class ScrapingResult:
    """Result from scraping attempt"""
    post_url: str
    method: ScrapingMethod
    success: bool
    metrics: Dict
    cost: float
    duration: float
    error: Optional[str] = None

@dataclass
class MethodStats:
    """Statistics for a scraping method"""
    method: ScrapingMethod
    total_attempts: int = 0
    successful_attempts: int = 0
    total_cost: float = 0.0
    total_duration: float = 0.0
    last_used: float = 0.0
    success_rate: float = 0.0
    avg_cost_per_post: float = 0.0
    avg_duration_per_post: float = 0.0

class HybridTikTokScraper:
    """
    Hybrid TikTok scraper with intelligent method selection
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.method_stats = {method: MethodStats(method) for method in ScrapingMethod}
        self.cost_tracker = CostTracker()
        self.rate_limiter = RateLimiter()
        self.fallback_chain = self._build_fallback_chain()
        
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "max_budget_per_day": 10.0,
            "max_posts_per_day": 10000,
            "preferred_methods": [ScrapingMethod.PLAYWRIGHT, ScrapingMethod.PUPPETEER],
            "fallback_methods": [ScrapingMethod.SELENIUM, ScrapingMethod.APIFY],
            "cost_weights": {
                ScrapingMethod.APIFY: 0.0025,
                ScrapingMethod.PLAYWRIGHT: 0.0001,
                ScrapingMethod.SELENIUM: 0.0002,
                ScrapingMethod.PUPPETEER: 0.00015,
                ScrapingMethod.API: 0.00005
            },
            "success_rate_threshold": 0.8,
            "max_retries": 3,
            "retry_delay": 2.0
        }
    
    def _build_fallback_chain(self) -> List[ScrapingMethod]:
        """Build fallback chain based on cost and reliability"""
        return [
            ScrapingMethod.PLAYWRIGHT,  # Primary: Low cost, good reliability
            ScrapingMethod.PUPPETEER,   # Secondary: Good stealth, moderate cost
            ScrapingMethod.SELENIUM,    # Tertiary: High reliability, higher cost
            ScrapingMethod.APIFY,       # Fallback: Managed service, highest cost
            ScrapingMethod.API          # Last resort: Lowest cost, lowest reliability
        ]
    
    async def scrape_post(self, post_url: str) -> ScrapingResult:
        """
        Scrape a single post using intelligent method selection
        """
        # Check budget constraints
        if self.cost_tracker.daily_cost >= self.config["max_budget_per_day"]:
            return ScrapingResult(
                post_url=post_url,
                method=ScrapingMethod.API,
                success=False,
                metrics={},
                cost=0.0,
                duration=0.0,
                error="Daily budget exceeded"
            )
        
        # Select best method
        method = self._select_best_method()
        
        # Try primary method
        result = await self._scrape_with_method(method, post_url)
        
        # If failed, try fallback methods
        if not result.success:
            for fallback_method in self.fallback_chain:
                if fallback_method == method:
                    continue
                
                logger.info(f"Trying fallback method: {fallback_method.value}")
                result = await self._scrape_with_method(fallback_method, post_url)
                
                if result.success:
                    break
        
        # Update statistics
        self._update_method_stats(result)
        
        return result
    
    def _select_best_method(self) -> ScrapingMethod:
        """
        Select the best method based on cost, success rate, and availability
        """
        # Filter methods by success rate threshold
        viable_methods = [
            method for method, stats in self.method_stats.items()
            if stats.success_rate >= self.config["success_rate_threshold"] or stats.total_attempts == 0
        ]
        
        if not viable_methods:
            # If no viable methods, use the first fallback method
            return self.fallback_chain[0]
        
        # Score methods based on cost and success rate
        method_scores = {}
        for method in viable_methods:
            stats = self.method_stats[method]
            cost_score = 1.0 / (self.config["cost_weights"][method] + 0.0001)
            success_score = stats.success_rate
            recency_score = 1.0 / (time.time() - stats.last_used + 1)
            
            # Weighted score
            method_scores[method] = (
                cost_score * 0.4 +      # 40% cost weight
                success_score * 0.4 +   # 40% success rate weight
                recency_score * 0.2     # 20% recency weight
            )
        
        # Select method with highest score
        best_method = max(method_scores, key=method_scores.get)
        logger.info(f"Selected method: {best_method.value} (score: {method_scores[best_method]:.2f})")
        
        return best_method
    
    async def _scrape_with_method(self, method: ScrapingMethod, post_url: str) -> ScrapingResult:
        """
        Scrape using a specific method
        """
        start_time = time.time()
        
        try:
            # Rate limiting
            await self.rate_limiter.wait(method)
            
            # Scrape based on method
            if method == ScrapingMethod.PLAYWRIGHT:
                metrics = await self._scrape_with_playwright(post_url)
            elif method == ScrapingMethod.PUPPETEER:
                metrics = await self._scrape_with_puppeteer(post_url)
            elif method == ScrapingMethod.SELENIUM:
                metrics = await self._scrape_with_selenium(post_url)
            elif method == ScrapingMethod.APIFY:
                metrics = await self._scrape_with_apify(post_url)
            elif method == ScrapingMethod.API:
                metrics = await self._scrape_with_api(post_url)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            duration = time.time() - start_time
            cost = self.config["cost_weights"][method]
            
            # Update cost tracker
            self.cost_tracker.add_cost(method, cost)
            
            return ScrapingResult(
                post_url=post_url,
                method=method,
                success=True,
                metrics=metrics,
                cost=cost,
                duration=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            cost = self.config["cost_weights"][method]
            
            logger.error(f"Method {method.value} failed for {post_url}: {str(e)}")
            
            return ScrapingResult(
                post_url=post_url,
                method=method,
                success=False,
                metrics={},
                cost=cost,
                duration=duration,
                error=str(e)
            )
    
    async def _scrape_with_playwright(self, post_url: str) -> Dict:
        """Scrape using Playwright (placeholder)"""
        # This would integrate with the actual Playwright scraper
        await asyncio.sleep(0.1)  # Simulate scraping time
        return {
            "views": random.randint(1000, 100000),
            "likes": random.randint(100, 10000),
            "comments": random.randint(10, 1000),
            "shares": random.randint(5, 500),
            "bookmarks": random.randint(0, 100),
            "engagement_rate": random.uniform(1.0, 10.0)
        }
    
    async def _scrape_with_puppeteer(self, post_url: str) -> Dict:
        """Scrape using Puppeteer (placeholder)"""
        # This would integrate with the actual Puppeteer scraper
        await asyncio.sleep(0.15)  # Simulate scraping time
        return {
            "views": random.randint(1000, 100000),
            "likes": random.randint(100, 10000),
            "comments": random.randint(10, 1000),
            "shares": random.randint(5, 500),
            "bookmarks": random.randint(0, 100),
            "engagement_rate": random.uniform(1.0, 10.0)
        }
    
    async def _scrape_with_selenium(self, post_url: str) -> Dict:
        """Scrape using Selenium (placeholder)"""
        # This would integrate with the actual Selenium scraper
        await asyncio.sleep(0.2)  # Simulate scraping time
        return {
            "views": random.randint(1000, 100000),
            "likes": random.randint(100, 10000),
            "comments": random.randint(10, 1000),
            "shares": random.randint(5, 500),
            "bookmarks": random.randint(0, 100),
            "engagement_rate": random.uniform(1.0, 10.0)
        }
    
    async def _scrape_with_apify(self, post_url: str) -> Dict:
        """Scrape using Apify (placeholder)"""
        # This would integrate with the actual Apify scraper
        await asyncio.sleep(0.05)  # Simulate scraping time
        return {
            "views": random.randint(1000, 100000),
            "likes": random.randint(100, 10000),
            "comments": random.randint(10, 1000),
            "shares": random.randint(5, 500),
            "bookmarks": random.randint(0, 100),
            "engagement_rate": random.uniform(1.0, 10.0)
        }
    
    async def _scrape_with_api(self, post_url: str) -> Dict:
        """Scrape using API (placeholder)"""
        # This would integrate with the actual API scraper
        await asyncio.sleep(0.02)  # Simulate scraping time
        # Simulate high failure rate for API
        if random.random() < 0.7:  # 70% failure rate
            raise Exception("API request failed")
        
        return {
            "views": random.randint(1000, 100000),
            "likes": random.randint(100, 10000),
            "comments": random.randint(10, 1000),
            "shares": random.randint(5, 500),
            "bookmarks": random.randint(0, 100),
            "engagement_rate": random.uniform(1.0, 10.0)
        }
    
    def _update_method_stats(self, result: ScrapingResult):
        """Update statistics for a method"""
        stats = self.method_stats[result.method]
        stats.total_attempts += 1
        stats.total_cost += result.cost
        stats.total_duration += result.duration
        stats.last_used = time.time()
        
        if result.success:
            stats.successful_attempts += 1
        
        # Calculate derived metrics
        stats.success_rate = stats.successful_attempts / stats.total_attempts
        stats.avg_cost_per_post = stats.total_cost / stats.total_attempts
        stats.avg_duration_per_post = stats.total_duration / stats.total_attempts
    
    async def scrape_batch(self, post_urls: List[str]) -> List[ScrapingResult]:
        """
        Scrape multiple posts with intelligent routing
        """
        results = []
        
        for i, url in enumerate(post_urls):
            # Check daily limits
            if self.cost_tracker.daily_cost >= self.config["max_budget_per_day"]:
                logger.warning("Daily budget exceeded, stopping batch")
                break
            
            if len(results) >= self.config["max_posts_per_day"]:
                logger.warning("Daily post limit exceeded, stopping batch")
                break
            
            # Scrape post
            result = await self.scrape_post(url)
            results.append(result)
            
            # Progress logging
            if (i + 1) % 10 == 0:
                logger.info(f"Processed {i + 1}/{len(post_urls)} posts")
        
        return results
    
    def get_performance_report(self) -> Dict:
        """Get performance report for all methods"""
        report = {
            "total_cost": self.cost_tracker.daily_cost,
            "total_posts": sum(stats.total_attempts for stats in self.method_stats.values()),
            "methods": {}
        }
        
        for method, stats in self.method_stats.items():
            if stats.total_attempts > 0:
                report["methods"][method.value] = {
                    "attempts": stats.total_attempts,
                    "success_rate": stats.success_rate,
                    "avg_cost": stats.avg_cost_per_post,
                    "avg_duration": stats.avg_duration_per_post,
                    "total_cost": stats.total_cost
                }
        
        return report

class CostTracker:
    """Track costs across methods"""
    
    def __init__(self):
        self.daily_cost = 0.0
        self.method_costs = {method: 0.0 for method in ScrapingMethod}
    
    def add_cost(self, method: ScrapingMethod, cost: float):
        """Add cost for a method"""
        self.daily_cost += cost
        self.method_costs[method] += cost

class RateLimiter:
    """Rate limiting for different methods"""
    
    def __init__(self):
        self.last_request = {method: 0.0 for method in ScrapingMethod}
        self.delays = {
            ScrapingMethod.APIFY: 1.0,
            ScrapingMethod.PLAYWRIGHT: 2.0,
            ScrapingMethod.SELENIUM: 2.5,
            ScrapingMethod.PUPPETEER: 2.0,
            ScrapingMethod.API: 0.5
        }
    
    async def wait(self, method: ScrapingMethod):
        """Wait if necessary to respect rate limits"""
        delay = self.delays[method]
        time_since_last = time.time() - self.last_request[method]
        
        if time_since_last < delay:
            await asyncio.sleep(delay - time_since_last)
        
        self.last_request[method] = time.time()

# Test function
async def test_hybrid_scraper():
    """
    Test the hybrid scraper
    """
    test_urls = [
        "https://www.tiktok.com/@user1/video/123",
        "https://www.tiktok.com/@user2/video/456",
        "https://www.tiktok.com/@user3/video/789",
        "https://www.tiktok.com/@user4/video/101",
        "https://www.tiktok.com/@user5/video/112",
    ]
    
    scraper = HybridTikTokScraper()
    
    print("Testing Hybrid TikTok Scraper...")
    
    start_time = time.time()
    results = await scraper.scrape_batch(test_urls)
    end_time = time.time()
    
    # Calculate metrics
    successful_scrapes = [r for r in results if r.success]
    success_rate = len(successful_scrapes) / len(test_urls) * 100
    total_time = end_time - start_time
    posts_per_minute = len(test_urls) / (total_time / 60)
    total_cost = sum(r.cost for r in results)
    
    print(f"\n=== Hybrid Scraper Test Results ===")
    print(f"Posts tested: {len(test_urls)}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Speed: {posts_per_minute:.1f} posts/minute")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Cost per 1000: ${(total_cost / len(test_urls)) * 1000:.2f}")
    
    # Show method usage
    method_usage = {}
    for result in results:
        method = result.method.value
        method_usage[method] = method_usage.get(method, 0) + 1
    
    print(f"\nMethod usage:")
    for method, count in method_usage.items():
        print(f"  {method}: {count} posts")
    
    # Show performance report
    report = scraper.get_performance_report()
    print(f"\nPerformance report:")
    for method, stats in report["methods"].items():
        print(f"  {method}: {stats['success_rate']:.1%} success, ${stats['avg_cost']:.4f} avg cost")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_hybrid_scraper())
