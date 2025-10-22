"""
Test Working URLs
SuperClaude Test Working TikTok URLs

Test the URLs that actually worked 4 hours ago
"""

import asyncio
import pandas as pd
import time
import re
from datetime import datetime
from playwright.async_api import async_playwright
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestWorkingURLs:
    """
    Test the URLs that actually worked 4 hours ago
    """
    
    def __init__(self, headless=True, debug=False):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.playwright = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def test_working_urls(self):
        """
        Test the URLs that actually worked 4 hours ago
        """
        # URLs that actually worked 4 hours ago
        working_urls = [
            "https://www.tiktok.com/t/ZTMmT78be/",  # Mara - 313 views
            "https://www.tiktok.com/t/ZTMmTvGqd/",  # Sofia - 1,693 views
            "https://www.tiktok.com/t/ZP8AWUGAJ/"   # Tyra - 125 views
        ]
        
        results = []
        
        for i, url in enumerate(working_urls, 1):
            try:
                # Create new page
                page = await self.browser.new_page()
                
                # Set realistic user agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # Set viewport
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                logger.info(f"🎯 Testing working URL {i}/{len(working_urls)}: {url}")
                
                # Navigate to post
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                await page.wait_for_timeout(3000)
                
                # Debug: Save page content for analysis
                if self.debug:
                    page_content = await page.content()
                    url_id = url.split('/')[-2] if '/' in url else 'unknown'
                    with open(f'test_working_debug_{url_id}.html', 'w', encoding='utf-8') as f:
                        f.write(page_content)
                    logger.info(f"🎯 Test working debug: Saved page content to test_working_debug_{url_id}.html")
                
                # Extract views using the same method
                views = await self._extract_views(page)
                
                await page.close()
                
                results.append({
                    "url": url,
                    "views": views,
                    "status": "success" if views > 0 else "no_data"
                })
                
                logger.info(f"🎯 Test working result: {url} - Views: {views}")
                
            except Exception as e:
                logger.error(f"❌ Test working failed {url}: {e}")
                results.append({
                    "url": url,
                    "views": 0,
                    "status": "failed",
                    "error": str(e)
                })
            
            # Add delay between tests
            if i < len(working_urls):
                await asyncio.sleep(2)
        
        return results
    
    async def _extract_views(self, page):
        """
        Extract views using the same method that worked
        """
        try:
            page_content = await page.content()
            
            # Look for playCount in the JSON data
            playcount_match = re.search(r'"playCount":(\d+)', page_content)
            if playcount_match:
                views = int(playcount_match.group(1))
                logger.info(f"🎯 Test working: Found views in JSON data: {views}")
                return views
        except Exception as e:
            logger.debug(f"🎯 Test working JSON extraction failed: {e}")
        
        # Try selectors
        view_selectors = [
            '[data-e2e="video-views"]',
            'strong[data-e2e="video-views"]',
            'span[data-e2e="video-views"]',
            '[class*="view"] strong',
            '[class*="View"] strong'
        ]
        
        for selector in view_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"🎯 Test working: Found views with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        logger.warning("🎯 Test working: Could not extract views with any method")
        return 0
    
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

async def main():
    """Main execution"""
    print("🎯 TEST WORKING URLs")
    print("=" * 60)
    print("🚀 Testing the URLs that actually worked 4 hours ago!")
    print()
    
    async with TestWorkingURLs(headless=True, debug=True) as tester:
        results = await tester.test_working_urls()
    
    print("\n🎯 TEST WORKING RESULTS:")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n📹 TEST {i}: {result['url']}")
        print(f"   Views: {result['views']:,}")
        print(f"   Status: {result['status']}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    no_data = len([r for r in results if r['status'] == 'no_data'])
    failed = len([r for r in results if r['status'] == 'failed'])
    total_views = sum(r['views'] for r in results)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Successful: {successful}/{len(results)}")
    print(f"   No Data: {no_data}/{len(results)}")
    print(f"   Failed: {failed}/{len(results)}")
    print(f"   Total Views: {total_views:,}")
    
    if successful > 0:
        print("\n✅ SUCCESS! The working URLs still work!")
        print("💡 The problem is that your new URLs are different!")
    elif no_data > 0:
        print("\n⚠️ PARTIAL! URLs load but no data extracted!")
        print("💡 TikTok might have changed their structure!")
    else:
        print("\n❌ FAILED! Even the working URLs don't work anymore!")
        print("💡 TikTok has definitely changed something!")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
