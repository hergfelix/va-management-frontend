import asyncio
import pandas as pd
import time
import re
import logging
from datetime import datetime
from playwright.async_api import async_playwright
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TikTokAccountScraper:
    """
    Professional TikTok account follower scraper
    Extracts follower counts, account info, and growth metrics
    """
    
    def __init__(self, headless=True, debug=False):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        self.results = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
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

    async def scrape_account(self, username: str, va_name: str = None) -> dict:
        """
        Scrape a single TikTok account for follower count and metadata
        """
        try:
            # Create new page for each account
            page = await self.browser.new_page()
            
            # Set realistic user agent and headers
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to profile
            profile_url = f"https://www.tiktok.com/@{username}"
            logger.info(f"Scraping: {profile_url}")
            
            await page.goto(profile_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Debug: Save page content
            if self.debug:
                page_content = await page.content()
                with open(f'debug_profile_{username}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"Debug: Saved page content to debug_profile_{username}.html")
            
            # Extract account data
            account_data = await self._extract_account_data(page, username, va_name)
            
            await page.close()
            return account_data
            
        except Exception as e:
            logger.error(f"Failed to scrape {username}: {e}")
            return {
                "username": username,
                "va_name": va_name,
                "followers": 0,
                "following": 0,
                "likes": 0,
                "videos": 0,
                "bio": "",
                "verified": False,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }

    async def _extract_account_data(self, page, username: str, va_name: str) -> dict:
        """
        Extract comprehensive account data from profile page
        """
        account_data = {
            "username": username,
            "va_name": va_name,
            "scraped_at": datetime.now().isoformat(),
            "status": "success"
        }
        
        try:
            # Extract follower count - try multiple methods
            followers = await self._extract_followers_comprehensive(page)
            account_data["followers"] = followers
            
            # Extract following count
            following = await self._extract_metric(page, [
                '[data-e2e="following-count"]',
                'strong[data-e2e="following-count"]',
                'div[data-e2e="following-count"]',
                'span[data-e2e="following-count"]'
            ])
            account_data["following"] = following
            
            # Extract likes count
            likes = await self._extract_metric(page, [
                '[data-e2e="likes-count"]',
                'strong[data-e2e="likes-count"]',
                'div[data-e2e="likes-count"]',
                'span[data-e2e="likes-count"]'
            ])
            account_data["likes"] = likes
            
            # Extract video count
            videos = await self._extract_metric(page, [
                '[data-e2e="video-count"]',
                'strong[data-e2e="video-count"]',
                'div[data-e2e="video-count"]',
                'span[data-e2e="video-count"]'
            ])
            account_data["videos"] = videos
            
            # Extract bio
            bio = await self._extract_bio(page)
            account_data["bio"] = bio
            
            # Check if verified
            verified = await self._check_verified(page)
            account_data["verified"] = verified
            
            logger.info(f"Successfully scraped @{username}: {followers:,} followers")
            
        except Exception as e:
            logger.error(f"Error extracting data for @{username}: {e}")
            account_data["error"] = str(e)
            account_data["status"] = "partial"
        
        return account_data

    async def _extract_followers_comprehensive(self, page):
        """
        Comprehensive follower extraction with multiple methods
        """
        # Method 1: Extract from JSON data in page
        try:
            page_content = await page.content()
            
            # Look for follower count in JSON data
            follower_match = re.search(r'"followerCount":(\d+)', page_content)
            if follower_match:
                followers = int(follower_match.group(1))
                logger.info(f"Found followers in JSON data: {followers}")
                return followers
        except Exception as e:
            logger.debug(f"JSON extraction failed: {e}")
        
        # Method 2: Try follower selectors
        follower_selectors = [
            '[data-e2e="followers-count"]',
            '[data-e2e="follower-count"]',
            'strong[data-e2e="followers-count"]',
            'div[data-e2e="followers-count"]',
            'span[data-e2e="followers-count"]',
            '.follower-count',
            '.followers-count',
            '[class*="follower"]',
            '[class*="Follower"]'
        ]
        
        for selector in follower_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and self._looks_like_followers(text):
                        parsed = self._parse_metric(text)
                        if parsed > 0:
                            logger.info(f"Found followers with selector '{selector}': {text} -> {parsed}")
                            return parsed
            except Exception:
                continue
        
        # Method 3: Look for any element containing "followers"
        try:
            all_elements = await page.query_selector_all('span, div, strong, p, h1, h2, h3')
            for element in all_elements:
                text = await element.text_content()
                if text and 'followers' in text.lower():
                    parsed = self._parse_metric(text)
                    if parsed > 0:
                        logger.info(f"Found followers in text: {text} -> {parsed}")
                        return parsed
        except Exception:
            pass
        
        logger.warning("Could not extract followers with any method")
        return 0

    async def _extract_metric(self, page, selectors):
        """
        Try multiple selectors to extract a metric
        """
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        return self._parse_metric(text)
            except Exception:
                continue
        return 0

    async def _extract_bio(self, page):
        """
        Extract account bio/description
        """
        try:
            bio_selectors = [
                '[data-e2e="user-bio"]',
                '.user-bio',
                '.bio',
                '[class*="bio"]',
                'h1 + div',
                'h2 + div'
            ]
            
            for selector in bio_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        bio = await element.text_content()
                        if bio and len(bio.strip()) > 0:
                            return bio.strip()
                except Exception:
                    continue
        except Exception:
            pass
        
        return ""

    async def _check_verified(self, page):
        """
        Check if account is verified
        """
        try:
            verified_selectors = [
                '[data-e2e="verified-icon"]',
                '.verified',
                '[class*="verified"]',
                'svg[class*="verified"]'
            ]
            
            for selector in verified_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        
        return False

    def _looks_like_followers(self, text):
        """
        Check if text looks like follower count
        """
        text = str(text).lower().strip()
        return (
            'follower' in text and 
            any(char.isdigit() for char in text) and
            len(text) < 20
        )

    def _parse_metric(self, text: str) -> int:
        """
        Parse a metric string (e.g., "10.5K", "1.2M") into an integer
        """
        text = text.replace(',', '').strip()
        text = text.lower()

        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        elif 'b' in text:
            return int(float(text.replace('b', '')) * 1000000000)
        else:
            # Extract only digits
            digits = re.findall(r'\d+', text)
            if digits:
                return int("".join(digits))
            return 0

    async def scrape_accounts_batch(self, accounts: list, delay_between_accounts: float = 2.0) -> list:
        """
        Scrape multiple accounts with rate limiting
        """
        results = []
        total_accounts = len(accounts)
        
        logger.info(f"Starting batch scraping of {total_accounts} accounts")
        
        for i, account in enumerate(accounts, 1):
            username = account.get('username', account.get('account', ''))
            va_name = account.get('va_name', account.get('va', ''))
            
            logger.info(f"Scraping account {i}/{total_accounts}: @{username}")
            
            try:
                result = await self.scrape_account(username, va_name)
                results.append(result)
                
                # Rate limiting
                if i < total_accounts:
                    await asyncio.sleep(delay_between_accounts)
                    
            except Exception as e:
                logger.error(f"Failed to scrape @{username}: {e}")
                results.append({
                    "username": username,
                    "va_name": va_name,
                    "followers": 0,
                    "following": 0,
                    "likes": 0,
                    "videos": 0,
                    "bio": "",
                    "verified": False,
                    "scraped_at": datetime.now().isoformat(),
                    "error": str(e),
                    "status": "failed"
                })
        
        logger.info(f"Batch scraping completed: {len(results)} results")
        return results

async def main():
    """
    Main function to scrape Miriam accounts
    """
    # Load accounts from CSV
    csv_path = '/Users/felixhergenroeder/Downloads/Tiktok Tracking Sheet - MIRIAMUS.csv'
    
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return
    
    # Extract accounts from CSV
    df = pd.read_csv(csv_path)
    
    # Find account names and followers (rows 5 and 6)
    account_row = df.iloc[5]  # Row 6 (0-indexed)
    follower_row = df.iloc[6]  # Row 7
    
    # Extract accounts
    accounts = []
    for i, (account, followers) in enumerate(zip(account_row, follower_row)):
        if pd.notna(account) and str(account).strip() and account != 'Account name':
            account_name = str(account).strip()
            if 'miriam' in account_name.lower() and len(account_name) > 3:
                # Determine VA based on column position (from your CSV structure)
                va_mapping = {
                    1: 'CARLA', 2: 'JAROLD', 3: 'AARON', 4: 'JOSUHA', 
                    5: 'GRASHANG', 6: 'JAIRIS', 7: 'SAMUEL', 8: 'LIYA'
                }
                va_name = va_mapping.get(i, 'UNKNOWN')
                
                accounts.append({
                    'username': account_name,
                    'va_name': va_name,
                    'current_followers': int(followers) if pd.notna(followers) and str(followers).isdigit() else 0
                })
    
    logger.info(f"Found {len(accounts)} Miriam accounts to scrape")
    
    # Scrape accounts
    async with TikTokAccountScraper(headless=True, debug=False) as scraper:
        results = await scraper.scrape_accounts_batch(accounts, delay_between_accounts=3.0)
    
    # Save results
    results_df = pd.DataFrame(results)
    output_file = 'miriam_accounts_scraped.csv'
    results_df.to_csv(output_file, index=False)
    
    logger.info(f"Results saved to: {output_file}")
    
    # Print summary
    successful_scrapes = results_df[results_df['status'] == 'success']
    total_followers = successful_scrapes['followers'].sum()
    
    print(f"\n🎯 SCRAPING RESULTS SUMMARY")
    print(f"=" * 50)
    print(f"✅ Successfully scraped: {len(successful_scrapes)}/{len(accounts)} accounts")
    print(f"📈 Total followers: {total_followers:,}")
    print(f"📊 Average followers: {total_followers/len(successful_scrapes):,.0f}" if len(successful_scrapes) > 0 else "📊 Average followers: 0")
    print(f"🏆 Largest account: {successful_scrapes['followers'].max():,} followers" if len(successful_scrapes) > 0 else "🏆 Largest account: 0 followers")
    
    return results_df

if __name__ == "__main__":
    asyncio.run(main())
