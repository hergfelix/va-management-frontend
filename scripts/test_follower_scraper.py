import asyncio
import pandas as pd
import time
import re
import logging
from datetime import datetime
from playwright.async_api import async_playwright

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFollowerScraper:
    """
    Simple TikTok follower scraper for testing
    """
    
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scrape_followers(self, username: str) -> dict:
        """
        Scrape follower count for a single account
        """
        try:
            page = await self.browser.new_page()
            
            # Set realistic headers
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            profile_url = f"https://www.tiktok.com/@{username}"
            logger.info(f"Scraping: {profile_url}")
            
            await page.goto(profile_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Try to extract follower count
            followers = 0
            
            # Method 1: Look for follower count in page content
            page_content = await page.content()
            
            # Look for follower count in JSON data
            follower_match = re.search(r'"followerCount":(\d+)', page_content)
            if follower_match:
                followers = int(follower_match.group(1))
                logger.info(f"Found followers in JSON: {followers}")
            else:
                # Method 2: Try selectors
                follower_selectors = [
                    '[data-e2e="followers-count"]',
                    '[data-e2e="follower-count"]',
                    'strong[data-e2e="followers-count"]',
                    'div[data-e2e="followers-count"]'
                ]
                
                for selector in follower_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.text_content()
                            if text and 'follower' in text.lower():
                                # Parse the number
                                numbers = re.findall(r'[\d,]+', text)
                                if numbers:
                                    followers = int(numbers[0].replace(',', ''))
                                    logger.info(f"Found followers with selector: {followers}")
                                    break
                    except Exception:
                        continue
            
            await page.close()
            
            return {
                "username": username,
                "followers": followers,
                "scraped_at": datetime.now().isoformat(),
                "status": "success" if followers > 0 else "no_data"
            }
            
        except Exception as e:
            logger.error(f"Failed to scrape @{username}: {e}")
            return {
                "username": username,
                "followers": 0,
                "scraped_at": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }

async def test_scraper():
    """
    Test the scraper with a few accounts
    """
    # Load clean accounts
    df = pd.read_csv('miriam_accounts_clean.csv')
    
    # Test with top 5 accounts
    test_accounts = df.head(5)['username'].tolist()
    
    print(f"🧪 TESTING FOLLOWER SCRAPER")
    print(f"=" * 50)
    print(f"Testing with {len(test_accounts)} accounts:")
    for i, account in enumerate(test_accounts, 1):
        print(f"  {i}. @{account}")
    print()
    
    results = []
    
    async with SimpleFollowerScraper(headless=True) as scraper:
        for i, username in enumerate(test_accounts, 1):
            print(f"📊 Scraping {i}/{len(test_accounts)}: @{username}")
            
            result = await scraper.scrape_followers(username)
            results.append(result)
            
            print(f"   Result: {result['followers']:,} followers ({result['status']})")
            
            # Rate limiting
            if i < len(test_accounts):
                await asyncio.sleep(3)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv('test_scraper_results.csv', index=False)
    
    print(f"\n🎯 TEST RESULTS:")
    print(f"=" * 50)
    successful = results_df[results_df['status'] == 'success']
    print(f"✅ Successful scrapes: {len(successful)}/{len(results)}")
    
    if len(successful) > 0:
        total_followers = successful['followers'].sum()
        print(f"📈 Total followers scraped: {total_followers:,}")
        print(f"📊 Average followers: {total_followers/len(successful):,.0f}")
    
    print(f"\n💾 Results saved to: test_scraper_results.csv")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(test_scraper())
