"""
Custom Comment Scraper - Professional Solution
SuperClaude Custom Comments Extraction Specialist

This scraper will use advanced browser automation to extract real comments
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

class CustomCommentScraper:
    """
    Custom comment scraper with advanced browser automation
    """
    
    def __init__(self, headless=False, debug=True):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Advanced browser setup"""
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_comments_custom(self, post_url: str) -> dict:
        """
        Custom comment scraping with advanced techniques
        """
        try:
            # Create mobile context with advanced settings
            context = await self.browser.new_context(
                viewport={'width': 375, 'height': 812},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                permissions=['geolocation']
            )
            
            page = await context.new_page()
            
            # Advanced mobile stealth
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'iPhone',
                });
                
                Object.defineProperty(navigator, 'maxTouchPoints', {
                    get: () => 5,
                });
                
                Object.defineProperty(navigator, 'language', {
                    get: () => 'en-US',
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Override touch events
                window.ontouchstart = null;
                window.ontouchmove = null;
                window.ontouchend = null;
            """)
            
            logger.info(f"💬 Custom comment scraping: {post_url}")
            
            # Navigate to post with advanced settings
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Try multiple advanced methods
            comments_data = await self._try_advanced_comment_methods(page, post_url)
            
            await context.close()
            return comments_data
            
        except Exception as e:
            logger.error(f"❌ Custom comment scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
                "comments": []
            }

    async def _try_advanced_comment_methods(self, page, post_url):
        """Try multiple advanced methods to access comments"""
        methods = [
            self._method_1_advanced_click,
            self._method_2_scroll_and_wait,
            self._method_3_direct_comments_url,
            self._method_4_force_comment_load,
            self._method_5_network_interception
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                logger.info(f"🔄 Trying advanced method {i}: {method.__name__}")
                result = await method(page, post_url)
                if result.get("success", False) and result.get("comments"):
                    logger.info(f"✅ Advanced method {i} succeeded!")
                    return result
                else:
                    logger.info(f"⚠️ Advanced method {i} failed, trying next...")
            except Exception as e:
                logger.error(f"❌ Advanced method {i} error: {e}")
                continue
        
        return {
            "post_url": post_url,
            "success": False,
            "error": "All advanced methods failed",
            "comments": []
        }

    async def _method_1_advanced_click(self, page, post_url):
        """Method 1: Advanced clicking with multiple selectors"""
        try:
            # Wait for page to fully load
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # Try multiple comment button selectors
            comment_selectors = [
                '[data-e2e="comment-count"]',
                '[data-e2e="comment-button"]',
                '[data-e2e="browse-comment-count"]',
                '[data-e2e="video-comment-count"]',
                '[class*="comment"]',
                '[class*="Comment"]',
                'button[aria-label*="comment"]',
                'button[aria-label*="Comment"]',
                'div[class*="comment"]',
                'span[class*="comment"]',
                '[data-e2e*="comment"]'
            ]
            
            for selector in comment_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            # Scroll to element
                            await element.scroll_into_view_if_needed()
                            await asyncio.sleep(1)
                            
                            # Click element
                            await element.click()
                            logger.info(f"✅ Clicked comment button: {selector}")
                            await asyncio.sleep(3)
                            
                            # Try to extract comments
                            comments = await self._extract_comments_advanced(page)
                            if comments:
                                return {
                                    "post_url": post_url,
                                    "method": "advanced_click",
                                    "success": True,
                                    "comments": comments,
                                    "comment_count": len(comments)
                                }
                except Exception:
                    continue
            
            return {"success": False, "error": "No comment button found"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _method_2_scroll_and_wait(self, page, post_url):
        """Method 2: Advanced scrolling with waiting"""
        try:
            # Scroll down slowly to trigger comment loading
            for i in range(10):
                await page.mouse.wheel(0, 300)
                await asyncio.sleep(0.5)
                
                # Check if comments are visible
                comments = await self._extract_comments_advanced(page)
                if comments:
                    return {
                        "post_url": post_url,
                        "method": "scroll_and_wait",
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments)
                    }
            
            return {"success": False, "error": "Comments not found after scrolling"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _method_3_direct_comments_url(self, page, post_url):
        """Method 3: Try direct comments URL"""
        try:
            # Try to construct comments URL
            if "/t/" in post_url:
                comments_url = post_url.replace("/t/", "/t/") + "/comments"
                logger.info(f"🔄 Trying direct comments URL: {comments_url}")
                
                await page.goto(comments_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(5)
                
                comments = await self._extract_comments_advanced(page)
                if comments:
                    return {
                        "post_url": post_url,
                        "method": "direct_comments_url",
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments)
                    }
            
            return {"success": False, "error": "Direct comments URL failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _method_4_force_comment_load(self, page, post_url):
        """Method 4: Force comment loading with JavaScript"""
        try:
            # Execute JavaScript to force comment loading
            await page.evaluate("""
                // Try to trigger comment loading
                const commentElements = document.querySelectorAll('[class*="comment"], [data-e2e*="comment"]');
                commentElements.forEach(el => {
                    if (el.click) el.click();
                });
                
                // Try to find and click comment button
                const buttons = document.querySelectorAll('button, div, span');
                buttons.forEach(btn => {
                    const text = btn.textContent || btn.innerText || '';
                    if (text.toLowerCase().includes('comment') || text.includes('💬')) {
                        btn.click();
                    }
                });
                
                // Trigger scroll events
                window.scrollTo(0, document.body.scrollHeight);
            """)
            
            await asyncio.sleep(5)
            
            comments = await self._extract_comments_advanced(page)
            if comments:
                return {
                    "post_url": post_url,
                    "method": "force_comment_load",
                    "success": True,
                    "comments": comments,
                    "comment_count": len(comments)
                }
            
            return {"success": False, "error": "Force comment load failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _method_5_network_interception(self, page, post_url):
        """Method 5: Network interception to catch comment data"""
        try:
            comments = []
            
            # Set up network interception
            async def handle_response(response):
                if 'comment' in response.url.lower() or 'api' in response.url.lower():
                    try:
                        data = await response.json()
                        if data:
                            # Extract comments from response
                            extracted_comments = await self._extract_comments_from_response(data)
                            comments.extend(extracted_comments)
                    except Exception:
                        pass
            
            page.on('response', handle_response)
            
            # Navigate and wait for network requests
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(5)
            
            # Try to trigger comment loading
            await page.evaluate("""
                const commentElements = document.querySelectorAll('[class*="comment"], [data-e2e*="comment"]');
                commentElements.forEach(el => {
                    if (el.click) el.click();
                });
            """)
            
            await asyncio.sleep(5)
            
            if comments:
                return {
                    "post_url": post_url,
                    "method": "network_interception",
                    "success": True,
                    "comments": comments,
                    "comment_count": len(comments)
                }
            
            return {"success": False, "error": "Network interception failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _extract_comments_advanced(self, page):
        """Advanced comment extraction"""
        comments = []
        
        try:
            # Get page content
            page_content = await page.content()
            
            # Method 1: Look for comment elements
            comment_selectors = [
                '[class*="comment-item"]',
                '[class*="comment-content"]',
                '[class*="comment-text"]',
                '[data-e2e*="comment"]',
                '[class*="CommentItem"]',
                '[class*="CommentContent"]',
                '[class*="CommentText"]'
            ]
            
            for selector in comment_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        comment_data = await self._extract_single_comment_advanced(element)
                        if comment_data:
                            comments.append(comment_data)
                except Exception:
                    continue
            
            # Method 2: Look for comment text in page content
            text_comments = await self._extract_comments_from_content(page_content)
            comments.extend(text_comments)
            
            # Method 3: Look for JSON data
            json_comments = await self._extract_comments_from_json(page_content)
            comments.extend(json_comments)
            
            # Remove duplicates
            unique_comments = []
            seen_texts = set()
            for comment in comments:
                if comment["text"] not in seen_texts:
                    unique_comments.append(comment)
                    seen_texts.add(comment["text"])
            
            return unique_comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments advanced: {e}")
            return []

    async def _extract_single_comment_advanced(self, element):
        """Extract a single comment with advanced techniques"""
        try:
            # Get comment text
            text_element = await element.query_selector('[class*="text"], [class*="content"], [class*="comment"]')
            if not text_element:
                text_element = element
            
            text = await text_element.text_content()
            if not text or len(text.strip()) < 5:
                return None
            
            # Get author
            author_element = await element.query_selector('[class*="author"], [class*="username"], [class*="user"]')
            author = "Unknown"
            if author_element:
                author_text = await author_element.text_content()
                if author_text:
                    author = author_text.strip()
            
            # Get likes if available
            likes_element = await element.query_selector('[class*="like"], [class*="heart"]')
            likes = 0
            if likes_element:
                likes_text = await likes_element.text_content()
                if likes_text:
                    likes = self._parse_metric(likes_text)
            
            return {
                "text": text.strip(),
                "author": author,
                "likes": likes,
                "timestamp": datetime.now().isoformat(),
                "source": "advanced_element_extraction"
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting single comment advanced: {e}")
            return None

    async def _extract_comments_from_content(self, page_content):
        """Extract comments from page content"""
        comments = []
        
        try:
            # Look for comment text patterns
            text_patterns = [
                r'"text":"([^"]+)"',
                r'"content":"([^"]+)"',
                r'"comment":"([^"]+)"',
                r'"message":"([^"]+)"'
            ]
            
            for pattern in text_patterns:
                matches = re.findall(pattern, page_content)
                for i, text in enumerate(matches):
                    if len(text) > 5 and not text.startswith('http'):
                        comments.append({
                            "text": text,
                            "author": f"user_{i}",
                            "likes": 0,
                            "timestamp": datetime.now().isoformat(),
                            "source": "content_extraction"
                        })
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from content: {e}")
            return []

    async def _extract_comments_from_json(self, page_content):
        """Extract comments from JSON data"""
        comments = []
        
        try:
            # Look for JSON data with comments
            json_patterns = [
                r'"comments":\[(.*?)\]',
                r'"commentList":\[(.*?)\]',
                r'"replies":\[(.*?)\]'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, page_content, re.DOTALL)
                if matches:
                    json_data = matches[0]
                    # Look for comment text in JSON
                    text_matches = re.findall(r'"text":"([^"]+)"', json_data)
                    for i, text in enumerate(text_matches):
                        if len(text) > 5:
                            comments.append({
                                "text": text,
                                "author": f"user_{i}",
                                "likes": 0,
                                "timestamp": datetime.now().isoformat(),
                                "source": "json_extraction"
                            })
                    break
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from JSON: {e}")
            return []

    async def _extract_comments_from_response(self, data):
        """Extract comments from network response"""
        comments = []
        
        try:
            # Look for comments in response data
            comment_sources = [
                data.get('comments', []),
                data.get('commentList', []),
                data.get('replies', []),
                data.get('data', {}).get('comments', []),
                data.get('data', {}).get('commentList', [])
            ]
            
            for comment_list in comment_sources:
                if isinstance(comment_list, list) and comment_list:
                    for comment in comment_list:
                        if isinstance(comment, dict):
                            text = comment.get('text', '') or comment.get('content', '')
                            if text and len(text) > 5:
                                comments.append({
                                    "text": text,
                                    "author": comment.get('author', {}).get('nickname', 'Unknown'),
                                    "likes": comment.get('digg_count', 0),
                                    "timestamp": datetime.now().isoformat(),
                                    "source": "network_response"
                                })
                    break
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from response: {e}")
            return []

    def _parse_metric(self, text: str) -> int:
        """Parse metric text to integer"""
        text = text.replace(',', '').strip().lower()
        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        else:
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

async def main():
    """Main execution"""
    print("💬 CUSTOM COMMENT SCRAPER - PROFESSIONAL SOLUTION")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"🔧 Method: Custom advanced browser automation")
    print(f"👁️ Headless: False (visible browser)")
    print()
    
    # Scrape comments with custom methods
    async with CustomCommentScraper(headless=False, debug=True) as scraper:
        comments_data = await scraper.scrape_comments_custom(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"custom_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 CUSTOM COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted with custom methods!")
        print(f"💬 Method: {comments_data.get('method', 'N/A')}")
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
            print("⚠️ No comments found")
    else:
        print("❌ Custom comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
