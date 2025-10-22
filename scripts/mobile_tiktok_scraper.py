"""
Mobile TikTok Scraper - Sofia's Handy URL
SuperClaude Mobile Scraping Specialist

Specialized scraper for mobile TikTok URLs like Sofia's post
"""

import asyncio
import pandas as pd
import time
import random
import re
from datetime import datetime
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MobileTikTokScraper:
    """
    Mobile-optimized TikTok scraper for hand-shared URLs
    """
    
    def __init__(self, headless=True, debug=True):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Mobile browser setup"""
        self.playwright = await async_playwright().start()
        
        # Mobile-optimized browser
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

    async def scrape_mobile_tiktok(self, post_url: str) -> dict:
        """
        Scrape mobile TikTok URL with mobile-optimized approach
        """
        try:
            # Create mobile context
            context = await self.browser.new_context(
                viewport={'width': 375, 'height': 812},  # iPhone size
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                permissions=['geolocation'],
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
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
            
            # Mobile-specific stealth
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
                
                window.orientation = 0;
                window.screen = {
                    width: 375,
                    height: 812,
                    availWidth: 375,
                    availHeight: 812,
                    colorDepth: 24,
                    pixelDepth: 24
                };
            """)
            
            logger.info(f"📱 Mobile scraping: {post_url}")
            
            # Navigate with mobile approach
            await page.goto(post_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Debug save
            if self.debug:
                page_content = await page.content()
                with open('sofia_mobile_debug.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info("💾 Mobile debug saved")
            
            # Extract data
            scraped_data = await self._extract_mobile_data(page, post_url)
            
            await context.close()
            return scraped_data
            
        except Exception as e:
            logger.error(f"❌ Mobile scraping failed: {e}")
            return {
                "post_url": post_url,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False
            }

    async def _extract_mobile_data(self, page, post_url):
        """Extract data from mobile TikTok page"""
        data = {
            "post_url": post_url,
            "scraped_at": datetime.now().isoformat(),
            "success": True
        }
        
        try:
            # Get page content for analysis
            page_content = await page.content()
            
            # Method 1: Look for mobile-specific JSON data
            mobile_patterns = [
                r'"playCount":(\d+)',
                r'"viewCount":(\d+)',
                r'"likeCount":(\d+)',
                r'"commentCount":(\d+)',
                r'"shareCount":(\d+)',
                r'"collectCount":(\d+)',
                r'"diggCount":(\d+)',
                r'"play":(\d+)',
                r'"like":(\d+)',
                r'"comment":(\d+)',
                r'"share":(\d+)'
            ]
            
            for pattern in mobile_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    value = int(matches[0])
                    if 'play' in pattern or 'view' in pattern:
                        data['views'] = value
                        logger.info(f"✅ Mobile views found: {value:,}")
                    elif 'like' in pattern or 'digg' in pattern:
                        data['likes'] = value
                        logger.info(f"✅ Mobile likes found: {value:,}")
                    elif 'comment' in pattern:
                        data['comments'] = value
                        logger.info(f"✅ Mobile comments found: {value:,}")
                    elif 'share' in pattern:
                        data['shares'] = value
                        logger.info(f"✅ Mobile shares found: {value:,}")
                    elif 'collect' in pattern:
                        data['bookmarks'] = value
                        logger.info(f"✅ Mobile bookmarks found: {value:,}")
            
            # Method 2: Mobile-specific selectors
            mobile_selectors = {
                'views': [
                    '[data-e2e="video-views"]',
                    '[data-e2e="video-view-count"]',
                    'strong[data-e2e="video-views"]',
                    'span[data-e2e="video-views"]',
                    '.video-count',
                    '.view-count'
                ],
                'likes': [
                    '[data-e2e="like-count"]',
                    'strong[data-e2e="like-count"]',
                    'div[data-e2e="like-count"]',
                    'span[data-e2e="like-count"]',
                    '.like-count'
                ],
                'comments': [
                    '[data-e2e="comment-count"]',
                    'strong[data-e2e="comment-count"]',
                    'div[data-e2e="comment-count"]',
                    'span[data-e2e="comment-count"]',
                    '.comment-count'
                ],
                'shares': [
                    '[data-e2e="share-count"]',
                    'strong[data-e2e="share-count"]',
                    'div[data-e2e="share-count"]',
                    'span[data-e2e="share-count"]',
                    '.share-count'
                ]
            }
            
            for metric, selectors in mobile_selectors.items():
                if metric not in data:  # Only if not found in JSON
                    for selector in selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                text = await element.text_content()
                                if text:
                                    parsed = self._parse_metric(text)
                                    if parsed > 0:
                                        data[metric] = parsed
                                        logger.info(f"✅ Mobile {metric}: {parsed:,}")
                                        break
                        except Exception:
                            continue
            
            # Method 3: Look for any numbers that could be metrics
            all_numbers = re.findall(r'\b(\d+(?:,\d{3})*(?:\.\d+)?[KMB]?)\b', page_content)
            logger.info(f"🔍 Found {len(all_numbers)} numbers in page: {all_numbers[:10]}")
            
            # Method 4: Try to find username
            username_patterns = [
                r'"uniqueId":"([^"]+)"',
                r'"nickname":"([^"]+)"',
                r'"username":"([^"]+)"',
                r'@(\w+)',
                r'tiktok\.com/@([^/?]+)'
            ]
            
            for pattern in username_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    data['username'] = matches[0]
                    logger.info(f"✅ Username found: @{data['username']}")
                    break
            
            # Method 5: Try to find followers
            follower_patterns = [
                r'"followerCount":(\d+)',
                r'"follower":(\d+)',
                r'"followers":(\d+)'
            ]
            
            for pattern in follower_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    data['followers'] = int(matches[0])
                    logger.info(f"✅ Followers found: {data['followers']:,}")
                    break
            
            # Set defaults
            for metric in ['views', 'likes', 'comments', 'shares', 'bookmarks']:
                if metric not in data:
                    data[metric] = 0
            
            # Calculate engagement
            total_engagement = data["likes"] + data["comments"] + data["shares"] + data["bookmarks"]
            data["engagement"] = total_engagement
            
            if data["views"] > 0:
                data["engagement_rate"] = round((total_engagement / data["views"]) * 100, 2)
            else:
                data["engagement_rate"] = 0.0
            
            logger.info(f"📊 Mobile extraction: {data['views']:,} views, {data['likes']:,} likes, {data['engagement_rate']:.2f}% engagement")
            
        except Exception as e:
            logger.error(f"❌ Mobile extraction error: {e}")
            data["extraction_error"] = str(e)
            data["success"] = False
        
        return data

    def _parse_metric(self, text: str) -> int:
        """Parse metric text to integer"""
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
    """Main execution"""
    print("📱 MOBILE TIKTOK SCRAPER - SOFIA'S HANDY URL")
    print("=" * 60)
    
    post_url = "https://www.tiktok.com/t/ZTMure1j4/"
    creator = "Sofia"
    set_id = 86
    va = "Almira"
    post_type = "NEW"
    
    print(f"📱 Target: {post_url}")
    print(f"👤 Creator: {creator}")
    print(f"📦 Set: #{set_id}")
    print(f"👥 VA: {va}")
    print(f"📝 Type: {post_type}")
    print()
    
    # Try mobile scraping
    async with MobileTikTokScraper(headless=True, debug=True) as scraper:
        scraped_data = await scraper.scrape_mobile_tiktok(post_url)
    
    # Add metadata
    scraped_data.update({
        "creator": creator,
        "set_id": set_id,
        "va": va,
        "post_type": post_type,
        "extraction_method": "Mobile TikTok Scraper"
    })
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"sofia_mobile_results_{timestamp}.json"
    
    import json
    with open(output_file, 'w') as f:
        json.dump(scraped_data, f, indent=2, default=str)
    
    print("\n📊 MOBILE SCRAPING RESULTS:")
    print("=" * 60)
    
    if scraped_data.get("success", False) and scraped_data.get('views', 0) > 0:
        print("✅ SUCCESS! Mobile scraping worked!")
        print(f"📊 Views: {scraped_data.get('views', 0):,}")
        print(f"❤️ Likes: {scraped_data.get('likes', 0):,}")
        print(f"💬 Comments: {scraped_data.get('comments', 0):,}")
        print(f"📤 Shares: {scraped_data.get('shares', 0):,}")
        print(f"🔖 Bookmarks: {scraped_data.get('bookmarks', 0):,}")
        print(f"📈 Engagement Rate: {scraped_data.get('engagement_rate', 0):.2f}%")
        print(f"👤 Username: @{scraped_data.get('username', 'N/A')}")
        print(f"👥 Followers: {scraped_data.get('followers', 0):,}")
    else:
        print("❌ Mobile scraping failed")
        if 'error' in scraped_data:
            print(f"Error: {scraped_data['error']}")
        else:
            print("Views: 0 - Need to try different approach")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return scraped_data

if __name__ == "__main__":
    asyncio.run(main())
