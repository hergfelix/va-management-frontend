"""
Advanced Comments Scraper
SuperClaude Advanced Comments Extraction Specialist

This scraper will wait for comments to load and extract them properly
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

class AdvancedCommentsScraper:
    """
    Advanced comments scraper that waits for comments to load
    """
    
    def __init__(self, headless=True, debug=True):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Mobile browser setup"""
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
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

    async def scrape_comments_with_wait(self, post_url: str) -> dict:
        """
        Scrape comments with proper waiting for dynamic content
        """
        try:
            # Create mobile context
            context = await self.browser.new_context(
                viewport={'width': 375, 'height': 812},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            page = await context.new_page()
            
            # Mobile stealth
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
            """)
            
            logger.info(f"💬 Advanced comments scraping: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Try multiple methods to access comments
            comments_data = await self._try_multiple_comment_methods(page, post_url)
            
            await context.close()
            return comments_data
            
        except Exception as e:
            logger.error(f"❌ Advanced comments scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
                "comments": []
            }

    async def _try_multiple_comment_methods(self, page, post_url):
        """Try multiple methods to access comments"""
        methods = [
            self._method_1_click_comments_button,
            self._method_2_scroll_to_comments,
            self._method_3_direct_url,
            self._method_4_wait_for_dynamic_load
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                logger.info(f"🔄 Trying method {i}: {method.__name__}")
                result = await method(page, post_url)
                if result.get("success", False) and result.get("comments"):
                    logger.info(f"✅ Method {i} succeeded!")
                    return result
                else:
                    logger.info(f"⚠️ Method {i} failed, trying next...")
            except Exception as e:
                logger.error(f"❌ Method {i} error: {e}")
                continue
        
        return {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat(),
            "success": False,
            "error": "All methods failed",
            "comments": []
        }

    async def _method_1_click_comments_button(self, page, post_url):
        """Method 1: Click comments button"""
        try:
            # Look for comments button
            comments_selectors = [
                '[data-e2e="comment-count"]',
                '[data-e2e="comment-button"]',
                '[class*="comment"]',
                'button[aria-label*="comment"]',
                'div[class*="comment"]'
            ]
            
            for selector in comments_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            await element.click()
                            logger.info(f"✅ Clicked comments button: {selector}")
                            await asyncio.sleep(3)
                            
                            # Try to extract comments after clicking
                            comments = await self._extract_comments_from_page(page)
                            if comments:
                                return {
                                    "post_url": post_url,
                                    "method": "click_comments_button",
                                    "success": True,
                                    "comments": comments,
                                    "comment_count": len(comments)
                                }
                except Exception:
                    continue
            
            return {"success": False, "error": "No comments button found"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _method_2_scroll_to_comments(self, page, post_url):
        """Method 2: Scroll to find comments"""
        try:
            # Scroll down to find comments
            for i in range(5):
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1)
                
                # Check if comments are visible
                comments = await self._extract_comments_from_page(page)
                if comments:
                    return {
                        "post_url": post_url,
                        "method": "scroll_to_comments",
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments)
                    }
            
            return {"success": False, "error": "Comments not found after scrolling"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _method_3_direct_url(self, page, post_url):
        """Method 3: Try direct comments URL"""
        try:
            # Try to construct comments URL
            if "/t/" in post_url:
                comments_url = post_url.replace("/t/", "/t/") + "/comments"
                logger.info(f"🔄 Trying comments URL: {comments_url}")
                
                await page.goto(comments_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(3)
                
                comments = await self._extract_comments_from_page(page)
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

    async def _method_4_wait_for_dynamic_load(self, page, post_url):
        """Method 4: Wait for dynamic content to load"""
        try:
            # Wait for dynamic content
            await asyncio.sleep(5)
            
            # Try to trigger comment loading
            await page.evaluate("""
                // Try to trigger comment loading
                const commentElements = document.querySelectorAll('[class*="comment"], [data-e2e*="comment"]');
                commentElements.forEach(el => {
                    if (el.click) el.click();
                });
            """)
            
            await asyncio.sleep(3)
            
            comments = await self._extract_comments_from_page(page)
            if comments:
                return {
                    "post_url": post_url,
                    "method": "wait_for_dynamic_load",
                    "success": True,
                    "comments": comments,
                    "comment_count": len(comments)
                }
            
            return {"success": False, "error": "Dynamic load failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _extract_comments_from_page(self, page):
        """Extract comments from the current page"""
        comments = []
        
        try:
            # Get page content
            page_content = await page.content()
            
            # Look for comment elements
            comment_selectors = [
                '[class*="comment"]',
                '[class*="Comment"]',
                '[data-e2e*="comment"]',
                'div[class*="comment-item"]',
                'div[class*="comment-content"]',
                'span[class*="comment"]'
            ]
            
            for selector in comment_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text and len(text.strip()) > 5:
                            comments.append({
                                "text": text.strip(),
                                "selector": selector,
                                "timestamp": datetime.now().isoformat()
                            })
                except Exception:
                    continue
            
            # Look for comment text in page content
            text_patterns = [
                r'"text":"([^"]+)"',
                r'"content":"([^"]+)"',
                r'"comment":"([^"]+)"'
            ]
            
            for pattern in text_patterns:
                matches = re.findall(pattern, page_content)
                for i, text in enumerate(matches):
                    if len(text) > 5 and not text.startswith('http'):
                        comments.append({
                            "text": text,
                            "source": "json_pattern",
                            "timestamp": datetime.now().isoformat()
                        })
            
            # Remove duplicates
            unique_comments = []
            seen_texts = set()
            for comment in comments:
                if comment["text"] not in seen_texts:
                    unique_comments.append(comment)
                    seen_texts.add(comment["text"])
            
            return unique_comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments: {e}")
            return []

async def main():
    """Main execution"""
    print("💬 ADVANCED COMMENTS SCRAPER")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments")
    print(f"🔄 Methods: 4 different approaches")
    print()
    
    # Scrape comments with advanced methods
    async with AdvancedCommentsScraper(headless=True, debug=True) as scraper:
        comments_data = await scraper.scrape_comments_with_wait(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"advanced_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 ADVANCED COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted!")
        print(f"💬 Method: {comments_data.get('method', 'N/A')}")
        print(f"💬 Comments Found: {comments_data.get('comment_count', 0)}")
        
        comments = comments_data.get('comments', [])
        if comments:
            print(f"\n💬 SAMPLE COMMENTS:")
            for i, comment in enumerate(comments[:10], 1):
                text = comment.get('text', 'N/A')[:80] + "..." if len(comment.get('text', '')) > 80 else comment.get('text', 'N/A')
                print(f"   {i:2d}. {text}")
    else:
        print("❌ Comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
