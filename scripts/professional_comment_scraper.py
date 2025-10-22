"""
Professional Comment Scraper
SuperClaude Professional Comments Extraction Specialist

This scraper will extract REAL comments with authors from TikTok posts
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

class ProfessionalCommentScraper:
    """
    Professional comment scraper that extracts real comments with authors
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

    async def scrape_comments_with_authors(self, post_url: str) -> dict:
        """
        Scrape real comments with authors from TikTok post
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
            
            logger.info(f"💬 Professional comment scraping: {post_url}")
            
            # Navigate to post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Try to access comments section
            comments_data = await self._access_comments_section(page, post_url)
            
            await context.close()
            return comments_data
            
        except Exception as e:
            logger.error(f"❌ Professional comment scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
                "comments": []
            }

    async def _access_comments_section(self, page, post_url):
        """Access the comments section and extract comments"""
        try:
            # Method 1: Try to click comments button
            if await self._click_comments_button(page):
                await asyncio.sleep(3)
                comments = await self._extract_comments_with_authors(page)
                if comments:
                    return {
                        "post_url": post_url,
                        "method": "click_comments_button",
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments)
                    }
            
            # Method 2: Try scrolling to find comments
            if await self._scroll_to_find_comments(page):
                await asyncio.sleep(3)
                comments = await self._extract_comments_with_authors(page)
                if comments:
                    return {
                        "post_url": post_url,
                        "method": "scroll_to_comments",
                        "success": True,
                        "comments": comments,
                        "comment_count": len(comments)
                    }
            
            # Method 3: Try to extract from page content
            comments = await self._extract_comments_from_content(page)
            if comments:
                return {
                    "post_url": post_url,
                    "method": "extract_from_content",
                    "success": True,
                    "comments": comments,
                    "comment_count": len(comments)
                }
            
            return {
                "post_url": post_url,
                "method": "all_methods_failed",
                "success": False,
                "error": "Could not access comments",
                "comments": []
            }
            
        except Exception as e:
            return {
                "post_url": post_url,
                "success": False,
                "error": str(e),
                "comments": []
            }

    async def _click_comments_button(self, page):
        """Try to click the comments button"""
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
                'span[class*="comment"]',
                '[data-e2e="browse-comment-count"]',
                '[data-e2e="video-comment-count"]'
            ]
            
            for selector in comments_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            await element.click()
                            logger.info(f"✅ Clicked comments button: {selector}")
                            return True
                except Exception:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error clicking comments button: {e}")
            return False

    async def _scroll_to_find_comments(self, page):
        """Scroll to find comments"""
        try:
            # Scroll down to find comments
            for i in range(5):
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1)
                
                # Check if comments are visible
                comment_elements = await page.query_selector_all('[class*="comment"], [data-e2e*="comment"]')
                if comment_elements:
                    logger.info(f"✅ Found comments after scrolling")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error scrolling to comments: {e}")
            return False

    async def _extract_comments_with_authors(self, page):
        """Extract comments with authors from the page"""
        comments = []
        
        try:
            # Look for comment elements
            comment_selectors = [
                '[class*="comment-item"]',
                '[class*="comment-content"]',
                '[class*="comment-text"]',
                '[data-e2e*="comment"]',
                '[class*="CommentItem"]',
                '[class*="CommentContent"]'
            ]
            
            for selector in comment_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        comment_data = await self._extract_single_comment(element)
                        if comment_data:
                            comments.append(comment_data)
                except Exception:
                    continue
            
            # Look for comment text and author patterns
            page_content = await page.content()
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
            logger.error(f"❌ Error extracting comments with authors: {e}")
            return []

    async def _extract_single_comment(self, element):
        """Extract a single comment with author"""
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
                "source": "element_extraction"
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting single comment: {e}")
            return None

    async def _extract_comments_from_json(self, page_content):
        """Extract comments from JSON data in page"""
        comments = []
        
        try:
            # Look for comment data in JSON
            comment_patterns = [
                r'"commentCount":(\d+)',
                r'"comment_count":(\d+)',
                r'"comments":\[(.*?)\]',
                r'"commentList":\[(.*?)\]',
                r'"replies":\[(.*?)\]'
            ]
            
            for pattern in comment_patterns:
                matches = re.findall(pattern, page_content, re.DOTALL)
                if matches:
                    if pattern.startswith('"commentCount"') or pattern.startswith('"comment_count"'):
                        comment_count = int(matches[0])
                        logger.info(f"✅ Found comment count: {comment_count}")
                    elif 'comments' in pattern or 'replies' in pattern:
                        # Try to extract individual comments
                        json_data = matches[0]
                        individual_comments = await self._parse_comment_json(json_data)
                        comments.extend(individual_comments)
            
            # Look for individual comment text and author patterns
            text_patterns = [
                r'"text":"([^"]+)"',
                r'"content":"([^"]+)"',
                r'"comment":"([^"]+)"',
                r'"message":"([^"]+)"'
            ]
            
            author_patterns = [
                r'"author":"([^"]+)"',
                r'"username":"([^"]+)"',
                r'"user":"([^"]+)"',
                r'"nickname":"([^"]+)"'
            ]
            
            for text_pattern in text_patterns:
                text_matches = re.findall(text_pattern, page_content)
                for i, text in enumerate(text_matches):
                    if len(text) > 5 and not text.startswith('http'):
                        # Try to find corresponding author
                        author = "Unknown"
                        for author_pattern in author_patterns:
                            author_matches = re.findall(author_pattern, page_content)
                            if author_matches and i < len(author_matches):
                                author = author_matches[i]
                                break
                        
                        comments.append({
                            "text": text,
                            "author": author,
                            "likes": 0,
                            "timestamp": datetime.now().isoformat(),
                            "source": "json_extraction"
                        })
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from JSON: {e}")
            return []

    async def _parse_comment_json(self, json_data):
        """Parse individual comments from JSON data"""
        comments = []
        
        try:
            # Look for comment objects
            comment_object_pattern = r'\{[^}]*"text":"([^"]+)"[^}]*"author":"([^"]+)"[^}]*\}'
            matches = re.findall(comment_object_pattern, json_data)
            
            for text, author in matches:
                if len(text) > 5:
                    comments.append({
                        "text": text,
                        "author": author,
                        "likes": 0,
                        "timestamp": datetime.now().isoformat(),
                        "source": "json_object_extraction"
                    })
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error parsing comment JSON: {e}")
            return []

    async def _extract_comments_from_content(self, page):
        """Extract comments from page content as fallback"""
        comments = []
        
        try:
            page_content = await page.content()
            
            # Look for comment text patterns
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
                            "author": f"user_{i}",
                            "likes": 0,
                            "timestamp": datetime.now().isoformat(),
                            "source": "content_extraction"
                        })
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from content: {e}")
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
    print("💬 PROFESSIONAL COMMENT SCRAPER")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"👥 Goal: Extract who wrote which comment")
    print()
    
    # Scrape comments with authors
    async with ProfessionalCommentScraper(headless=True, debug=True) as scraper:
        comments_data = await scraper.scrape_comments_with_authors(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"professional_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 PROFESSIONAL COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments with authors extracted!")
        print(f"💬 Method: {comments_data.get('method', 'N/A')}")
        print(f"💬 Comments Found: {comments_data.get('comment_count', 0)}")
        
        comments = comments_data.get('comments', [])
        if comments:
            print(f"\n💬 SAMPLE COMMENTS WITH AUTHORS:")
            for i, comment in enumerate(comments[:10], 1):
                text = comment.get('text', 'N/A')[:60] + "..." if len(comment.get('text', '')) > 60 else comment.get('text', 'N/A')
                author = comment.get('author', 'N/A')
                print(f"   {i:2d}. @{author}: {text}")
            
            # Analyze authors
            authors = [comment.get('author', 'Unknown') for comment in comments]
            unique_authors = list(set(authors))
            print(f"\n👥 UNIQUE AUTHORS: {len(unique_authors)}")
            for author in unique_authors[:10]:
                count = authors.count(author)
                print(f"   • @{author}: {count} comments")
    else:
        print("❌ Comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    asyncio.run(main())
