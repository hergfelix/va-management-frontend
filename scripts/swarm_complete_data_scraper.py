"""
SWARM MODE: Complete Data Scraper for 100 Videos
SuperClaude SWARM TikTok Scraper

6 Parallel Agents testing different methods to extract COMPLETE data
"""

import asyncio
import pandas as pd
import time
import re
import json
import random
from datetime import datetime
from playwright.async_api import async_playwright
import logging
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import aiofiles

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SwarmCompleteDataScraper:
    """
    SWARM MODE: 6 parallel agents testing different scraping methods
    """
    
    def __init__(self, headless=True, debug=False):
        self.headless = headless
        self.debug = debug
        self.results = []
        self.success_count = 0
        self.failure_count = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.playwright:
            await self.playwright.stop()

    async def agent_1_mobile_optimized(self, urls: list) -> list:
        """
        Agent 1: Mobile-optimized scraper with iPhone user-agent
        """
        logger.info("📱 Agent 1: Mobile-optimized scraper starting...")
        results = []
        
        browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        try:
            for i, url in enumerate(urls, 1):
                try:
                    page = await browser.new_page()
                    
                    # Mobile user agent
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
                    })
                    
                    # Mobile viewport
                    await page.set_viewport_size({"width": 375, "height": 667})
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    # Extract data
                    data = await self._extract_complete_data(page, url, "mobile_optimized")
                    results.append(data)
                    
                    await page.close()
                    logger.info(f"📱 Agent 1: {i}/{len(urls)} - {url} - Success")
                    
                except Exception as e:
                    logger.error(f"📱 Agent 1: {i}/{len(urls)} - {url} - Failed: {e}")
                    results.append(self._create_failed_result(url, "mobile_optimized", str(e)))
                
                # Rate limiting
                await asyncio.sleep(2)
                
        finally:
            await browser.close()
        
        logger.info(f"📱 Agent 1: Completed {len(results)} URLs")
        return results

    async def agent_2_desktop_optimized(self, urls: list) -> list:
        """
        Agent 2: Desktop-optimized scraper with Chrome user-agent
        """
        logger.info("🖥️ Agent 2: Desktop-optimized scraper starting...")
        results = []
        
        browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        try:
            for i, url in enumerate(urls, 1):
                try:
                    page = await browser.new_page()
                    
                    # Desktop user agent
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    })
                    
                    # Desktop viewport
                    await page.set_viewport_size({"width": 1920, "height": 1080})
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    # Extract data
                    data = await self._extract_complete_data(page, url, "desktop_optimized")
                    results.append(data)
                    
                    await page.close()
                    logger.info(f"🖥️ Agent 2: {i}/{len(urls)} - {url} - Success")
                    
                except Exception as e:
                    logger.error(f"🖥️ Agent 2: {i}/{len(urls)} - {url} - Failed: {e}")
                    results.append(self._create_failed_result(url, "desktop_optimized", str(e)))
                
                # Rate limiting
                await asyncio.sleep(2)
                
        finally:
            await browser.close()
        
        logger.info(f"🖥️ Agent 2: Completed {len(results)} URLs")
        return results

    async def agent_3_stealth_mode(self, urls: list) -> list:
        """
        Agent 3: Stealth mode with anti-detection measures
        """
        logger.info("🥷 Agent 3: Stealth mode scraper starting...")
        results = []
        
        browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        try:
            for i, url in enumerate(urls, 1):
                try:
                    page = await browser.new_page()
                    
                    # Random user agent
                    user_agents = [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    ]
                    
                    await page.set_extra_http_headers({
                        'User-Agent': random.choice(user_agents)
                    })
                    
                    # Random viewport
                    viewports = [
                        {"width": 1920, "height": 1080},
                        {"width": 1366, "height": 768},
                        {"width": 1440, "height": 900}
                    ]
                    
                    await page.set_viewport_size(random.choice(viewports))
                    
                    # Add random delay
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(random.uniform(2, 5))
                    
                    # Extract data
                    data = await self._extract_complete_data(page, url, "stealth_mode")
                    results.append(data)
                    
                    await page.close()
                    logger.info(f"🥷 Agent 3: {i}/{len(urls)} - {url} - Success")
                    
                except Exception as e:
                    logger.error(f"🥷 Agent 3: {i}/{len(urls)} - {url} - Failed: {e}")
                    results.append(self._create_failed_result(url, "stealth_mode", str(e)))
                
                # Random rate limiting
                await asyncio.sleep(random.uniform(1, 4))
                
        finally:
            await browser.close()
        
        logger.info(f"🥷 Agent 3: Completed {len(results)} URLs")
        return results

    async def agent_4_api_scraper(self, urls: list) -> list:
        """
        Agent 4: API-based scraper using TikTok's internal APIs
        """
        logger.info("🔌 Agent 4: API scraper starting...")
        results = []
        
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(urls, 1):
                try:
                    # Extract video ID from URL
                    video_id = self._extract_video_id(url)
                    if not video_id:
                        results.append(self._create_failed_result(url, "api_scraper", "Could not extract video ID"))
                        continue
                    
                    # Try multiple API endpoints
                    api_endpoints = [
                        f"https://www.tiktok.com/api/item/detail/?itemId={video_id}",
                        f"https://www.tiktok.com/api/video/item/?itemId={video_id}",
                        f"https://www.tiktok.com/api/aweme/v1/feed/?aweme_id={video_id}"
                    ]
                    
                    data = None
                    for endpoint in api_endpoints:
                        try:
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                'Referer': 'https://www.tiktok.com/',
                                'Accept': 'application/json, text/plain, */*'
                            }
                            
                            async with session.get(endpoint, headers=headers, timeout=30) as response:
                                if response.status == 200:
                                    json_data = await response.json()
                                    data = await self._parse_api_response(json_data, url, "api_scraper")
                                    if data and data.get('views', 0) > 0:
                                        break
                        except Exception as e:
                            logger.debug(f"🔌 Agent 4: API endpoint failed: {e}")
                            continue
                    
                    if data:
                        results.append(data)
                        logger.info(f"🔌 Agent 4: {i}/{len(urls)} - {url} - Success")
                    else:
                        results.append(self._create_failed_result(url, "api_scraper", "All API endpoints failed"))
                        logger.error(f"🔌 Agent 4: {i}/{len(urls)} - {url} - Failed")
                    
                except Exception as e:
                    logger.error(f"🔌 Agent 4: {i}/{len(urls)} - {url} - Failed: {e}")
                    results.append(self._create_failed_result(url, "api_scraper", str(e)))
                
                # Rate limiting
                await asyncio.sleep(1)
        
        logger.info(f"🔌 Agent 4: Completed {len(results)} URLs")
        return results

    async def agent_5_hybrid_scraper(self, urls: list) -> list:
        """
        Agent 5: Hybrid scraper combining multiple methods
        """
        logger.info("🔄 Agent 5: Hybrid scraper starting...")
        results = []
        
        browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        try:
            for i, url in enumerate(urls, 1):
                try:
                    page = await browser.new_page()
                    
                    # Try mobile first
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
                    })
                    
                    await page.set_viewport_size({"width": 375, "height": 667})
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    # Extract data with multiple methods
                    data = await self._extract_complete_data_hybrid(page, url, "hybrid_scraper")
                    results.append(data)
                    
                    await page.close()
                    logger.info(f"🔄 Agent 5: {i}/{len(urls)} - {url} - Success")
                    
                except Exception as e:
                    logger.error(f"🔄 Agent 5: {i}/{len(urls)} - {url} - Failed: {e}")
                    results.append(self._create_failed_result(url, "hybrid_scraper", str(e)))
                
                # Rate limiting
                await asyncio.sleep(2)
                
        finally:
            await browser.close()
        
        logger.info(f"🔄 Agent 5: Completed {len(results)} URLs")
        return results

    async def agent_6_advanced_scraper(self, urls: list) -> list:
        """
        Agent 6: Advanced scraper with network interception
        """
        logger.info("🚀 Agent 6: Advanced scraper starting...")
        results = []
        
        browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        try:
            for i, url in enumerate(urls, 1):
                try:
                    page = await browser.new_page()
                    
                    # Set up network interception
                    await page.route("**/*", self._handle_route)
                    
                    # Desktop user agent
                    await page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    })
                    
                    await page.set_viewport_size({"width": 1920, "height": 1080})
                    
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await page.wait_for_timeout(3000)
                    
                    # Extract data
                    data = await self._extract_complete_data(page, url, "advanced_scraper")
                    results.append(data)
                    
                    await page.close()
                    logger.info(f"🚀 Agent 6: {i}/{len(urls)} - {url} - Success")
                    
                except Exception as e:
                    logger.error(f"🚀 Agent 6: {i}/{len(urls)} - {url} - Failed: {e}")
                    results.append(self._create_failed_result(url, "advanced_scraper", str(e)))
                
                # Rate limiting
                await asyncio.sleep(2)
                
        finally:
            await browser.close()
        
        logger.info(f"🚀 Agent 6: Completed {len(results)} URLs")
        return results

    async def _handle_route(self, route):
        """Handle network requests for advanced scraper"""
        try:
            await route.continue_()
        except Exception:
            pass

    async def _extract_complete_data(self, page, url: str, method: str) -> dict:
        """
        Extract complete data from TikTok page
        """
        try:
            # Get page content
            page_content = await page.content()
            
            # Extract all metrics
            views = await self._extract_views_comprehensive(page, page_content)
            likes = await self._extract_likes_comprehensive(page, page_content)
            comments = await self._extract_comments_comprehensive(page, page_content)
            shares = await self._extract_shares_comprehensive(page, page_content)
            bookmarks = await self._extract_bookmarks_comprehensive(page, page_content)
            
            # Calculate engagement
            engagement = likes + comments + shares + bookmarks
            engagement_rate = (engagement / views * 100) if views > 0 else 0.0
            
            # Extract account details
            account_username = await self._extract_username_comprehensive(page, page_content, url)
            account_followers = await self._extract_followers_comprehensive(page, page_content)
            account_following = await self._extract_following_comprehensive(page, page_content)
            account_posts = await self._extract_posts_comprehensive(page, page_content)
            account_likes = await self._extract_account_likes_comprehensive(page, page_content)
            account_verified = await self._extract_verified_comprehensive(page, page_content)
            
            # Extract content details
            post_description = await self._extract_description_comprehensive(page, page_content)
            hashtags = await self._extract_hashtags_comprehensive(page, page_content)
            mentions = await self._extract_mentions_comprehensive(page, page_content)
            content_length = len(post_description) if post_description else 0
            
            # Extract sound details
            sound_title = await self._extract_sound_title_comprehensive(page, page_content)
            sound_url = await self._extract_sound_url_comprehensive(page, page_content)
            sound_author = await self._extract_sound_author_comprehensive(page, page_content)
            has_sound = bool(sound_url)
            
            # Extract slides
            slides = await self._extract_slides_comprehensive(page, page_content)
            slide_count = len([s for s in slides if s])
            
            # Create result
            result = {
                "post_url": url,
                "creator": "Unknown",  # Will be filled from external data
                "set_id": 0,  # Will be filled from external data
                "va": "Unknown",  # Will be filled from external data
                "type": "Unknown",  # Will be filled from external data
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "bookmarks": bookmarks,
                "engagement": engagement,
                "engagement_rate": round(engagement_rate, 2),
                "account_username": account_username,
                "account_followers": account_followers,
                "account_following": account_following,
                "account_posts": account_posts,
                "account_likes": account_likes,
                "account_verified": account_verified,
                "post_description": post_description,
                "hashtags": hashtags,
                "mentions": mentions,
                "content_length": content_length,
                "sound_title": sound_title,
                "sound_url": sound_url,
                "sound_author": sound_author,
                "has_sound": has_sound,
                "slide_count": slide_count,
                "slide_1": slides[0] if len(slides) > 0 else "",
                "slide_2": slides[1] if len(slides) > 1 else "",
                "slide_3": slides[2] if len(slides) > 2 else "",
                "slide_4": slides[3] if len(slides) > 3 else "",
                "slide_5": slides[4] if len(slides) > 4 else "",
                "slide_6": slides[5] if len(slides) > 5 else "",
                "slide_7": slides[6] if len(slides) > 6 else "",
                "slide_8": slides[7] if len(slides) > 7 else "",
                "slide_9": slides[8] if len(slides) > 8 else "",
                "slide_10": slides[9] if len(slides) > 9 else "",
                "slide_11": slides[10] if len(slides) > 10 else "",
                "slide_12": slides[11] if len(slides) > 11 else "",
                "scraped_at": datetime.now().isoformat(),
                "scraping_method": method,
                "scraping_success": True,
                "data_quality": "Complete" if views > 0 and likes > 0 else "Partial"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting complete data: {e}")
            return self._create_failed_result(url, method, str(e))

    async def _extract_complete_data_hybrid(self, page, url: str, method: str) -> dict:
        """
        Extract complete data using hybrid methods
        """
        # Try multiple extraction methods and combine results
        result = await self._extract_complete_data(page, url, method)
        
        # If basic extraction failed, try alternative methods
        if result.get('views', 0) == 0:
            # Try alternative view extraction
            page_content = await page.content()
            views = await self._extract_views_alternative(page, page_content)
            if views > 0:
                result['views'] = views
                result['data_quality'] = "Hybrid"
        
        return result

    async def _extract_views_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive view extraction"""
        # Method 1: JSON data
        try:
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                return int(playcount_match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="video-views"]',
            'strong[data-e2e="video-views"]',
            'span[data-e2e="video-views"]',
            '[class*="view"] strong',
            '[class*="View"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_views_alternative(self, page, page_content: str) -> int:
        """Alternative view extraction methods"""
        # Look for any large numbers that could be views
        try:
            all_elements = await page.query_selector_all('span, div, strong')
            for element in all_elements:
                text = await element.text_content()
                if text and self._looks_like_views(text):
                    parsed = self._parse_metric(text)
                    if parsed > 100:  # Views should be at least 100
                        return parsed
        except:
            pass
        
        return 0

    async def _extract_likes_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive likes extraction"""
        # Method 1: JSON data
        try:
            like_patterns = [
                r'"diggCount":(\d+)',
                r'"likeCount":(\d+)',
                r'"likes":(\d+)',
                r'"heartCount":(\d+)'
            ]
            
            for pattern in like_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="like-count"]',
            'strong[data-e2e="like-count"]',
            'div[data-e2e="like-count"]',
            'span[data-e2e="like-count"]',
            '[class*="like"] strong',
            '[class*="Like"] strong',
            '[class*="heart"] strong',
            '[class*="Heart"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_comments_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive comments extraction"""
        # Method 1: JSON data
        try:
            comment_patterns = [
                r'"commentCount":(\d+)',
                r'"comments":(\d+)',
                r'"replyCount":(\d+)'
            ]
            
            for pattern in comment_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="comment-count"]',
            'strong[data-e2e="comment-count"]',
            'div[data-e2e="comment-count"]',
            'span[data-e2e="comment-count"]',
            '[class*="comment"] strong',
            '[class*="Comment"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_shares_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive shares extraction"""
        # Method 1: JSON data
        try:
            share_patterns = [
                r'"shareCount":(\d+)',
                r'"shares":(\d+)',
                r'"forwardCount":(\d+)'
            ]
            
            for pattern in share_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="share-count"]',
            'strong[data-e2e="share-count"]',
            'div[data-e2e="share-count"]',
            'span[data-e2e="share-count"]',
            '[class*="share"] strong',
            '[class*="Share"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_bookmarks_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive bookmarks extraction"""
        # Method 1: JSON data
        try:
            bookmark_patterns = [
                r'"collectCount":(\d+)',
                r'"bookmarkCount":(\d+)',
                r'"saves":(\d+)'
            ]
            
            for pattern in bookmark_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="collect-count"]',
            'strong[data-e2e="collect-count"]',
            'div[data-e2e="collect-count"]',
            'span[data-e2e="collect-count"]',
            '[class*="collect"] strong',
            '[class*="Collect"] strong',
            '[class*="bookmark"] strong',
            '[class*="Bookmark"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_username_comprehensive(self, page, page_content: str, url: str) -> str:
        """Comprehensive username extraction"""
        # Method 1: From URL
        try:
            url_match = re.search(r'@([^/]+)', url)
            if url_match:
                return url_match.group(1)
        except:
            pass
        
        # Method 2: From page
        selectors = [
            '[data-e2e="user-title"]',
            '[class*="username"]',
            '[class*="Username"]',
            '[class*="user-name"]',
            '[class*="User-name"]'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        return text.replace('@', '').strip()
            except:
                continue
        
        return "Unknown"

    async def _extract_followers_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive followers extraction"""
        # Method 1: JSON data
        try:
            follower_patterns = [
                r'"followerCount":(\d+)',
                r'"followers":(\d+)',
                r'"fans":(\d+)'
            ]
            
            for pattern in follower_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="followers-count"] strong',
            'strong[data-e2e="followers-count"]',
            'div[data-e2e="followers-count"]',
            'span[data-e2e="followers-count"]',
            '[class*="follower"] strong',
            '[class*="Follower"] strong',
            '[class*="follow"] strong',
            '[class*="Follow"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_following_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive following extraction"""
        # Method 1: JSON data
        try:
            following_patterns = [
                r'"followingCount":(\d+)',
                r'"following":(\d+)'
            ]
            
            for pattern in following_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="following-count"] strong',
            'strong[data-e2e="following-count"]',
            'div[data-e2e="following-count"]',
            'span[data-e2e="following-count"]',
            '[class*="following"] strong',
            '[class*="Following"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_posts_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive posts extraction"""
        # Method 1: JSON data
        try:
            post_patterns = [
                r'"videoCount":(\d+)',
                r'"posts":(\d+)',
                r'"awemeCount":(\d+)'
            ]
            
            for pattern in post_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="posts-count"] strong',
            'strong[data-e2e="posts-count"]',
            'div[data-e2e="posts-count"]',
            'span[data-e2e="posts-count"]',
            '[class*="post"] strong',
            '[class*="Post"] strong',
            '[class*="video"] strong',
            '[class*="Video"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_account_likes_comprehensive(self, page, page_content: str) -> int:
        """Comprehensive account likes extraction"""
        # Method 1: JSON data
        try:
            likes_patterns = [
                r'"totalDiggCount":(\d+)',
                r'"totalLikes":(\d+)',
                r'"totalHeartCount":(\d+)'
            ]
            
            for pattern in likes_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return int(match.group(1))
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="total-likes-count"] strong',
            'strong[data-e2e="total-likes-count"]',
            'div[data-e2e="total-likes-count"]',
            'span[data-e2e="total-likes-count"]',
            '[class*="total-like"] strong',
            '[class*="Total-like"] strong'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            return parsed
            except:
                continue
        
        return 0

    async def _extract_verified_comprehensive(self, page, page_content: str) -> bool:
        """Comprehensive verified extraction"""
        # Method 1: JSON data
        try:
            verified_match = re.search(r'"verified":(true|false)', page_content)
            if verified_match:
                return verified_match.group(1) == 'true'
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="verified-icon"]',
            '[class*="verified"]',
            '[class*="Verified"]',
            '[class*="checkmark"]',
            '[class*="Checkmark"]'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    return True
            except:
                continue
        
        return False

    async def _extract_description_comprehensive(self, page, page_content: str) -> str:
        """Comprehensive description extraction"""
        # Method 1: JSON data
        try:
            desc_patterns = [
                r'"desc":"([^"]+)"',
                r'"description":"([^"]+)"',
                r'"text":"([^"]+)"'
            ]
            
            for pattern in desc_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="video-desc"]',
            '[class*="description"]',
            '[class*="Description"]',
            '[class*="caption"]',
            '[class*="Caption"]',
            '[class*="text"]',
            '[class*="Text"]'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        return text.strip()
            except:
                continue
        
        return ""

    async def _extract_hashtags_comprehensive(self, page, page_content: str) -> str:
        """Comprehensive hashtags extraction"""
        # Method 1: JSON data
        try:
            hashtag_patterns = [
                r'"hashtags":\[([^\]]+)\]',
                r'"challenges":\[([^\]]+)\]'
            ]
            
            for pattern in hashtag_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="hashtag"]',
            '[class*="hashtag"]',
            '[class*="Hashtag"]',
            '[class*="tag"]',
            '[class*="Tag"]'
        ]
        
        hashtags = []
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text and text.startswith('#'):
                        hashtags.append(text)
            except:
                continue
        
        return ', '.join(hashtags)

    async def _extract_mentions_comprehensive(self, page, page_content: str) -> str:
        """Comprehensive mentions extraction"""
        # Method 1: JSON data
        try:
            mention_patterns = [
                r'"mentions":\[([^\]]+)\]',
                r'"atUsers":\[([^\]]+)\]'
            ]
            
            for pattern in mention_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="mention"]',
            '[class*="mention"]',
            '[class*="Mention"]',
            '[class*="at"]',
            '[class*="At"]'
        ]
        
        mentions = []
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text and text.startswith('@'):
                        mentions.append(text)
            except:
                continue
        
        return ', '.join(mentions)

    async def _extract_sound_title_comprehensive(self, page, page_content: str) -> str:
        """Comprehensive sound title extraction"""
        # Method 1: JSON data
        try:
            sound_patterns = [
                r'"musicTitle":"([^"]+)"',
                r'"soundTitle":"([^"]+)"',
                r'"title":"([^"]+)"'
            ]
            
            for pattern in sound_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="sound-title"]',
            '[class*="sound-title"]',
            '[class*="Sound-title"]',
            '[class*="music-title"]',
            '[class*="Music-title"]'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        return text.strip()
            except:
                continue
        
        return ""

    async def _extract_sound_url_comprehensive(self, page, page_content: str) -> str:
        """Comprehensive sound URL extraction"""
        # Method 1: JSON data
        try:
            sound_url_patterns = [
                r'"musicUrl":"([^"]+)"',
                r'"soundUrl":"([^"]+)"',
                r'"playUrl":"([^"]+)"'
            ]
            
            for pattern in sound_url_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="sound-link"]',
            '[class*="sound-link"]',
            '[class*="Sound-link"]',
            '[class*="music-link"]',
            '[class*="Music-link"]'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    href = await element.get_attribute('href')
                    if href:
                        return href
            except:
                continue
        
        return ""

    async def _extract_sound_author_comprehensive(self, page, page_content: str) -> str:
        """Comprehensive sound author extraction"""
        # Method 1: JSON data
        try:
            author_patterns = [
                r'"musicAuthor":"([^"]+)"',
                r'"soundAuthor":"([^"]+)"',
                r'"author":"([^"]+)"'
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, page_content)
                if match:
                    return match.group(1)
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="sound-author"]',
            '[class*="sound-author"]',
            '[class*="Sound-author"]',
            '[class*="music-author"]',
            '[class*="Music-author"]'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        return text.strip()
            except:
                continue
        
        return ""

    async def _extract_slides_comprehensive(self, page, page_content: str) -> list:
        """Comprehensive slides extraction"""
        slides = []
        
        # Method 1: JSON data
        try:
            slide_patterns = [
                r'"images":\[([^\]]+)\]',
                r'"slides":\[([^\]]+)\]',
                r'"thumbnails":\[([^\]]+)\]'
            ]
            
            for pattern in slide_patterns:
                match = re.search(pattern, page_content)
                if match:
                    # Parse JSON array
                    try:
                        slide_data = json.loads(f"[{match.group(1)}]")
                        for slide in slide_data:
                            if isinstance(slide, str):
                                slides.append(slide)
                            elif isinstance(slide, dict) and 'url' in slide:
                                slides.append(slide['url'])
                    except:
                        pass
        except:
            pass
        
        # Method 2: Selectors
        selectors = [
            '[data-e2e="slide"]',
            '[class*="slide"]',
            '[class*="Slide"]',
            '[class*="image"]',
            '[class*="Image"]',
            '[class*="thumbnail"]',
            '[class*="Thumbnail"]'
        ]
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    # Try to get src attribute
                    src = await element.get_attribute('src')
                    if src and src.startswith('http'):
                        slides.append(src)
                    
                    # Try to get data-src attribute
                    data_src = await element.get_attribute('data-src')
                    if data_src and data_src.startswith('http'):
                        slides.append(data_src)
            except:
                continue
        
        # Remove duplicates and limit to 12
        unique_slides = list(dict.fromkeys(slides))[:12]
        
        # Pad with empty strings to ensure 12 slides
        while len(unique_slides) < 12:
            unique_slides.append("")
        
        return unique_slides

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from TikTok URL"""
        try:
            # Handle different URL formats
            if '/t/' in url:
                # Short URL format: https://www.tiktok.com/t/ZTMuUscW9/
                match = re.search(r'/t/([^/]+)', url)
                if match:
                    return match.group(1)
            elif '/video/' in url:
                # Long URL format: https://www.tiktok.com/@user/video/1234567890
                match = re.search(r'/video/(\d+)', url)
                if match:
                    return match.group(1)
            elif 'vt.tiktok.com' in url:
                # VT URL format: https://vt.tiktok.com/ZSUGHkc9j/
                match = re.search(r'vt\.tiktok\.com/([^/]+)', url)
                if match:
                    return match.group(1)
        except:
            pass
        
        return ""

    async def _parse_api_response(self, json_data: dict, url: str, method: str) -> dict:
        """Parse API response and extract data"""
        try:
            # This is a simplified parser - would need to be adapted based on actual API response structure
            views = json_data.get('playCount', 0)
            likes = json_data.get('diggCount', 0)
            comments = json_data.get('commentCount', 0)
            shares = json_data.get('shareCount', 0)
            bookmarks = json_data.get('collectCount', 0)
            
            if views > 0:
                return {
                    "post_url": url,
                    "creator": "Unknown",
                    "set_id": 0,
                    "va": "Unknown",
                    "type": "Unknown",
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "bookmarks": bookmarks,
                    "engagement": likes + comments + shares + bookmarks,
                    "engagement_rate": round((likes + comments + shares + bookmarks) / views * 100, 2) if views > 0 else 0.0,
                    "account_username": "Unknown",
                    "account_followers": 0,
                    "account_following": 0,
                    "account_posts": 0,
                    "account_likes": 0,
                    "account_verified": False,
                    "post_description": "",
                    "hashtags": "",
                    "mentions": "",
                    "content_length": 0,
                    "sound_title": "",
                    "sound_url": "",
                    "sound_author": "",
                    "has_sound": False,
                    "slide_count": 0,
                    "slide_1": "", "slide_2": "", "slide_3": "", "slide_4": "", "slide_5": "", "slide_6": "",
                    "slide_7": "", "slide_8": "", "slide_9": "", "slide_10": "", "slide_11": "", "slide_12": "",
                    "scraped_at": datetime.now().isoformat(),
                    "scraping_method": method,
                    "scraping_success": True,
                    "data_quality": "API"
                }
        except:
            pass
        
        return None

    def _create_failed_result(self, url: str, method: str, error: str) -> dict:
        """Create a failed result"""
        return {
            "post_url": url,
            "creator": "Unknown",
            "set_id": 0,
            "va": "Unknown",
            "type": "Unknown",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "bookmarks": 0,
            "engagement": 0,
            "engagement_rate": 0.0,
            "account_username": "Unknown",
            "account_followers": 0,
            "account_following": 0,
            "account_posts": 0,
            "account_likes": 0,
            "account_verified": False,
            "post_description": "",
            "hashtags": "",
            "mentions": "",
            "content_length": 0,
            "sound_title": "",
            "sound_url": "",
            "sound_author": "",
            "has_sound": False,
            "slide_count": 0,
            "slide_1": "", "slide_2": "", "slide_3": "", "slide_4": "", "slide_5": "", "slide_6": "",
            "slide_7": "", "slide_8": "", "slide_9": "", "slide_10": "", "slide_11": "", "slide_12": "",
            "scraped_at": datetime.now().isoformat(),
            "scraping_method": method,
            "scraping_success": False,
            "data_quality": "Failed",
            "error": error
        }

    def _looks_like_views(self, text: str) -> bool:
        """Check if text looks like view count"""
        text = str(text).lower().strip()
        return (
            'view' in text and 
            any(char.isdigit() for char in text) and
            len(text) < 20
        )

    def _parse_metric(self, text: str) -> int:
        """Parse a metric string (e.g., "10.5K", "1.2M") into an integer"""
        text = text.replace(',', '').strip()
        text = text.lower()

        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        elif 'b' in text:
            return int(float(text.replace('b', '')) * 1000000000)
        else:
            # Extract only digits, handle cases like "22 comments"
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

    async def run_swarm_test(self, urls: list, test_name: str) -> pd.DataFrame:
        """
        Run SWARM test with all 6 agents
        """
        logger.info(f"🚀 SWARM MODE: {test_name} - Testing {len(urls)} URLs")
        logger.info("=" * 80)
        
        # Split URLs among agents
        chunk_size = max(1, len(urls) // 6)  # Ensure chunk_size is at least 1
        url_chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
        
        # Ensure we have 6 chunks
        while len(url_chunks) < 6:
            url_chunks.append([])
        
        # Run all agents in parallel
        tasks = [
            self.agent_1_mobile_optimized(url_chunks[0]),
            self.agent_2_desktop_optimized(url_chunks[1]),
            self.agent_3_stealth_mode(url_chunks[2]),
            self.agent_4_api_scraper(url_chunks[3]),
            self.agent_5_hybrid_scraper(url_chunks[4]),
            self.agent_6_advanced_scraper(url_chunks[5])
        ]
        
        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {i+1} failed with exception: {result}")
                continue
            
            all_results.extend(result)
        
        # Create DataFrame
        df = pd.DataFrame(all_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"SWARM_{test_name}_{timestamp}.csv"
        df.to_csv(output_file, index=False)
        
        # Analyze results
        self._analyze_results(df, test_name, output_file)
        
        return df

    def _analyze_results(self, df: pd.DataFrame, test_name: str, output_file: str):
        """Analyze and report results"""
        logger.info(f"\n📊 SWARM RESULTS ANALYSIS: {test_name}")
        logger.info("=" * 80)
        
        total_urls = len(df)
        successful_scrapes = len(df[df['scraping_success'] == True])
        failed_scrapes = len(df[df['scraping_success'] == False])
        
        logger.info(f"📈 Total URLs: {total_urls}")
        logger.info(f"✅ Successful: {successful_scrapes} ({successful_scrapes/total_urls*100:.1f}%)")
        logger.info(f"❌ Failed: {failed_scrapes} ({failed_scrapes/total_urls*100:.1f}%)")
        
        # Analyze by method
        method_stats = df.groupby('scraping_method').agg({
            'scraping_success': ['count', 'sum'],
            'views': ['sum', 'mean'],
            'likes': ['sum', 'mean'],
            'comments': ['sum', 'mean']
        }).round(2)
        
        logger.info(f"\n🔧 METHOD PERFORMANCE:")
        for method in df['scraping_method'].unique():
            method_df = df[df['scraping_method'] == method]
            success_rate = method_df['scraping_success'].mean() * 100
            avg_views = method_df['views'].mean()
            avg_likes = method_df['likes'].mean()
            avg_comments = method_df['comments'].mean()
            
            logger.info(f"   {method}: {success_rate:.1f}% success, {avg_views:.0f} avg views, {avg_likes:.0f} avg likes, {avg_comments:.0f} avg comments")
        
        # Data quality analysis
        complete_data = len(df[(df['views'] > 0) & (df['likes'] > 0) & (df['comments'] > 0)])
        partial_data = len(df[(df['views'] > 0) & ((df['likes'] == 0) | (df['comments'] == 0))])
        no_data = len(df[df['views'] == 0])
        
        logger.info(f"\n📊 DATA QUALITY:")
        logger.info(f"   Complete Data: {complete_data} ({complete_data/total_urls*100:.1f}%)")
        logger.info(f"   Partial Data: {partial_data} ({partial_data/total_urls*100:.1f}%)")
        logger.info(f"   No Data: {no_data} ({no_data/total_urls*100:.1f}%)")
        
        logger.info(f"\n💾 Results saved to: {output_file}")
        
        return {
            'total_urls': total_urls,
            'successful_scrapes': successful_scrapes,
            'failed_scrapes': failed_scrapes,
            'complete_data': complete_data,
            'partial_data': partial_data,
            'no_data': no_data,
            'output_file': output_file
        }

async def main():
    """Main execution"""
    print("🚀 SWARM MODE: Complete Data Scraper for 100 Videos")
    print("=" * 80)
    
    # Your 100 URLs
    urls = [
        "https://www.tiktok.com/t/ZTMuUscW9/",
        "https://www.tiktok.com/t/ZTMuUEG3c/",
        "https://www.tiktok.com/t/ZTMuyRh5a/",
        "https://www.tiktok.com/t/ZP8A7kX4w/",
        "https://www.tiktok.com/t/ZP8A7L74E/",
        "https://www.tiktok.com/t/ZP8AWKSmF/",
        "https://www.tiktok.com/t/ZP8AWE7sA/",
        "https://www.tiktok.com/t/ZP8A7eWtL/",
        "https://www.tiktok.com/t/ZTMumCAUk/",
        "https://www.tiktok.com/t/ZTMuuY6RG/",
        "https://www.tiktok.com/t/ZTMuuuUWY/",
        "https://www.tiktok.com/t/ZTMuuvqtk/",
        "https://www.tiktok.com/t/ZTMuHX9Bv/",
        "https://www.tiktok.com/t/ZP8AWKcBJ/",
        "https://www.tiktok.com/t/ZP8A7ymPT/",
        "https://www.tiktok.com/t/ZP8A7Sj5N/",
        "https://www.tiktok.com/t/ZP8A7egj8/",
        "https://www.tiktok.com/t/ZP8A74CCt/",
        "https://www.tiktok.com/t/ZP8A7t8Ch/",
        "https://www.tiktok.com/t/ZP8A7bXhw/",
        "https://www.tiktok.com/t/ZP8A7fLcC/",
        "https://www.tiktok.com/t/ZP8A7bj6f/",
        "https://www.tiktok.com/t/ZP8A7Ctk7/",
        "https://www.tiktok.com/t/ZTMuQ5W1q/",
        "https://www.tiktok.com/t/ZTMuXq7EW/",
        "https://www.tiktok.com/t/ZP8A7xhj5/",
        "https://www.tiktok.com/t/ZTMuX3oSU/",
        "https://www.tiktok.com/t/ZTMu4JN1Y/",
        "https://www.tiktok.com/t/ZTMu42n2V/",
        "https://www.tiktok.com/t/ZTMu4aCUa/",
        "https://www.tiktok.com/t/ZTMu4D8Kw/",
        "https://www.tiktok.com/t/ZP8A77Lec/",
        "https://www.tiktok.com/t/ZP8A74dd6/",
        "https://www.tiktok.com/t/ZP8A7gYvo/",
        "https://www.tiktok.com/t/ZP8A7pfce/",
        "https://www.tiktok.com/t/ZTMuV2Wxk/",
        "https://www.tiktok.com/t/ZP8A7xTtY/",
        "https://www.tiktok.com/t/ZP8A7ay5o/",
        "https://www.tiktok.com/t/ZTMuVm5Jm/",
        "https://www.tiktok.com/t/ZP8A7gUkm/",
        "https://www.tiktok.com/t/ZTMuV2gC9/",
        "https://www.tiktok.com/t/ZP8A7qJ7f/",
        "https://www.tiktok.com/t/ZTMuVqtCG/",
        "https://vt.tiktok.com/ZSUGHkc9j/",
        "https://www.tiktok.com/t/ZP8A7VCuu/",
        "https://www.tiktok.com/t/ZP8A7XmFu/",
        "https://www.tiktok.com/t/ZTMuV9UxR/",
        "https://www.tiktok.com/t/ZTMuVn2Ex/",
        "https://www.tiktok.com/t/ZTMuVXXyb/",
        "https://www.tiktok.com/t/ZTMuV9b55/",
        "https://www.tiktok.com/t/ZTMuVKabr/",
        "https://www.tiktok.com/t/ZTMuVWAYj/",
        "https://www.tiktok.com/t/ZP8A754BD/",
        "https://www.tiktok.com/t/ZTMuVTj13/",
        "https://vt.tiktok.com/ZSUGHmYun/",
        "https://www.tiktok.com/t/ZTMuqMdfm/",
        "https://www.tiktok.com/t/ZP8A7QdkT/",
        "https://www.tiktok.com/t/ZTMuqApVw/",
        "https://www.tiktok.com/t/ZTMuqkTK9/",
        "https://www.tiktok.com/t/ZTMuq8QpU/",
        "https://www.tiktok.com/t/ZP8A7fmgp/",
        "https://www.tiktok.com/t/ZP8A7CT3q/",
        "https://www.tiktok.com/t/ZTMuqJ6Hx/",
        "https://www.tiktok.com/t/ZTMuqSj7G/",
        "https://www.tiktok.com/t/ZTMuqjS1e/",
        "https://www.tiktok.com/t/ZTMuqY5Xj/",
        "https://www.tiktok.com/t/ZP8A7PJ72/",
        "https://www.tiktok.com/t/ZTMuqNbXK/",
        "https://www.tiktok.com/t/ZTMuqn9hg/",
        "https://www.tiktok.com/t/ZTMuqHBws/",
        "https://www.tiktok.com/t/ZP8A7xxS8/",
        "https://www.tiktok.com/t/ZTMuqWNwt/",
        "https://www.tiktok.com/t/ZTMuqaukV/",
        "https://www.tiktok.com/t/ZP8A778mN/",
        "https://www.tiktok.com/t/ZP8A7b11C/",
        "https://www.tiktok.com/t/ZTMuq9Xjj/",
        "https://www.tiktok.com/t/ZTMuqxDdV/",
        "https://www.tiktok.com/t/ZP8A7XrN7/",
        "https://www.tiktok.com/t/ZTMuqQjqE/",
        "https://www.tiktok.com/t/ZP8A7VwsM/",
        "https://www.tiktok.com/t/ZTMuqbRjn/",
        "https://www.tiktok.com/t/ZP8A7Ccwv/",
        "https://www.tiktok.com/t/ZTMuqxjnC/",
        "https://www.tiktok.com/t/ZTMuq7CnX/",
        "https://www.tiktok.com/t/ZTMuqQjqE/",
        "https://www.tiktok.com/t/ZP8A7mVAH/",
        "https://www.tiktok.com/t/ZTMub6bbM/",
        "https://www.tiktok.com/t/ZP8A7xEHa/",
        "https://www.tiktok.com/t/ZTMuqKXmB/",
        "https://www.tiktok.com/t/ZTMubRucf/",
        "https://www.tiktok.com/t/ZTMubjtfY/",
        "https://www.tiktok.com/t/ZTMubdJPp/",
        "https://www.tiktok.com/t/ZTMuqEX44/",
        "https://www.tiktok.com/t/ZP8A7uELk/",
        "https://www.tiktok.com/t/ZTMuqwRmw/",
        "https://www.tiktok.com/t/ZP8A7qrSk/",
        "https://www.tiktok.com/t/ZP8A7vY59/",
        "https://www.tiktok.com/t/ZTMubAWvv/",
        "https://www.tiktok.com/t/ZTMubggAH/",
        "https://www.tiktok.com/t/ZP8A7mJAD/"
    ]
    
    print(f"📊 Total URLs: {len(urls)}")
    print("🔧 6 Parallel Agents:")
    print("   📱 Agent 1: Mobile-optimized")
    print("   🖥️ Agent 2: Desktop-optimized")
    print("   🥷 Agent 3: Stealth mode")
    print("   🔌 Agent 4: API scraper")
    print("   🔄 Agent 5: Hybrid scraper")
    print("   🚀 Agent 6: Advanced scraper")
    print()
    
    # Test 1: 5 videos
    print("🎯 TEST 1: 5 VIDEOS")
    print("-" * 40)
    
    async with SwarmCompleteDataScraper(headless=True, debug=False) as scraper:
        test_5_results = await scraper.run_swarm_test(urls[:5], "5_VIDEOS")
    
    # Test 2: 20 videos (if 5 videos successful)
    if len(test_5_results[test_5_results['scraping_success'] == True]) >= 3:
        print("\n🎯 TEST 2: 20 VIDEOS")
        print("-" * 40)
        
        async with SwarmCompleteDataScraper(headless=True, debug=False) as scraper:
            test_20_results = await scraper.run_swarm_test(urls[:20], "20_VIDEOS")
        
        # Test 3: All 100 videos (if 20 videos successful)
        if len(test_20_results[test_20_results['scraping_success'] == True]) >= 15:
            print("\n🎯 TEST 3: ALL 100 VIDEOS")
            print("-" * 40)
            
            async with SwarmCompleteDataScraper(headless=True, debug=False) as scraper:
                test_100_results = await scraper.run_swarm_test(urls, "100_VIDEOS")
        else:
            print("❌ 20 videos test failed - stopping at 20 videos")
    else:
        print("❌ 5 videos test failed - stopping at 5 videos")
    
    print("\n🎉 SWARM MODE COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
