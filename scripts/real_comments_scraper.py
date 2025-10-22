"""
REAL Comments Scraper - No Fake Data!
SuperClaude Comments Extraction Specialist

This scraper will extract REAL comments from TikTok posts
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

class RealCommentsScraper:
    """
    REAL comments scraper - extracts actual comments from TikTok
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

    async def scrape_real_comments(self, post_url: str) -> dict:
        """
        Scrape REAL comments from TikTok post
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
            
            logger.info(f"💬 Scraping REAL comments from: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Try to find and click comments button
            await self._click_comments_button(page)
            
            # Wait for comments to load
            await asyncio.sleep(5)
            
            # Debug save
            if self.debug:
                page_content = await page.content()
                with open(f'real_comments_debug_{int(time.time())}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"💾 Debug saved: real_comments_debug_{int(time.time())}.html")
            
            # Extract real comments
            comments_data = await self._extract_real_comments(page, post_url)
            
            await context.close()
            return comments_data
            
        except Exception as e:
            logger.error(f"❌ Real comments scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
                "real_comments": []
            }

    async def _click_comments_button(self, page):
        """Try to find and click the comments button"""
        try:
            # Look for comments button with various selectors
            comments_selectors = [
                '[data-e2e="comment-count"]',
                '[data-e2e="comment-button"]',
                '[class*="comment"]',
                '[class*="Comment"]',
                'button[aria-label*="comment"]',
                'button[aria-label*="Comment"]',
                'div[class*="comment"]',
                'span[class*="comment"]'
            ]
            
            for selector in comments_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        # Check if element is clickable
                        is_visible = await element.is_visible()
                        if is_visible:
                            await element.click()
                            logger.info(f"✅ Clicked comments button: {selector}")
                            await asyncio.sleep(2)
                            return True
                except Exception:
                    continue
            
            # Try scrolling to find comments
            logger.info("🔄 Scrolling to find comments...")
            for i in range(3):
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1)
            
            # Try clicking on any element that might be comments
            try:
                # Look for any clickable element that might be comments
                clickable_elements = await page.query_selector_all('button, div, span')
                for element in clickable_elements:
                    text = await element.text_content()
                    if text and ('comment' in text.lower() or '💬' in text):
                        await element.click()
                        logger.info(f"✅ Clicked element with text: {text}")
                        await asyncio.sleep(2)
                        return True
            except Exception:
                pass
            
            logger.warning("⚠️ Could not find comments button")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error clicking comments button: {e}")
            return False

    async def _extract_real_comments(self, page, post_url):
        """Extract REAL comments from the page"""
        data = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat(),
            "success": True,
            "real_comments": []
        }
        
        try:
            # Get page content
            page_content = await page.content()
            
            # Method 1: Look for comment count in page
            comment_count = await self._extract_comment_count(page_content)
            data["comment_count"] = comment_count
            
            # Method 2: Look for actual comment elements
            real_comments = await self._find_comment_elements(page)
            data["real_comments"] = real_comments
            data["extracted_comments_count"] = len(real_comments)
            
            # Method 3: Look for comment data in JSON
            json_comments = await self._extract_comments_from_json(page_content)
            if json_comments:
                data["json_comments"] = json_comments
                data["json_comments_count"] = len(json_comments)
            
            logger.info(f"✅ Found {comment_count} total comments")
            logger.info(f"✅ Extracted {len(real_comments)} real comments")
            if json_comments:
                logger.info(f"✅ Found {len(json_comments)} JSON comments")
            
        except Exception as e:
            logger.error(f"❌ Error extracting real comments: {e}")
            data["extraction_error"] = str(e)
            data["success"] = False
        
        return data

    async def _extract_comment_count(self, page_content):
        """Extract comment count from page content"""
        try:
            # Look for comment count patterns
            patterns = [
                r'"commentCount":(\d+)',
                r'"comment_count":(\d+)',
                r'"comments":(\d+)',
                r'(\d+)\s*comments?',
                r'comments?\s*(\d+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                if matches:
                    count = int(matches[0])
                    logger.info(f"✅ Found comment count: {count}")
                    return count
            
            logger.warning("⚠️ Could not find comment count")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Error extracting comment count: {e}")
            return 0

    async def _find_comment_elements(self, page):
        """Find actual comment elements on the page"""
        comments = []
        
        try:
            # Look for comment elements
            comment_selectors = [
                '[class*="comment"]',
                '[class*="Comment"]',
                '[data-e2e*="comment"]',
                'div[class*="comment-item"]',
                'div[class*="comment-content"]'
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
            
            # Remove duplicates
            unique_comments = []
            seen_texts = set()
            for comment in comments:
                if comment["text"] not in seen_texts:
                    unique_comments.append(comment)
                    seen_texts.add(comment["text"])
            
            return unique_comments
            
        except Exception as e:
            logger.error(f"❌ Error finding comment elements: {e}")
            return []

    async def _extract_comments_from_json(self, page_content):
        """Extract comments from JSON data in page"""
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
                    logger.info(f"✅ Found JSON comments data")
                    # Try to parse JSON comments
                    json_data = matches[0]
                    # Look for comment text in JSON
                    text_matches = re.findall(r'"text":"([^"]+)"', json_data)
                    for i, text in enumerate(text_matches):
                        if len(text) > 5:
                            comments.append({
                                "text": text,
                                "source": "json",
                                "index": i
                            })
                    break
            
        except Exception as e:
            logger.error(f"❌ Error extracting JSON comments: {e}")
        
        return comments

async def main():
    """Main execution"""
    print("💬 REAL COMMENTS SCRAPER - NO FAKE DATA!")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ REAL comments")
    print(f"❌ Previous: Fake 50 comments")
    print()
    
    # Scrape real comments
    async with RealCommentsScraper(headless=True, debug=True) as scraper:
        comments_data = await scraper.scrape_real_comments(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"real_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 REAL COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Real comments extracted!")
        print(f"💬 Total Comment Count: {comments_data.get('comment_count', 0)}")
        print(f"💬 Extracted Comments: {comments_data.get('extracted_comments_count', 0)}")
        
        if comments_data.get('json_comments'):
            print(f"💬 JSON Comments: {comments_data.get('json_comments_count', 0)}")
        
        # Show sample real comments
        real_comments = comments_data.get('real_comments', [])
        if real_comments:
            print(f"\n💬 SAMPLE REAL COMMENTS:")
            for i, comment in enumerate(real_comments[:5], 1):
                print(f"   {i}. {comment.get('text', 'N/A')[:80]}...")
        
        json_comments = comments_data.get('json_comments', [])
        if json_comments:
            print(f"\n💬 SAMPLE JSON COMMENTS:")
            for i, comment in enumerate(json_comments[:5], 1):
                print(f"   {i}. {comment.get('text', 'N/A')[:80]}...")
    else:
        print("❌ Comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
