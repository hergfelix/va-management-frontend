"""
Reverse Engineered Comment Scraper
SuperClaude Reverse Engineering Specialist

This scraper will reverse engineer Apify's method to extract comments
"""

import asyncio
import pandas as pd
import time
import random
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReverseEngineeredCommentScraper:
    """
    Reverse engineered comment scraper based on Apify's method
    """
    
    def __init__(self, headless=False, debug=True):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Advanced browser setup with Apify-like configuration"""
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-javascript',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_comments_reverse_engineered(self, post_url: str) -> dict:
        """
        Reverse engineered comment scraping based on Apify's method
        """
        try:
            logger.info(f"💬 Reverse engineered comment scraping: {post_url}")
            
            # Create context with Apify-like settings
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            page = await context.new_page()
            
            # Advanced stealth (Apify-like)
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32',
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Override automation detection
                window.chrome = {
                    runtime: {},
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Try Apify's method: Direct API calls
            comments_data = await self._apify_method_direct_api(page, post_url)
            
            await context.close()
            return comments_data
            
        except Exception as e:
            logger.error(f"❌ Reverse engineered scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
                "comments": []
            }

    async def _apify_method_direct_api(self, page, post_url):
        """Apify's method: Direct API calls to TikTok's internal APIs"""
        try:
            # Extract video ID
            video_id = self._extract_video_id(post_url)
            if not video_id:
                return {"success": False, "error": "Could not extract video ID"}
            
            logger.info(f"🎯 Video ID: {video_id}")
            
            # Apify's method: Use TikTok's internal API endpoints
            api_endpoints = [
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=20",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=50",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=100",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=200",
                f"https://www.tiktok.com/api/comment/list/?aweme_id={video_id}&cursor=0&count=500"
            ]
            
            # Try to get session cookies first
            cookies = await page.context.cookies()
            cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            
            # Make API calls with proper headers
            for endpoint in api_endpoints:
                try:
                    logger.info(f"🔄 Trying API endpoint: {endpoint}")
                    
                    # Use page.evaluate to make API call from browser context
                    response = await page.evaluate(f"""
                        async () => {{
                            try {{
                                const response = await fetch('{endpoint}', {{
                                    method: 'GET',
                                    headers: {{
                                        'Accept': 'application/json, text/plain, */*',
                                        'Accept-Language': 'en-US,en;q=0.9',
                                        'Accept-Encoding': 'gzip, deflate, br',
                                        'Connection': 'keep-alive',
                                        'Referer': '{post_url}',
                                        'Sec-Fetch-Dest': 'empty',
                                        'Sec-Fetch-Mode': 'cors',
                                        'Sec-Fetch-Site': 'same-origin',
                                        'X-Requested-With': 'XMLHttpRequest'
                                    }},
                                    credentials: 'include'
                                }});
                                
                                if (response.ok) {{
                                    const data = await response.json();
                                    return {{ success: true, data: data, status: response.status }};
                                }} else {{
                                    return {{ success: false, status: response.status, error: 'HTTP ' + response.status }};
                                }}
                            }} catch (error) {{
                                return {{ success: false, error: error.message }};
                            }}
                        }}
                    """)
                    
                    if response.get("success", False):
                        logger.info(f"✅ API call successful: {response.get('status')}")
                        
                        # Parse comments from response
                        comments = self._parse_apify_response(response.get("data", {}))
                        if comments:
                            return {
                                "post_url": post_url,
                                "method": "apify_direct_api",
                                "success": True,
                                "comments": comments,
                                "comment_count": len(comments),
                                "api_endpoint": endpoint
                            }
                    else:
                        logger.warning(f"⚠️ API call failed: {response.get('error')}")
                        
                except Exception as e:
                    logger.error(f"❌ API endpoint error: {e}")
                    continue
            
            return {"success": False, "error": "All API endpoints failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

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

    def _parse_apify_response(self, data: dict) -> list:
        """Parse comments from Apify-style response"""
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
                            parsed_comment = self._parse_single_comment_apify(comment)
                            if parsed_comment:
                                comments.append(parsed_comment)
                    break
            
            # If no comments found, look for comment text patterns
            if not comments:
                comments = self._extract_comments_from_text(data)
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error parsing Apify response: {e}")
            return []

    def _parse_single_comment_apify(self, comment: dict) -> dict:
        """Parse a single comment from Apify-style response"""
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
                    reply_data = self._parse_single_comment_apify(reply)
                    if reply_data:
                        replies.append(reply_data)
            
            return {
                "text": text,
                "author": author,
                "likes": likes,
                "timestamp": timestamp,
                "replies": replies,
                "source": "apify_reverse_engineered"
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
    print("💬 REVERSE ENGINEERED COMMENT SCRAPER")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"🔧 Method: Reverse engineered Apify method")
    print(f"💰 Cost: FREE (no Apify fees)")
    print()
    
    # Scrape comments with reverse engineered method
    async with ReverseEngineeredCommentScraper(headless=False, debug=True) as scraper:
        comments_data = await scraper.scrape_comments_reverse_engineered(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"reverse_engineered_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 REVERSE ENGINEERED COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted with reverse engineered method!")
        print(f"💬 Method: {comments_data.get('method', 'N/A')}")
        print(f"💬 Comments Found: {comments_data.get('comment_count', 0)}")
        print(f"🔗 API Endpoint: {comments_data.get('api_endpoint', 'N/A')}")
        
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
            
            # Analyze replies
            total_replies = sum(len(comment.get('replies', [])) for comment in comments)
            print(f"\n💬 TOTAL REPLIES: {total_replies}")
            
            # Show sample replies
            if total_replies > 0:
                print(f"\n💬 SAMPLE REPLIES:")
                reply_count = 0
                for comment in comments:
                    for reply in comment.get('replies', []):
                        if reply_count < 5:
                            text = reply.get('text', 'N/A')[:50] + "..." if len(reply.get('text', '')) > 50 else reply.get('text', 'N/A')
                            author = reply.get('author', 'N/A')
                            print(f"   • @{author}: {text}")
                            reply_count += 1
        else:
            print("⚠️ No comments found")
    else:
        print("❌ Reverse engineered comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
