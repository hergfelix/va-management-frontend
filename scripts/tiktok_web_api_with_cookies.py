"""
TikTok Web API with Real Cookies
SuperClaude TikTok Web API with Cookies Specialist

This scraper will use TikTok's web API with your real cookies
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokWebAPIWithCookies:
    """
    TikTok Web API scraper with real cookies
    """
    
    def __init__(self, cookies_dict=None):
        self.cookies_dict = cookies_dict or {}
        self.session = None
        
    async def __aenter__(self):
        """Setup session with real cookies"""
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://www.tiktok.com/',
                'Origin': 'https://www.tiktok.com',
                'X-Tt-Token': self.cookies_dict.get('tt_csrf_token', ''),
                'X-Tt-Store-Region': 'us',
                'X-Tt-Store-Region-Src': 'did'
            },
            cookies=self.cookies_dict
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        if self.session:
            await self.session.close()

    async def scrape_comments_web_api_with_cookies(self, post_url: str) -> dict:
        """
        Scrape comments using TikTok web API with real cookies
        """
        try:
            logger.info(f"💬 TikTok Web API with cookies: {post_url}")
            
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
            
            # Try multiple web API endpoints
            api_endpoints = [
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=20",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=50",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=100",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=200",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=500"
            ]
            
            for endpoint in api_endpoints:
                try:
                    logger.info(f"🔄 Trying Web API endpoint: {endpoint}")
                    comments_data = await self._call_web_api_endpoint(endpoint)
                    if comments_data.get("success", False) and comments_data.get("comments"):
                        return comments_data
                except Exception as e:
                    logger.error(f"❌ Web API endpoint failed: {e}")
                    continue
            
            return {
                "post_url": post_url,
                "success": False,
                "error": "All Web API endpoints failed",
                "comments": []
            }
            
        except Exception as e:
            logger.error(f"❌ TikTok Web API with cookies failed: {e}")
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

    async def _call_web_api_endpoint(self, endpoint: str) -> dict:
        """Call a specific web API endpoint"""
        try:
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Web API call successful: {response.status}")
                    
                    # Parse comments from response
                    comments = self._parse_web_api_response(data)
                    
                    return {
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments),
                        "api_endpoint": endpoint,
                        "raw_response": data
                    }
                else:
                    logger.warning(f"⚠️ Web API call failed: {response.status}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "api_endpoint": endpoint
                    }
                    
        except Exception as e:
            logger.error(f"❌ Web API call error: {e}")
            return {
                "success": False,
                "error": str(e),
                "api_endpoint": endpoint
            }

    def _parse_web_api_response(self, data: dict) -> list:
        """Parse comments from web API response"""
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
                            parsed_comment = self._parse_single_comment(comment)
                            if parsed_comment:
                                comments.append(parsed_comment)
                    break
            
            # If no comments found, look for comment text patterns
            if not comments:
                comments = self._extract_comments_from_text(data)
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error parsing web API response: {e}")
            return []

    def _parse_single_comment(self, comment: dict) -> dict:
        """Parse a single comment from web API response"""
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
                    reply_data = self._parse_single_comment(reply)
                    if reply_data:
                        replies.append(reply_data)
            
            return {
                "text": text,
                "author": author,
                "likes": likes,
                "timestamp": timestamp,
                "replies": replies,
                "source": "web_api_with_cookies"
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
    print("💬 TIKTOK WEB API WITH COOKIES")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"🔧 Method: TikTok Web API with your real cookies")
    print()
    
    # Your real TikTok cookies
    real_cookies = {
        'delay_guest_mode_vid': '3',
        'msToken': 'o8J0pZGhfk9AQJC-jqOsjZskC-ZxGbC0q1_RPV4GtgLYM1JhJ9S4CXWOgveAs3c79qi1r-ImJKQ0kzscrUiEFMKUjrhRLN_Y5fiHbu54KjvecKPo1Oc7ckwc5m90lxL6DIOuozB5BHZvoxt823WuQMu9',
        'tt_session_tlb_tag': 'sttt%7C2%7C6miGQA6OhHVoymUWTq1xrv_________6SFem7yprIiJZ3JovLXl9pY3oEmPr4IntFq41D2nVWL0%3D',
        'sid_guard': 'ea6886400e8e847568ca65164ead71ae%7C1760813198%7C15552000%7CThu%2C+16-Apr-2026+18%3A46%3A38+GMT',
        'ttwid': '1%7CFlQryCP0YRYJR8dcctWcW-hOAeEYwbs7roVHjgT9bDY%7C1761085257%7C4c676a7b4dbe6f87888662436e0a18088be40f8c06b85ba375d261d3ad622d28',
        'perf_feed_cache': '{%22expireTimestamp%22:1761256800000%2C%22itemIds%22:[%227557497442225097992%22%2C%227541252946684677399%22%2C%227558861093423107350%22]}',
        'cookie-consent': '{%22optional%22:true%2C%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22hubspot%22:true%2C%22version%22:%22v10%22}',
        'uid_tt': '3333535ad1412bb479c94913da72dd678c2b3e28e6486d82bbcef2c02662b355',
        'passport_csrf_token_default': '6aa7765c43224e3f55ef0beb62db90a6',
        's_v_web_id': 'verify_mgwjjik6_7pMbHMWW_2xG8_4laM_Aiyt_hxhgEVPKoGwU',
        'ssid_ucp_v1': '1.0.0-KGNkZTY4NmVmOTA3ZTA3ZWMxYWRkZWY5ODRkOTFlMzUzMThmOGI4ZmMKIQiWiMqu3fLy-WgQjsHPxwYYswsgDDCul8_HBjgIQBJIBBAFGgRubzFhIiBlYTY4ODY0MDBlOGU4NDc1NjhjYTY1MTY0ZWFkNzFhZQ',
        'tiktok_webapp_theme': 'dark',
        'cmpl_token': 'AgQQAPOQF-RO0rjNJTJd4F0v8pJSmFuQf5QbYNxUsg',
        'multi_sids': '7562612043683103766%3Aea6886400e8e847568ca65164ead71ae',
        'passport_auth_status_ss': '40fb31b6e84d9e06167071330dcdc0bf%2C',
        'passport_csrf_token': '6aa7765c43224e3f55ef0beb62db90a6',
        'sessionid': 'ea6886400e8e847568ca65164ead71ae',
        'sessionid_ss': 'ea6886400e8e847568ca65164ead71ae',
        'sid_tt': 'ea6886400e8e847568ca65164ead71ae',
        'sid_ucp_v1': '1.0.0-KGNkZTY4NmVmOTA3ZTA3ZWMxYWRkZWY5ODRkOTFlMzUzMThmOGI4ZmMKIQiWiMqu3fLy-WgQjsHPxwYYswsgDDCul8_HBjgIQBJIBBAFGgRubzFhIiBlYTY4ODY0MDBlOGU4NDc1NjhjYTY1MTY0ZWFkNzFhZQ',
        'tiktok_webapp_theme_source': 'auto',
        'tt_chain_token': 'Igqbw7SDzZgYt8QA9yFNrw==',
        'tt_csrf_token': 'xbwqGqIa-fnWWxmCNZerPT7H9OqmT3wWoOHo',
        'uid_tt_ss': '3333535ad1412bb479c94913da72dd678c2b3e28e6486d82bbcef2c02662b355'
    }
    
    print("🍪 YOUR REAL COOKIES LOADED!")
    print(f"📊 Total cookies: {len(real_cookies)}")
    print("✅ Key cookies found:")
    print(f"   • sessionid: {real_cookies.get('sessionid', 'N/A')[:20]}...")
    print(f"   • ttwid: {real_cookies.get('ttwid', 'N/A')[:20]}...")
    print(f"   • msToken: {real_cookies.get('msToken', 'N/A')[:20]}...")
    print(f"   • uid_tt: {real_cookies.get('uid_tt', 'N/A')[:20]}...")
    print()
    
    print("🚀 TESTING WEB API WITH YOUR COOKIES!")
    print("This should work now...")
    print()
    
    # Test with your real cookies
    async with TikTokWebAPIWithCookies(cookies_dict=real_cookies) as scraper:
        comments_data = await scraper.scrape_comments_web_api_with_cookies(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"web_api_with_cookies_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 WEB API WITH COOKIES RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted with Web API + cookies!")
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
        print("❌ Web API with cookies failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
