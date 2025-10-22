"""
Real Session Comment Scraper
SuperClaude Real Session Comments Extraction Specialist

This scraper will use real user sessions to extract comments
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealSessionCommentScraper:
    """
    Real session comment scraper using actual user sessions
    """
    
    def __init__(self, session_cookies=None, proxy_url=None):
        self.session_cookies = session_cookies
        self.proxy_url = proxy_url
        self.session = None
        
    async def __aenter__(self):
        """Setup session with real cookies and proxy"""
        connector = None
        if self.proxy_url:
            connector = aiohttp.ProxyConnector.from_url(self.proxy_url)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest'
            },
            cookies=self.session_cookies
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        if self.session:
            await self.session.close()

    async def scrape_comments_with_real_session(self, post_url: str) -> dict:
        """
        Scrape comments using real user session
        """
        try:
            logger.info(f"💬 Real session comment scraping: {post_url}")
            
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
            
            # Try API endpoints with real session
            api_endpoints = [
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=20",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=50",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=100",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=200",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=500"
            ]
            
            for endpoint in api_endpoints:
                try:
                    logger.info(f"🔄 Trying API endpoint with real session: {endpoint}")
                    comments_data = await self._call_api_with_real_session(endpoint)
                    if comments_data.get("success", False) and comments_data.get("comments"):
                        return comments_data
                except Exception as e:
                    logger.error(f"❌ API endpoint failed: {e}")
                    continue
            
            return {
                "post_url": post_url,
                "success": False,
                "error": "All API endpoints failed",
                "comments": []
            }
            
        except Exception as e:
            logger.error(f"❌ Real session scraping failed: {e}")
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

    async def _call_api_with_real_session(self, endpoint: str) -> dict:
        """Call API with real session"""
        try:
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ API call successful with real session: {response.status}")
                    
                    # Parse comments from response
                    comments = self._parse_real_session_response(data)
                    
                    return {
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments),
                        "api_endpoint": endpoint,
                        "raw_response": data
                    }
                else:
                    logger.warning(f"⚠️ API call failed: {response.status}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "api_endpoint": endpoint
                    }
                    
        except Exception as e:
            logger.error(f"❌ API call error: {e}")
            return {
                "success": False,
                "error": str(e),
                "api_endpoint": endpoint
            }

    def _parse_real_session_response(self, data: dict) -> list:
        """Parse comments from real session response"""
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
                            parsed_comment = self._parse_single_comment_real_session(comment)
                            if parsed_comment:
                                comments.append(parsed_comment)
                    break
            
            # If no comments found, look for comment text patterns
            if not comments:
                comments = self._extract_comments_from_text(data)
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error parsing real session response: {e}")
            return []

    def _parse_single_comment_real_session(self, comment: dict) -> dict:
        """Parse a single comment from real session response"""
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
            
            # Extract replies
            replies = []
            if comment.get('replies'):
                for reply in comment['replies']:
                    reply_data = self._parse_single_comment_real_session(reply)
                    if reply_data:
                        replies.append(reply_data)
            
            return {
                "text": text,
                "author": author,
                "likes": likes,
                "timestamp": timestamp,
                "replies": replies,
                "source": "real_session_scraper"
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
                            "replies": [],
                            "source": "text_extraction"
                        })
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from text: {e}")
            return []

async def main():
    """Main execution"""
    print("💬 REAL SESSION COMMENT SCRAPER")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"🔧 Method: Real User Session")
    print(f"💰 Cost: Session cookies + Proxy costs")
    print()
    
    print("🔑 SESSION OPTIONS:")
    print("1. Buy TikTok session cookies from providers")
    print("2. Use residential proxies with session rotation")
    print("3. Create real TikTok accounts and extract cookies")
    print("4. Use browser automation with real accounts")
    print()
    
    print("💡 RECOMMENDED APPROACH:")
    print("1. Buy session cookies from providers like:")
    print("   - Proxy-seller.com")
    print("   - Bright Data")
    print("   - Oxylabs")
    print("   - Smartproxy")
    print()
    print("2. Use residential proxies for IP rotation")
    print("3. Implement session rotation")
    print("4. Add rate limiting")
    print()
    
    # Example session cookies (you would get these from a provider)
    example_cookies = {
        'sessionid': 'your_session_id_here',
        'ttwid': 'your_ttwid_here',
        'msToken': 'your_ms_token_here',
        'odin_tt': 'your_odin_tt_here'
    }
    
    # Example proxy URL
    proxy_url = "http://username:password@proxy.provider.com:8080"
    
    print("⚠️  TO USE THIS SCRAPER:")
    print("1. Buy session cookies from a provider")
    print("2. Set up residential proxy")
    print("3. Update the cookies and proxy_url variables")
    print("4. Run the scraper")
    print()
    
    # For demo purposes, we'll run without real session
    print("🔄 Running demo without real session...")
    
    # Scrape comments with real session (demo)
    async with RealSessionCommentScraper() as scraper:
        comments_data = await scraper.scrape_comments_with_real_session(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"real_session_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 REAL SESSION COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted with real session!")
        print(f"💬 Comments Found: {comments_data.get('comment_count', 0)}")
        
        comments = comments_data.get('comments', [])
        if comments:
            print(f"\n💬 SAMPLE COMMENTS WITH AUTHORS:")
            for i, comment in enumerate(comments[:10], 1):
                text = comment.get('text', 'N/A')[:60] + "..." if len(comment.get('text', '')) > 60 else comment.get('text', 'N/A')
                author = comment.get('author', 'N/A')
                likes = comment.get('likes', 0)
                replies_count = len(comment.get('replies', []))
                print(f"   {i:2d}. @{author}: {text} ({likes} likes, {replies_count} replies)")
            
            # Analyze authors
            authors = [comment.get('author', 'Unknown') for comment in comments]
            unique_authors = list(set(authors))
            print(f"\n👥 UNIQUE AUTHORS: {len(unique_authors)}")
            for author in unique_authors[:10]:
                count = authors.count(author)
                print(f"   • @{author}: {count} comments")
        else:
            print("⚠️ No comments found")
    else:
        print("❌ Real session comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
