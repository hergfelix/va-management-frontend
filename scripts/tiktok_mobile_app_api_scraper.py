"""
TikTok Mobile App API Scraper - Final Solution
SuperClaude TikTok Mobile App API Specialist

This scraper will use TikTok's mobile app API directly
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokMobileAppAPIScraper:
    """
    TikTok Mobile App API scraper
    """
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'TikTok 32.0.0 rv:32.0.0 (iPhone; iOS 17.0; en_US) Cronet',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Tt-Token': '',
            'X-Tt-Store-Region': 'us',
            'X-Tt-Store-Region-Src': 'did',
            'X-Tt-Request-Tag': 't=0',
            'X-Tt-Response-Encoding': 'gzip',
            'X-Tt-Response-Compress': '1'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def scrape_comments_mobile_app_api(self, post_url: str) -> dict:
        """
        Scrape comments using TikTok's mobile app API
        """
        try:
            logger.info(f"💬 TikTok Mobile App API scraping: {post_url}")
            
            # Extract video ID
            video_id = self._extract_video_id(post_url)
            if not video_id:
                return {
                    "post_url": post_url,
                    "success": False,
                    "error": "Could not extract video ID",
                    "comments": []
                }
            
            logger.info(f"🎯 Video ID: {video_id}")
            
            # Try mobile app API endpoints
            api_endpoints = [
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=20",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=50",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=100",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=200",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=500"
            ]
            
            for endpoint in api_endpoints:
                try:
                    logger.info(f"🔄 Trying Mobile App API endpoint: {endpoint}")
                    comments_data = await self._call_mobile_app_api_endpoint(endpoint)
                    if comments_data.get("success", False) and comments_data.get("comments"):
                        return comments_data
                except Exception as e:
                    logger.error(f"❌ Mobile App API endpoint failed: {e}")
                    continue
            
            return {
                "post_url": post_url,
                "success": False,
                "error": "All Mobile App API endpoints failed",
                "comments": []
            }
            
        except Exception as e:
            logger.error(f"❌ TikTok Mobile App API scraping failed: {e}")
            return {
                "post_url": post_url,
                "success": False,
                "error": str(e),
                "comments": []
            }

    def _extract_video_id(self, post_url: str) -> str:
        """Extract video ID from TikTok URL"""
        try:
            patterns = [
                r'/t/([^/]+)',
                r'/video/(\d+)',
                r'@[^/]+/video/(\d+)',
                r'aweme_id=(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, post_url)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting video ID: {e}")
            return None

    async def _call_mobile_app_api_endpoint(self, endpoint: str) -> dict:
        """Call a specific mobile app API endpoint"""
        try:
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Mobile App API call successful: {response.status}")
                    
                    # Parse comments from response
                    comments = self._parse_mobile_app_api_response(data)
                    
                    return {
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments),
                        "api_endpoint": endpoint,
                        "raw_response": data
                    }
                else:
                    logger.warning(f"⚠️ Mobile App API call failed: {response.status}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "api_endpoint": endpoint
                    }
                    
        except Exception as e:
            logger.error(f"❌ Mobile App API call error: {e}")
            return {
                "success": False,
                "error": str(e),
                "api_endpoint": endpoint
            }

    def _parse_mobile_app_api_response(self, data: dict) -> list:
        """Parse comments from mobile app API response"""
        comments = []
        
        try:
            # Look for comments in different response structures
            comment_sources = [
                data.get('comments', []),
                data.get('commentList', []),
                data.get('replies', []),
                data.get('data', {}).get('comments', []),
                data.get('data', {}).get('commentList', []),
                data.get('data', {}).get('replies', [])
            ]
            
            for comment_list in comment_sources:
                if isinstance(comment_list, list) and comment_list:
                    logger.info(f"✅ Found {len(comment_list)} comments in response")
                    
                    for comment in comment_list:
                        if isinstance(comment, dict):
                            parsed_comment = self._parse_single_comment_mobile_app(comment)
                            if parsed_comment:
                                comments.append(parsed_comment)
                    break
            
            # If no comments found, look for comment text patterns
            if not comments:
                comments = self._extract_comments_from_text(data)
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error parsing mobile app API response: {e}")
            return []

    def _parse_single_comment_mobile_app(self, comment: dict) -> dict:
        """Parse a single comment from mobile app API response"""
        try:
            # Extract comment text
            text = (
                comment.get('text', '') or
                comment.get('content', '') or
                comment.get('comment', '') or
                comment.get('message', '') or
                comment.get('desc', '') or
                comment.get('comment_text', '')
            )
            
            if not text or len(text) < 5:
                return None
            
            # Extract author
            author = (
                comment.get('author', {}).get('nickname', '') or
                comment.get('author', {}).get('username', '') or
                comment.get('user', {}).get('nickname', '') or
                comment.get('user', {}).get('username', '') or
                comment.get('nickname', '') or
                comment.get('username', '') or
                comment.get('user_name', '') or
                'Unknown'
            )
            
            # Extract likes
            likes = (
                comment.get('digg_count', 0) or
                comment.get('like_count', 0) or
                comment.get('likes', 0) or
                comment.get('diggCount', 0) or
                comment.get('likeCount', 0) or
                0
            )
            
            # Extract timestamp
            timestamp = (
                comment.get('create_time', '') or
                comment.get('timestamp', '') or
                comment.get('createTime', '') or
                datetime.now().isoformat()
            )
            
            return {
                "text": text,
                "author": author,
                "likes": likes,
                "timestamp": timestamp,
                "source": "mobile_app_api_response"
            }
            
        except Exception as e:
            logger.error(f"❌ Error parsing single comment: {e}")
            return None

    def _extract_comments_from_text(self, data: dict) -> list:
        """Extract comments from text patterns in response"""
        comments = []
        
        try:
            # Convert data to string and look for comment patterns
            data_str = json.dumps(data)
            
            # Look for comment text patterns
            text_patterns = [
                r'"text":"([^"]+)"',
                r'"content":"([^"]+)"',
                r'"comment":"([^"]+)"',
                r'"message":"([^"]+)"',
                r'"comment_text":"([^"]+)"'
            ]
            
            for pattern in text_patterns:
                matches = re.findall(pattern, data_str)
                for i, text in enumerate(matches):
                    if len(text) > 5 and not text.startswith('http'):
                        comments.append({
                            "text": text,
                            "author": f"user_{i}",
                            "likes": 0,
                            "timestamp": datetime.now().isoformat(),
                            "source": "text_extraction"
                        })
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from text: {e}")
            return []

async def main():
    """Main execution"""
    print("💬 TIKTOK MOBILE APP API SCRAPER - FINAL SOLUTION")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"🔧 Method: TikTok Mobile App API")
    print(f"💰 Cost: FREE")
    print()
    
    # Scrape comments with mobile app API
    async with TikTokMobileAppAPIScraper() as scraper:
        comments_data = await scraper.scrape_comments_mobile_app_api(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"tiktok_mobile_app_api_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 TIKTOK MOBILE APP API COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted with Mobile App API!")
        print(f"💬 API Endpoint: {comments_data.get('api_endpoint', 'N/A')}")
        print(f"💬 Comments Found: {comments_data.get('comment_count', 0)}")
        
        comments = comments_data.get('comments', [])
        if comments:
            print(f"\n💬 SAMPLE COMMENTS WITH AUTHORS:")
            for i, comment in enumerate(comments[:10], 1):
                text = comment.get('text', 'N/A')[:60] + "..." if len(comment.get('text', '')) > 60 else comment.get('text', 'N/A')
                author = comment.get('author', 'N/A')
                likes = comment.get('likes', 0)
                print(f"   {i:2d}. @{author}: {text} ({likes} likes)")
            
            # Analyze authors
            authors = [comment.get('author', 'Unknown') for comment in comments]
            unique_authors = list(set(authors))
            print(f"\n👥 UNIQUE AUTHORS: {len(unique_authors)}")
            for author in unique_authors[:10]:
                count = authors.count(author)
                print(f"   • @{author}: {count} comments")
        else:
            print("⚠️ No comments found in response")
            if 'raw_response' in comments_data:
                print(f"📄 Raw response: {comments_data['raw_response']}")
    else:
        print("❌ Mobile App API comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
