"""
Enhanced Stealth Sofia Scraper
SuperClaude Advanced Anti-Bot Bypass Agent

Using advanced stealth techniques to bypass TikTok's anti-bot protection
"""

import asyncio
import pandas as pd
import time
import random
from datetime import datetime
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedStealthSofiaScraper:
    """
    Enhanced stealth scraper with advanced anti-bot bypass techniques
    """
    
    def __init__(self, headless=True, debug=True):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Async context manager entry with enhanced stealth"""
        self.playwright = await async_playwright().start()
        
        # Enhanced browser launch with maximum stealth
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
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-javascript',
                '--disable-default-apps',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-ipc-flooding-protection',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-pings',
                '--password-store=basic',
                '--use-mock-keychain',
                '--disable-component-extensions-with-background-pages',
                '--disable-background-networking',
                '--disable-sync',
                '--metrics-recording-only',
                '--no-report-upload',
                '--disable-logging',
                '--disable-gpu-logging',
                '--silent',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-client-side-phishing-detection',
                '--disable-component-update',
                '--disable-domain-reliability',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_sofia_with_stealth(self, post_url: str) -> dict:
        """
        Scrape Sofia's post with maximum stealth
        """
        try:
            # Create new page with stealth context
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                permissions=['geolocation'],
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            page = await context.new_page()
            
            # Add stealth scripts
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
                
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' }),
                    }),
                });
            """)
            
            logger.info(f"🔍 Starting enhanced stealth scraping: {post_url}")
            
            # Human-like navigation
            await page.goto('https://www.tiktok.com', wait_until='networkidle', timeout=30000)
            await self._human_delay(2, 4)
            
            # Navigate to Sofia's post
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await self._human_delay(3, 6)
            
            # Simulate human behavior
            await self._simulate_human_behavior(page)
            
            # Debug: Save page content
            if self.debug:
                page_content = await page.content()
                with open('sofia_enhanced_stealth_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info("💾 Debug: Saved enhanced stealth page content")
            
            # Extract data with multiple attempts
            scraped_data = await self._extract_data_with_retries(page, post_url)
            
            await context.close()
            return scraped_data
            
        except Exception as e:
            logger.error(f"❌ Enhanced stealth scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False
            }

    async def _human_delay(self, min_seconds: float, max_seconds: float):
        """Simulate human-like delays"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def _simulate_human_behavior(self, page):
        """Simulate human-like behavior on the page"""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 1800)
                y = random.randint(100, 900)
                await page.mouse.move(x, y)
                await self._human_delay(0.5, 1.5)
            
            # Random scrolls
            for _ in range(random.randint(1, 3)):
                await page.mouse.wheel(0, random.randint(100, 500))
                await self._human_delay(1, 2)
            
            # Random clicks (not on interactive elements)
            for _ in range(random.randint(1, 2)):
                x = random.randint(200, 1600)
                y = random.randint(200, 800)
                await page.mouse.click(x, y)
                await self._human_delay(0.5, 1)
            
        except Exception as e:
            logger.debug(f"Human behavior simulation error: {e}")

    async def _extract_data_with_retries(self, page, post_url):
        """Extract data with multiple retry attempts"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            logger.info(f"🔄 Data extraction attempt {attempt + 1}/{max_retries}")
            
            try:
                # Wait for content to load
                await self._human_delay(2, 4)
                
                # Try to extract data
                data = await self._extract_all_data(page, post_url)
                
                # Check if we got meaningful data
                if data.get('views', 0) > 0 or data.get('likes', 0) > 0:
                    logger.info("✅ Successfully extracted data!")
                    return data
                else:
                    logger.warning(f"⚠️ Attempt {attempt + 1}: No meaningful data extracted")
                    if attempt < max_retries - 1:
                        await self._human_delay(retry_delay, retry_delay * 2)
                        retry_delay *= 2
                
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await self._human_delay(retry_delay, retry_delay * 2)
                    retry_delay *= 2
        
        # If all attempts failed, return what we have
        return await self._extract_all_data(page, post_url)

    async def _extract_all_data(self, page, post_url):
        """Extract all possible data from the page"""
        data = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat(),
            "success": True
        }
        
        try:
            # Extract post metrics
            logger.info("📊 Extracting post metrics...")
            data.update(await self._extract_post_metrics_enhanced(page))
            
            # Extract account information
            logger.info("👤 Extracting account information...")
            data.update(await self._extract_account_info_enhanced(page))
            
            # Extract content analysis
            logger.info("🎨 Extracting content analysis...")
            data.update(await self._extract_content_analysis_enhanced(page))
            
            logger.info("✅ Enhanced data extraction completed")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced extraction: {e}")
            data["extraction_error"] = str(e)
            data["success"] = False
        
        return data

    async def _extract_post_metrics_enhanced(self, page):
        """Enhanced post metrics extraction"""
        metrics = {}
        
        try:
            # Method 1: Look for JSON data in page source
            page_content = await page.content()
            
            # Try multiple JSON patterns
            json_patterns = [
                r'"playCount":(\d+)',
                r'"viewCount":(\d+)',
                r'"views":(\d+)',
                r'"likeCount":(\d+)',
                r'"commentCount":(\d+)',
                r'"shareCount":(\d+)',
                r'"collectCount":(\d+)'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    value = int(matches[0])
                    if 'playCount' in pattern or 'viewCount' in pattern or 'views' in pattern:
                        metrics['views'] = value
                        logger.info(f"✅ Found views in JSON: {value:,}")
                    elif 'likeCount' in pattern:
                        metrics['likes'] = value
                    elif 'commentCount' in pattern:
                        metrics['comments'] = value
                    elif 'shareCount' in pattern:
                        metrics['shares'] = value
                    elif 'collectCount' in pattern:
                        metrics['bookmarks'] = value
            
            # Method 2: Try enhanced selectors
            enhanced_selectors = {
                'views': [
                    '[data-e2e="video-views"]',
                    '[data-e2e="video-view-count"]',
                    '[data-e2e="browse-video-view-count"]',
                    'strong[data-e2e="video-views"]',
                    'span[data-e2e="video-views"]',
                    '[class*="view"] strong',
                    '[class*="View"] strong',
                    '[class*="count"] strong'
                ],
                'likes': [
                    '[data-e2e="like-count"]',
                    'strong[data-e2e="like-count"]',
                    'div[data-e2e="like-count"]',
                    'span[data-e2e="like-count"]',
                    '[class*="like"] strong',
                    '[class*="Like"] strong'
                ],
                'comments': [
                    '[data-e2e="comment-count"]',
                    'strong[data-e2e="comment-count"]',
                    'div[data-e2e="comment-count"]',
                    'span[data-e2e="comment-count"]',
                    '[class*="comment"] strong',
                    '[class*="Comment"] strong'
                ],
                'shares': [
                    '[data-e2e="share-count"]',
                    'strong[data-e2e="share-count"]',
                    'div[data-e2e="share-count"]',
                    'span[data-e2e="share-count"]',
                    '[class*="share"] strong',
                    '[class*="Share"] strong'
                ]
            }
            
            for metric, selectors in enhanced_selectors.items():
                if metric not in metrics:  # Only if not found in JSON
                    for selector in selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                text = await element.text_content()
                                if text:
                                    parsed = self._parse_metric(text)
                                    if parsed > 0:
                                        metrics[metric] = parsed
                                        logger.info(f"✅ Found {metric} with selector: {parsed:,}")
                                        break
                        except Exception:
                            continue
            
            # Set defaults if not found
            for metric in ['views', 'likes', 'comments', 'shares', 'bookmarks']:
                if metric not in metrics:
                    metrics[metric] = 0
            
            # Calculate engagement
            total_engagement = metrics["likes"] + metrics["comments"] + metrics["shares"] + metrics["bookmarks"]
            metrics["engagement"] = total_engagement
            
            if metrics["views"] > 0:
                metrics["engagement_rate"] = round((total_engagement / metrics["views"]) * 100, 2)
            else:
                metrics["engagement_rate"] = 0.0
            
            logger.info(f"📊 Enhanced metrics: {metrics['views']:,} views, {metrics['likes']:,} likes, {metrics['engagement_rate']:.2f}% engagement")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced metrics extraction: {e}")
            metrics["metrics_error"] = str(e)
        
        return metrics

    async def _extract_account_info_enhanced(self, page):
        """Enhanced account information extraction"""
        account_info = {}
        
        try:
            # Enhanced username extraction
            username_selectors = [
                '[data-e2e="browse-username"]',
                'h1[data-e2e="browse-username"]',
                '[class*="username"]',
                '[class*="Username"]',
                'h1[class*="username"]',
                'span[class*="username"]'
            ]
            
            for selector in username_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and text.strip():
                            account_info["username"] = text.strip().replace('@', '')
                            logger.info(f"✅ Found username: @{account_info['username']}")
                            break
                except Exception:
                    continue
            
            # Enhanced followers extraction
            followers_selectors = [
                '[data-e2e="followers-count"] strong',
                'strong[data-e2e="followers-count"]',
                '[class*="follower"] strong',
                '[class*="Follower"] strong',
                '[class*="count"] strong'
            ]
            
            for selector in followers_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text:
                            parsed = self._parse_metric(text)
                            if parsed > 0:
                                account_info["followers"] = parsed
                                logger.info(f"✅ Found followers: {parsed:,}")
                                break
                except Exception:
                    continue
            
            # Set defaults
            if "username" not in account_info:
                account_info["username"] = ""
            if "followers" not in account_info:
                account_info["followers"] = 0
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced account extraction: {e}")
            account_info["account_error"] = str(e)
        
        return account_info

    async def _extract_content_analysis_enhanced(self, page):
        """Enhanced content analysis extraction"""
        content = {}
        
        try:
            # Enhanced hashtag extraction
            hashtags = []
            
            # Method 1: Look for hashtag elements
            hashtag_elements = await page.query_selector_all('a[href*="/tag/"], [class*="hashtag"], [class*="Hashtag"]')
            for element in hashtag_elements:
                text = await element.text_content()
                if text and text.startswith('#'):
                    hashtags.append(text)
            
            # Method 2: Look in description
            description_selectors = [
                '[data-e2e="browse-desc"]',
                '[class*="description"]',
                '[class*="caption"]',
                '[class*="bio"]'
            ]
            
            for selector in description_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text:
                            hashtag_matches = re.findall(r'#\w+', text)
                            hashtags.extend(hashtag_matches)
                            content["description"] = text.strip()
                            break
                except Exception:
                    continue
            
            # Remove duplicates
            content["hashtags"] = list(set(hashtags))
            
            logger.info(f"🎨 Enhanced content: {len(content['hashtags'])} hashtags")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced content extraction: {e}")
            content["content_error"] = str(e)
        
        return content

    def _parse_metric(self, text: str) -> int:
        """Parse a metric string into an integer"""
        import re
        text = text.replace(',', '').strip()
        text = text.lower()

        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        elif 'b' in text:
            return int(float(text.replace('b', '')) * 1000000000)
        else:
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

async def main():
    """Main execution function"""
    print("🎯 ENHANCED STEALTH SOFIA SCRAPER")
    print("=" * 60)
    
    # Sofia's post details
    post_url = "https://www.tiktok.com/t/ZTMure1j4/"
    creator = "Sofia"
    set_id = 86
    va = "Almira"
    post_type = "NEW"
    
    print(f"🔍 Target: {post_url}")
    print(f"👤 Creator: {creator}")
    print(f"📦 Set: #{set_id}")
    print(f"👥 VA: {va}")
    print(f"📝 Type: {post_type}")
    print()
    
    # Run enhanced stealth scraping
    async with EnhancedStealthSofiaScraper(headless=True, debug=True) as scraper:
        scraped_data = await scraper.scrape_sofia_with_stealth(post_url)
    
    # Add metadata
    scraped_data.update({
        "creator": creator,
        "set_id": set_id,
        "va": va,
        "post_type": post_type,
        "extraction_method": "Enhanced Stealth Scraping"
    })
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"sofia_enhanced_stealth_results_{timestamp}.json"
    
    import json
    with open(output_file, 'w') as f:
        json.dump(scraped_data, f, indent=2, default=str)
    
    print("\n📊 ENHANCED STEALTH SCRAPING RESULTS:")
    print("=" * 60)
    
    if scraped_data.get("success", False) and scraped_data.get('views', 0) > 0:
        print("✅ SUCCESS! Real data extracted with enhanced stealth!")
        print(f"📊 Views: {scraped_data.get('views', 0):,}")
        print(f"❤️ Likes: {scraped_data.get('likes', 0):,}")
        print(f"💬 Comments: {scraped_data.get('comments', 0):,}")
        print(f"📤 Shares: {scraped_data.get('shares', 0):,}")
        print(f"🔖 Bookmarks: {scraped_data.get('bookmarks', 0):,}")
        print(f"📈 Engagement Rate: {scraped_data.get('engagement_rate', 0):.2f}%")
        print(f"👤 Username: @{scraped_data.get('username', 'N/A')}")
        print(f"👥 Followers: {scraped_data.get('followers', 0):,}")
        print(f"🎨 Hashtags: {', '.join(scraped_data.get('hashtags', []))}")
        print(f"📝 Description: {scraped_data.get('description', 'N/A')[:100]}...")
    else:
        print("❌ Enhanced stealth scraping failed")
        if 'error' in scraped_data:
            print(f"Error: {scraped_data['error']}")
        else:
            print("Views: 0 - TikTok's anti-bot protection is very strong")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return scraped_data

if __name__ == "__main__":
    import re
    asyncio.run(main())
