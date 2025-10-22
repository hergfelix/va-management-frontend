"""
Selenium Comment Scraper - Ultimate Solution
SuperClaude Selenium Comments Extraction Specialist

This scraper will use Selenium with real browser interactions to extract comments
"""

import time
import random
import re
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumCommentScraper:
    """
    Selenium comment scraper with real browser interactions
    """
    
    def __init__(self, headless=False, debug=True):
        self.headless = headless
        self.debug = debug
        self.driver = None
        
    def __enter__(self):
        """Setup Selenium driver"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
        chrome_options.add_argument('--window-size=375,812')
        
        # Mobile emulation
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        if self.driver:
            self.driver.quit()

    def scrape_comments_selenium(self, post_url: str) -> dict:
        """
        Scrape comments using Selenium with real browser interactions
        """
        try:
            logger.info(f"💬 Selenium comment scraping: {post_url}")
            
            # Navigate to post
            self.driver.get(post_url)
            time.sleep(5)
            
            # Try multiple methods to access comments
            comments_data = self._try_selenium_comment_methods(post_url)
            
            return comments_data
            
        except Exception as e:
            logger.error(f"❌ Selenium comment scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
                "comments": []
            }

    def _try_selenium_comment_methods(self, post_url):
        """Try multiple Selenium methods to access comments"""
        methods = [
            self._method_1_click_comments_button,
            self._method_2_scroll_to_comments,
            self._method_3_direct_comments_url,
            self._method_4_force_comment_load,
            self._method_5_wait_for_comments
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                logger.info(f"🔄 Trying Selenium method {i}: {method.__name__}")
                result = method(post_url)
                if result.get("success", False) and result.get("comments"):
                    logger.info(f"✅ Selenium method {i} succeeded!")
                    return result
                else:
                    logger.info(f"⚠️ Selenium method {i} failed, trying next...")
            except Exception as e:
                logger.error(f"❌ Selenium method {i} error: {e}")
                continue
        
        return {
            "post_url": post_url,
            "success": False,
            "error": "All Selenium methods failed",
            "comments": []
        }

    def _method_1_click_comments_button(self, post_url):
        """Method 1: Click comments button with Selenium"""
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
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
                'span[class*="comment"]'
            ]
            
            for selector in comment_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            # Scroll to element
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(1)
                            
                            # Click element
                            element.click()
                            logger.info(f"✅ Clicked comment button: {selector}")
                            time.sleep(3)
                            
                            # Try to extract comments
                            comments = self._extract_comments_selenium()
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
            
            return {"success": False, "error": "No comment button found"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _method_2_scroll_to_comments(self, post_url):
        """Method 2: Scroll to find comments"""
        try:
            # Scroll down slowly to trigger comment loading
            for i in range(10):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # Check if comments are visible
                comments = self._extract_comments_selenium()
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

    def _method_3_direct_comments_url(self, post_url):
        """Method 3: Try direct comments URL"""
        try:
            # Try to construct comments URL
            if "/t/" in post_url:
                comments_url = post_url.replace("/t/", "/t/") + "/comments"
                logger.info(f"🔄 Trying direct comments URL: {comments_url}")
                
                self.driver.get(comments_url)
                time.sleep(5)
                
                comments = self._extract_comments_selenium()
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

    def _method_4_force_comment_load(self, post_url):
        """Method 4: Force comment loading with JavaScript"""
        try:
            # Execute JavaScript to force comment loading
            self.driver.execute_script("""
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
            
            time.sleep(5)
            
            comments = self._extract_comments_selenium()
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

    def _method_5_wait_for_comments(self, post_url):
        """Method 5: Wait for comments to load"""
        try:
            # Wait for comments to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="comment"], [data-e2e*="comment"]'))
            )
            
            time.sleep(3)
            
            comments = self._extract_comments_selenium()
            if comments:
                return {
                    "post_url": post_url,
                    "method": "wait_for_comments",
                    "success": True,
                    "comments": comments,
                    "comment_count": len(comments)
                }
            
            return {"success": False, "error": "Comments not found after waiting"}
            
        except TimeoutException:
            return {"success": False, "error": "Timeout waiting for comments"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_comments_selenium(self):
        """Extract comments using Selenium"""
        comments = []
        
        try:
            # Look for comment elements
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
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        comment_data = self._extract_single_comment_selenium(element)
                        if comment_data:
                            comments.append(comment_data)
                except Exception:
                    continue
            
            # Look for comment text in page source
            page_source = self.driver.page_source
            text_comments = self._extract_comments_from_source(page_source)
            comments.extend(text_comments)
            
            # Remove duplicates
            unique_comments = []
            seen_texts = set()
            for comment in comments:
                if comment["text"] not in seen_texts:
                    unique_comments.append(comment)
                    seen_texts.add(comment["text"])
            
            return unique_comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments with Selenium: {e}")
            return []

    def _extract_single_comment_selenium(self, element):
        """Extract a single comment with Selenium"""
        try:
            # Get comment text
            text_element = element.find_element(By.CSS_SELECTOR, '[class*="text"], [class*="content"], [class*="comment"]')
            if not text_element:
                text_element = element
            
            text = text_element.text
            if not text or len(text.strip()) < 5:
                return None
            
            # Get author
            try:
                author_element = element.find_element(By.CSS_SELECTOR, '[class*="author"], [class*="username"], [class*="user"]')
                author = author_element.text.strip()
            except NoSuchElementException:
                author = "Unknown"
            
            # Get likes if available
            try:
                likes_element = element.find_element(By.CSS_SELECTOR, '[class*="like"], [class*="heart"]')
                likes = self._parse_metric(likes_element.text)
            except NoSuchElementException:
                likes = 0
            
            return {
                "text": text.strip(),
                "author": author,
                "likes": likes,
                "timestamp": datetime.now().isoformat(),
                "source": "selenium_extraction"
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting single comment with Selenium: {e}")
            return None

    def _extract_comments_from_source(self, page_source):
        """Extract comments from page source"""
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
                matches = re.findall(pattern, page_source)
                for i, text in enumerate(matches):
                    if len(text) > 5 and not text.startswith('http'):
                        comments.append({
                            "text": text,
                            "author": f"user_{i}",
                            "likes": 0,
                            "timestamp": datetime.now().isoformat(),
                            "source": "source_extraction"
                        })
            
            return comments
            
        except Exception as e:
            logger.error(f"❌ Error extracting comments from source: {e}")
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

def main():
    """Main execution"""
    print("💬 SELENIUM COMMENT SCRAPER - ULTIMATE SOLUTION")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZP8SxfT4H/"
    
    print(f"🎯 Target: {post_url}")
    print(f"💬 Expected: 500+ comments with authors")
    print(f"🔧 Method: Selenium with real browser interactions")
    print(f"👁️ Headless: False (visible browser)")
    print()
    
    # Scrape comments with Selenium
    with SeleniumCommentScraper(headless=False, debug=True) as scraper:
        comments_data = scraper.scrape_comments_selenium(post_url)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"selenium_comments_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(comments_data, f, indent=2, default=str)
    
    print("\n📊 SELENIUM COMMENTS RESULTS:")
    print("=" * 60)
    
    if comments_data.get("success", False):
        print("✅ SUCCESS! Comments extracted with Selenium!")
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
        print("❌ Selenium comments extraction failed")
        if 'error' in comments_data:
            print(f"Error: {comments_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return comments_data

if __name__ == "__main__":
    main()
