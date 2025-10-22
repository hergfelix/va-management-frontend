#!/usr/bin/env python3
"""
Agent 3: TikTok Unofficial API Implementation
Research and implementation of TikTok's internal GraphQL API
"""

import asyncio
import aiohttp
import json
import time
import hashlib
import random
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokAPIScraper:
    """
    TikTok Unofficial API Scraper
    Uses TikTok's internal GraphQL endpoints for data extraction
    """
    
    def __init__(self):
        self.base_url = "https://www.tiktok.com/api"
        self.graphql_url = "https://www.tiktok.com/api/graphql"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cost_per_post = 0.00005  # Very low cost (just API calls)
        
        # TikTok API headers (simulated mobile app)
        self.headers = {
            "User-Agent": "com.zhiliaoapp.musically/2023110100 (Linux; U; Android 11; en_US; SM-G973F; Build/PPR1.180610.011; Cronet/58.0.2991.0)",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest",
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _generate_device_id(self) -> str:
        """Generate a realistic device ID"""
        return f"7{random.randint(1000000000000000, 9999999999999999)}"
    
    def _generate_signature(self, data: str) -> str:
        """Generate request signature (simplified)"""
        # In reality, TikTok uses complex signature generation
        # This is a simplified version for demonstration
        return hashlib.md5(data.encode()).hexdigest()
    
    async def scrape_post_metrics(self, post_url: str) -> Dict:
        """
        Scrape post metrics using TikTok's GraphQL API
        """
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(post_url)
            if not video_id:
                raise ValueError(f"Could not extract video ID from {post_url}")
            
            # GraphQL query for post details
            query = {
                "query": """
                query VideoDetail($videoId: String!) {
                    videoDetail(videoId: $videoId) {
                        id
                        desc
                        createTime
                        video {
                            id
                            playAddr
                            cover
                            duration
                            ratio
                            playCount
                            diggCount
                            commentCount
                            shareCount
                            collectCount
                        }
                        author {
                            id
                            uniqueId
                            nickname
                            avatarMedium
                            followerCount
                            followingCount
                            heartCount
                            videoCount
                        }
                    }
                }
                """,
                "variables": {
                    "videoId": video_id
                }
            }
            
            # Add device ID and signature
            device_id = self._generate_device_id()
            signature = self._generate_signature(json.dumps(query))
            
            # Prepare request
            params = {
                "device_id": device_id,
                "signature": signature,
                "timestamp": str(int(time.time() * 1000))
            }
            
            # Make API request
            async with self.session.post(
                self.graphql_url,
                json=query,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return self._parse_api_response(data, post_url)
                else:
                    logger.error(f"API request failed: {response.status}")
                    return {
                        "post_url": post_url,
                        "error": f"API request failed: {response.status}",
                        "scraped_at": time.time()
                    }
                    
        except Exception as e:
            logger.error(f"Failed to scrape {post_url}: {str(e)}")
            return {
                "post_url": post_url,
                "error": str(e),
                "scraped_at": time.time()
            }
    
    def _extract_video_id(self, post_url: str) -> Optional[str]:
        """
        Extract video ID from TikTok URL
        """
        import re
        
        # Pattern for TikTok video URLs
        patterns = [
            r'/video/(\d+)',
            r'/v/(\d+)',
            r'video/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, post_url)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_api_response(self, data: Dict, post_url: str) -> Dict:
        """
        Parse TikTok API response and extract metrics
        """
        try:
            video_data = data.get("data", {}).get("videoDetail", {}).get("video", {})
            
            if not video_data:
                return {
                    "post_url": post_url,
                    "error": "No video data in API response",
                    "scraped_at": time.time()
                }
            
            # Extract metrics
            metrics = {
                "post_url": post_url,
                "views": video_data.get("playCount", 0),
                "likes": video_data.get("diggCount", 0),
                "comments": video_data.get("commentCount", 0),
                "shares": video_data.get("shareCount", 0),
                "bookmarks": video_data.get("collectCount", 0),
                "scraped_at": time.time()
            }
            
            # Calculate engagement rate
            if metrics["views"] > 0:
                total_engagement = (
                    metrics["likes"] + 
                    metrics["comments"] + 
                    metrics["shares"] + 
                    metrics["bookmarks"]
                )
                metrics["engagement_rate"] = round(
                    (total_engagement / metrics["views"]) * 100, 2
                )
            else:
                metrics["engagement_rate"] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error parsing API response: {str(e)}")
            return {
                "post_url": post_url,
                "error": f"Parse error: {str(e)}",
                "scraped_at": time.time()
            }
    
    async def scrape_batch(self, post_urls: List[str], delay: float = 1.0) -> List[Dict]:
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

# Alternative approach using web scraping with API endpoints
class TikTokWebAPIScraper:
    """
    Alternative approach: Scrape TikTok's web API endpoints directly
    """
    
    def __init__(self):
        self.base_url = "https://www.tiktok.com/api"
        self.session: Optional[aiohttp.ClientSession] = None
        self.cost_per_post = 0.0001  # Very low cost
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_post_metrics(self, post_url: str) -> Dict:
        """
        Scrape using TikTok's web API endpoints
        """
        try:
            # Extract video ID
            video_id = self._extract_video_id(post_url)
            if not video_id:
                raise ValueError(f"Could not extract video ID from {post_url}")
            
            # Try different API endpoints
            endpoints = [
                f"/item/detail/?itemId={video_id}",
                f"/video/detail/?videoId={video_id}",
                f"/aweme/v1/aweme/detail/?aweme_id={video_id}",
            ]
            
            for endpoint in endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    async with self.session.get(url, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._parse_web_api_response(data, post_url)
                except Exception as e:
                    logger.warning(f"Endpoint {endpoint} failed: {str(e)}")
                    continue
            
            return {
                "post_url": post_url,
                "error": "All API endpoints failed",
                "scraped_at": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape {post_url}: {str(e)}")
            return {
                "post_url": post_url,
                "error": str(e),
                "scraped_at": time.time()
            }
    
    def _extract_video_id(self, post_url: str) -> Optional[str]:
        """Extract video ID from URL"""
        import re
        match = re.search(r'/video/(\d+)', post_url)
        return match.group(1) if match else None
    
    def _parse_web_api_response(self, data: Dict, post_url: str) -> Dict:
        """Parse web API response"""
        try:
            # Navigate through response structure
            video_data = data.get("itemInfo", {}).get("itemStruct", {})
            
            metrics = {
                "post_url": post_url,
                "views": video_data.get("statistics", {}).get("playCount", 0),
                "likes": video_data.get("statistics", {}).get("diggCount", 0),
                "comments": video_data.get("statistics", {}).get("commentCount", 0),
                "shares": video_data.get("statistics", {}).get("shareCount", 0),
                "bookmarks": video_data.get("statistics", {}).get("collectCount", 0),
                "scraped_at": time.time()
            }
            
            # Calculate engagement rate
            if metrics["views"] > 0:
                total_engagement = sum([
                    metrics["likes"], metrics["comments"], 
                    metrics["shares"], metrics["bookmarks"]
                ])
                metrics["engagement_rate"] = round(
                    (total_engagement / metrics["views"]) * 100, 2
                )
            else:
                metrics["engagement_rate"] = 0.0
            
            return metrics
            
        except Exception as e:
            return {
                "post_url": post_url,
                "error": f"Parse error: {str(e)}",
                "scraped_at": time.time()
            }

# Test function
async def test_tiktok_api_scraper():
    """
    Test the TikTok API scraper
    """
    test_urls = [
        "https://www.tiktok.com/@miriamrollqueen/video/7502407048114605354",
        "https://www.tiktok.com/@miriglow/video/7502422163824151851",
    ]
    
    print("Testing TikTok API Scraper...")
    
    # Test GraphQL approach
    async with TikTokAPIScraper() as scraper:
        start_time = time.time()
        results = await scraper.scrape_batch(test_urls, delay=1.0)
        end_time = time.time()
        
        successful_scrapes = [r for r in results if "error" not in r]
        success_rate = len(successful_scrapes) / len(test_urls) * 100
        total_time = end_time - start_time
        posts_per_minute = len(test_urls) / (total_time / 60)
        
        print(f"\n=== TikTok API Scraper Test Results ===")
        print(f"Posts tested: {len(test_urls)}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Speed: {posts_per_minute:.1f} posts/minute")
        print(f"Cost: ${len(test_urls) * scraper.cost_per_post:.4f}")
        
        # Show sample results
        for result in results:
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
    asyncio.run(test_tiktok_api_scraper())
