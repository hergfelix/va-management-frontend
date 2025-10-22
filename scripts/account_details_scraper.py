"""
Account Details Scraper - Sofia's Complete Profile
SuperClaude Account Analysis Specialist

Scraping all account details for @sofiatightlegs
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

class AccountDetailsScraper:
    """
    Comprehensive account details scraper
    """
    
    def __init__(self, headless=True, debug=True):
        self.headless = headless
        self.debug = debug
        self.browser = None
        self.page = None
        
    async def __aenter__(self):
        """Mobile browser setup for account scraping"""
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

    async def scrape_account_details(self, username: str) -> dict:
        """
        Scrape complete account details for username
        """
        try:
            # Create mobile context
            context = await self.browser.new_context(
                viewport={'width': 375, 'height': 812},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
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
            
            # Navigate to account profile
            account_url = f"https://www.tiktok.com/@{username}"
            logger.info(f"👤 Scraping account: {account_url}")
            
            await page.goto(account_url, wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)
            
            # Debug save
            if self.debug:
                page_content = await page.content()
                with open(f'sofia_account_debug_{username}.html', 'w', encoding='utf-8') as f:
                    f.write(page_content)
                logger.info(f"💾 Account debug saved: sofia_account_debug_{username}.html")
            
            # Extract all account details
            account_data = await self._extract_account_details(page, username)
            
            await context.close()
            return account_data
            
        except Exception as e:
            logger.error(f"❌ Account scraping failed: {e}")
            return {
                "username": username,
                "scraped_at": datetime.now().isoformat(),
                "error": str(e),
                "success": False
            }

    async def _extract_account_details(self, page, username):
        """Extract comprehensive account details"""
        data = {
            "username": username,
            "scraped_at": datetime.now().isoformat(),
            "success": True
        }
        
        try:
            # Get page content
            page_content = await page.content()
            
            # Extract basic account info
            logger.info("📊 Extracting basic account info...")
            data.update(await self._extract_basic_info(page, page_content))
            
            # Extract account statistics
            logger.info("📈 Extracting account statistics...")
            data.update(await self._extract_account_stats(page, page_content))
            
            # Extract account metadata
            logger.info("📋 Extracting account metadata...")
            data.update(await self._extract_account_metadata(page, page_content))
            
            # Extract recent posts info
            logger.info("📱 Extracting recent posts info...")
            data.update(await self._extract_recent_posts_info(page, page_content))
            
            # Extract account performance
            logger.info("🎯 Extracting account performance...")
            data.update(await self._extract_account_performance(page, page_content))
            
            logger.info("✅ Account details extraction completed")
            
        except Exception as e:
            logger.error(f"❌ Account extraction error: {e}")
            data["extraction_error"] = str(e)
            data["success"] = False
        
        return data

    async def _extract_basic_info(self, page, page_content):
        """Extract basic account information"""
        basic_info = {}
        
        try:
            # Display name
            display_name_patterns = [
                r'"nickname":"([^"]+)"',
                r'"displayName":"([^"]+)"',
                r'"name":"([^"]+)"'
            ]
            
            for pattern in display_name_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    basic_info["display_name"] = matches[0]
                    logger.info(f"✅ Display name: {basic_info['display_name']}")
                    break
            
            # Bio/Description
            bio_patterns = [
                r'"signature":"([^"]+)"',
                r'"bio":"([^"]+)"',
                r'"description":"([^"]+)"'
            ]
            
            for pattern in bio_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    basic_info["bio"] = matches[0]
                    logger.info(f"✅ Bio: {basic_info['bio'][:50]}...")
                    break
            
            # Profile picture
            avatar_patterns = [
                r'"avatarLarger":"([^"]+)"',
                r'"avatarMedium":"([^"]+)"',
                r'"avatarThumb":"([^"]+)"',
                r'"profilePicture":"([^"]+)"'
            ]
            
            for pattern in avatar_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    basic_info["profile_picture"] = matches[0]
                    logger.info(f"✅ Profile picture found")
                    break
            
            # Verification status
            verification_patterns = [
                r'"verified":(true|false)',
                r'"isVerified":(true|false)',
                r'"verifiedUser":(true|false)'
            ]
            
            for pattern in verification_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    basic_info["verified"] = matches[0] == 'true'
                    logger.info(f"✅ Verified: {basic_info['verified']}")
                    break
            
            # Account type/category
            type_patterns = [
                r'"accountType":"([^"]+)"',
                r'"userType":"([^"]+)"',
                r'"category":"([^"]+)"'
            ]
            
            for pattern in type_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    basic_info["account_type"] = matches[0]
                    logger.info(f"✅ Account type: {basic_info['account_type']}")
                    break
            
        except Exception as e:
            logger.error(f"❌ Basic info extraction error: {e}")
            basic_info["basic_info_error"] = str(e)
        
        return basic_info

    async def _extract_account_stats(self, page, page_content):
        """Extract account statistics"""
        stats = {}
        
        try:
            # Followers count
            follower_patterns = [
                r'"followerCount":(\d+)',
                r'"followers":(\d+)',
                r'"follower":(\d+)'
            ]
            
            for pattern in follower_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    stats["followers"] = int(matches[0])
                    logger.info(f"✅ Followers: {stats['followers']:,}")
                    break
            
            # Following count
            following_patterns = [
                r'"followingCount":(\d+)',
                r'"following":(\d+)',
                r'"followings":(\d+)'
            ]
            
            for pattern in following_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    stats["following"] = int(matches[0])
                    logger.info(f"✅ Following: {stats['following']:,}")
                    break
            
            # Total posts count
            posts_patterns = [
                r'"videoCount":(\d+)',
                r'"postCount":(\d+)',
                r'"totalPosts":(\d+)',
                r'"posts":(\d+)'
            ]
            
            for pattern in posts_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    stats["total_posts"] = int(matches[0])
                    logger.info(f"✅ Total posts: {stats['total_posts']:,}")
                    break
            
            # Total likes received
            likes_patterns = [
                r'"heartCount":(\d+)',
                r'"totalLikes":(\d+)',
                r'"likesReceived":(\d+)',
                r'"totalHearts":(\d+)'
            ]
            
            for pattern in likes_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    stats["total_likes_received"] = int(matches[0])
                    logger.info(f"✅ Total likes received: {stats['total_likes_received']:,}")
                    break
            
        except Exception as e:
            logger.error(f"❌ Stats extraction error: {e}")
            stats["stats_error"] = str(e)
        
        return stats

    async def _extract_account_metadata(self, page, page_content):
        """Extract account metadata"""
        metadata = {}
        
        try:
            # Account creation date
            creation_patterns = [
                r'"createTime":(\d+)',
                r'"createdAt":(\d+)',
                r'"joinDate":(\d+)',
                r'"registrationTime":(\d+)'
            ]
            
            for pattern in creation_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    timestamp = int(matches[0])
                    if timestamp > 1000000000:  # Unix timestamp
                        creation_date = datetime.fromtimestamp(timestamp)
                        metadata["account_created"] = creation_date.isoformat()
                        logger.info(f"✅ Account created: {creation_date.strftime('%Y-%m-%d')}")
                    break
            
            # Last active
            active_patterns = [
                r'"lastActiveTime":(\d+)',
                r'"lastSeen":(\d+)',
                r'"lastActivity":(\d+)'
            ]
            
            for pattern in active_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    timestamp = int(matches[0])
                    if timestamp > 1000000000:
                        last_active = datetime.fromtimestamp(timestamp)
                        metadata["last_active"] = last_active.isoformat()
                        logger.info(f"✅ Last active: {last_active.strftime('%Y-%m-%d %H:%M')}")
                    break
            
            # Account ID
            id_patterns = [
                r'"id":"([^"]+)"',
                r'"userId":"([^"]+)"',
                r'"uid":"([^"]+)"'
            ]
            
            for pattern in id_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    metadata["account_id"] = matches[0]
                    logger.info(f"✅ Account ID: {metadata['account_id']}")
                    break
            
            # Privacy settings
            privacy_patterns = [
                r'"privateAccount":(true|false)',
                r'"isPrivate":(true|false)',
                r'"privacyMode":(true|false)'
            ]
            
            for pattern in privacy_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    metadata["private_account"] = matches[0] == 'true'
                    logger.info(f"✅ Private account: {metadata['private_account']}")
                    break
            
        except Exception as e:
            logger.error(f"❌ Metadata extraction error: {e}")
            metadata["metadata_error"] = str(e)
        
        return metadata

    async def _extract_recent_posts_info(self, page, page_content):
        """Extract recent posts information"""
        posts_info = {}
        
        try:
            # Recent posts count (visible on profile)
            recent_posts_patterns = [
                r'"recentPosts":(\d+)',
                r'"visiblePosts":(\d+)',
                r'"profilePosts":(\d+)'
            ]
            
            for pattern in recent_posts_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    posts_info["recent_posts_count"] = int(matches[0])
                    logger.info(f"✅ Recent posts: {posts_info['recent_posts_count']}")
                    break
            
            # Average views per post
            avg_views_patterns = [
                r'"avgViews":(\d+)',
                r'"averageViews":(\d+)',
                r'"meanViews":(\d+)'
            ]
            
            for pattern in avg_views_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    posts_info["avg_views_per_post"] = int(matches[0])
                    logger.info(f"✅ Avg views per post: {posts_info['avg_views_per_post']:,}")
                    break
            
            # Average engagement rate
            avg_engagement_patterns = [
                r'"avgEngagementRate":([\d.]+)',
                r'"averageEngagement":([\d.]+)',
                r'"meanEngagement":([\d.]+)'
            ]
            
            for pattern in avg_engagement_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    posts_info["avg_engagement_rate"] = float(matches[0])
                    logger.info(f"✅ Avg engagement rate: {posts_info['avg_engagement_rate']:.2f}%")
                    break
            
        except Exception as e:
            logger.error(f"❌ Recent posts info extraction error: {e}")
            posts_info["posts_info_error"] = str(e)
        
        return posts_info

    async def _extract_account_performance(self, page, page_content):
        """Extract account performance metrics"""
        performance = {}
        
        try:
            # Account growth rate (if available)
            growth_patterns = [
                r'"growthRate":([\d.]+)',
                r'"followerGrowth":([\d.]+)',
                r'"growthPercentage":([\d.]+)'
            ]
            
            for pattern in growth_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    performance["growth_rate"] = float(matches[0])
                    logger.info(f"✅ Growth rate: {performance['growth_rate']:.2f}%")
                    break
            
            # Account quality score
            quality_patterns = [
                r'"qualityScore":([\d.]+)',
                r'"accountScore":([\d.]+)',
                r'"performanceScore":([\d.]+)'
            ]
            
            for pattern in quality_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    performance["quality_score"] = float(matches[0])
                    logger.info(f"✅ Quality score: {performance['quality_score']:.2f}")
                    break
            
            # Engagement quality
            engagement_quality_patterns = [
                r'"engagementQuality":([\d.]+)',
                r'"qualityEngagement":([\d.]+)',
                r'"engagementScore":([\d.]+)'
            ]
            
            for pattern in engagement_quality_patterns:
                matches = re.findall(pattern, page_content)
                if matches:
                    performance["engagement_quality"] = float(matches[0])
                    logger.info(f"✅ Engagement quality: {performance['engagement_quality']:.2f}")
                    break
            
        except Exception as e:
            logger.error(f"❌ Performance extraction error: {e}")
            performance["performance_error"] = str(e)
        
        return performance

async def main():
    """Main execution"""
    print("👤 ACCOUNT DETAILS SCRAPER - SOFIA'S PROFILE")
    print("=" * 60)
    
    username = "sofiatightlegs"
    
    print(f"👤 Target: @{username}")
    print(f"🔗 URL: https://www.tiktok.com/@{username}")
    print()
    
    # Scrape account details
    async with AccountDetailsScraper(headless=True, debug=True) as scraper:
        account_data = await scraper.scrape_account_details(username)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"sofia_account_details_{timestamp}.json"
    
    import json
    with open(output_file, 'w') as f:
        json.dump(account_data, f, indent=2, default=str)
    
    print("\n📊 ACCOUNT DETAILS RESULTS:")
    print("=" * 60)
    
    if account_data.get("success", False):
        print("✅ SUCCESS! Account details extracted!")
        print(f"👤 Username: @{account_data.get('username', 'N/A')}")
        print(f"📝 Display Name: {account_data.get('display_name', 'N/A')}")
        print(f"📄 Bio: {account_data.get('bio', 'N/A')[:100]}...")
        print(f"👥 Followers: {account_data.get('followers', 0):,}")
        print(f"👥 Following: {account_data.get('following', 0):,}")
        print(f"📱 Total Posts: {account_data.get('total_posts', 0):,}")
        print(f"❤️ Total Likes Received: {account_data.get('total_likes_received', 0):,}")
        print(f"✅ Verified: {account_data.get('verified', False)}")
        print(f"🔒 Private Account: {account_data.get('private_account', False)}")
        print(f"📅 Account Created: {account_data.get('account_created', 'N/A')}")
        print(f"🕒 Last Active: {account_data.get('last_active', 'N/A')}")
        print(f"📊 Avg Views per Post: {account_data.get('avg_views_per_post', 0):,}")
        print(f"📈 Avg Engagement Rate: {account_data.get('avg_engagement_rate', 0):.2f}%")
    else:
        print("❌ Account details extraction failed")
        if 'error' in account_data:
            print(f"Error: {account_data['error']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return account_data

if __name__ == "__main__":
    asyncio.run(main())
