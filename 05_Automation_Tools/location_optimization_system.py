#!/usr/bin/env python3
"""
TikTok USA Audience Optimization System
Automates location percentage management and audience targeting

Core Features:
1. Location Percentage Monitoring
2. AI Profile Analysis (USA vs Non-USA)
3. Automated Warm-up Engagement
4. Intelligent Comment Management
5. Optimal Posting Time Calculator
6. Sound Verification System
7. Real-time Dashboard Integration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
import pytz
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
import time as time_module

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocationOptimizationSystem:
    """
    Main system for TikTok USA audience optimization
    """
    
    def __init__(self, database_url: str, tiktok_session_cookies: str = None):
        self.db_engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.db_engine)
        self.tiktok_cookies = tiktok_session_cookies
        
        # USA Signal Detection Patterns
        self.usa_patterns = {
            'flags': [r'🇺🇸', r'🇺🇲', r'usa', r'america'],
            'states': [
                'texas', 'ohio', 'alabama', 'florida', 'idaho', 'tennessee',
                'california', 'new york', 'illinois', 'pennsylvania', 'georgia'
            ],
            'cities': [
                'houston', 'dallas', 'austin', 'miami', 'atlanta', 'chicago',
                'phoenix', 'philadelphia', 'san antonio', 'san diego'
            ],
            'slang': [r'\by\'all\b', r'\bain\'t\b', r'\bbro\b', r'\bbuddy\b'],
            'blue_collar': [
                'pickup truck', 'construction', 'toolbelt', 'worksite',
                'country road', 'trucker', 'blue collar', 'bubba truck'
            ],
            'music_genres': ['country music', 'classic rock', 'truck engine']
        }
        
        # Non-USA Detection Patterns
        self.non_usa_patterns = {
            'languages': [
                r'[ا-ي]',  # Arabic
                r'[ह-ह]',  # Hindi
                r'[中-龯]',  # Chinese
                r'[あ-ん]',  # Japanese
                r'[가-힣]',  # Korean
                r'[а-яё]',  # Russian
                r'[α-ω]'   # Greek
            ],
            'currencies': ['€', '£', '¥', '₹', '₽', 'kr'],
            'regions': ['europe', 'asia', 'middle east', 'africa']
        }
        
        # Optimal posting times (PHT)
        self.optimal_posting_windows = [
            (time(6, 0), time(12, 0)),   # Morning to Midday
            (time(22, 0), time(23, 59))  # Late Night
        ]
        
        # Warm-up keywords for USA engagement
        self.warmup_keywords = [
            "USA pickup truck", "old pickup truck USA", "blue collar USA",
            "construction Texas", "American trucker", "Bubba truck",
            "country road USA", "truck driver America", "USA construction worker"
        ]

    @dataclass
    class LocationMetrics:
        """Location percentage and audience data"""
        usa_percentage: float
        non_usa_percentage: float
        total_audience: int
        usa_engagements: int
        non_usa_engagements: int
        last_updated: datetime
        confidence_score: float  # 0-1, how confident we are in this data

    @dataclass
    class ProfileAnalysis:
        """Analysis result for a TikTok profile"""
        is_usa: bool
        confidence: float
        signals: List[str]
        risk_factors: List[str]
        recommendation: str

    @dataclass
    class WarmupSession:
        """Warm-up engagement session data"""
        session_id: str
        start_time: datetime
        duration_minutes: int
        keywords_searched: List[str]
        profiles_engaged: List[str]
        comments_made: int
        follows_made: int
        usa_signals_strengthened: int

    async def analyze_profile_usa_signals(self, profile_data: Dict[str, Any]) -> ProfileAnalysis:
        """
        AI-powered analysis to determine if a profile is USA-based
        
        Args:
            profile_data: Dict containing username, bio, posts, followers, etc.
            
        Returns:
            ProfileAnalysis with USA detection results
        """
        signals = []
        risk_factors = []
        confidence = 0.0
        
        # Analyze bio text
        bio_text = profile_data.get('bio', '').lower()
        display_name = profile_data.get('display_name', '').lower()
        username = profile_data.get('username', '').lower()
        
        # Check USA positive signals
        for category, patterns in self.usa_patterns.items():
            for pattern in patterns:
                if re.search(pattern, bio_text + ' ' + display_name + ' ' + username, re.IGNORECASE):
                    signals.append(f"{category}: {pattern}")
                    confidence += 0.15
        
        # Check non-USA risk factors
        for category, patterns in self.non_usa_patterns.items():
            for pattern in patterns:
                if re.search(pattern, bio_text + ' ' + display_name + ' ' + username, re.IGNORECASE):
                    risk_factors.append(f"{category}: {pattern}")
                    confidence -= 0.2
        
        # Analyze recent posts for content signals
        recent_posts = profile_data.get('recent_posts', [])
        usa_content_signals = 0
        for post in recent_posts[:5]:  # Check last 5 posts
            post_text = (post.get('description', '') + ' ' + 
                        ' '.join(post.get('hashtags', []))).lower()
            
            for pattern in self.usa_patterns['blue_collar'] + self.usa_patterns['states']:
                if pattern in post_text:
                    usa_content_signals += 1
                    break
        
        if usa_content_signals >= 3:
            signals.append("Strong USA content focus")
            confidence += 0.3
        elif usa_content_signals == 0:
            risk_factors.append("No USA content signals")
            confidence -= 0.2
        
        # Analyze follower network
        followers_sample = profile_data.get('followers_sample', [])
        usa_followers = 0
        for follower in followers_sample[:10]:
            if self._quick_usa_check(follower.get('username', '')):
                usa_followers += 1
        
        follower_usa_ratio = usa_followers / len(followers_sample) if followers_sample else 0
        if follower_usa_ratio > 0.7:
            signals.append("High USA follower ratio")
            confidence += 0.2
        elif follower_usa_ratio < 0.3:
            risk_factors.append("Low USA follower ratio")
            confidence -= 0.15
        
        # Determine final recommendation
        is_usa = confidence > 0.3 and len(risk_factors) < len(signals)
        
        if is_usa:
            recommendation = "✅ SAFE TO ENGAGE - Strong USA signals detected"
        else:
            recommendation = "❌ AVOID - Non-USA or unclear signals detected"
        
        return ProfileAnalysis(
            is_usa=is_usa,
            confidence=min(max(confidence, 0.0), 1.0),
            signals=signals,
            risk_factors=risk_factors,
            recommendation=recommendation
        )

    def _quick_usa_check(self, text: str) -> bool:
        """Quick USA signal check for usernames/bios"""
        text_lower = text.lower()
        return any(
            pattern in text_lower 
            for pattern in ['usa', '🇺🇸', 'america', 'texas', 'florida', 'california']
        )

    async def get_current_location_percentage(self, account_username: str) -> LocationMetrics:
        """
        Get current USA location percentage for an account
        
        This would integrate with TikTok's analytics API or scrape the data
        """
        # This is a placeholder - in reality, you'd need to:
        # 1. Access TikTok's analytics dashboard
        # 2. Scrape the audience demographics data
        # 3. Parse the location percentages
        
        session = self.Session()
        try:
            # Get recent posts for this account
            recent_posts = session.execute(text("""
                SELECT views, likes, comments, shares, created_date
                FROM posts 
                WHERE account = :account 
                ORDER BY created_date DESC 
                LIMIT 10
            """), {"account": account_username}).fetchall()
            
            # Calculate estimated USA percentage based on engagement patterns
            # This is a simplified approach - real implementation would use actual analytics data
            
            total_engagement = sum(post.views + post.likes + post.comments for post in recent_posts)
            
            # Placeholder calculation - replace with actual analytics scraping
            estimated_usa_percentage = 85.0  # This would come from actual TikTok analytics
            
            return LocationMetrics(
                usa_percentage=estimated_usa_percentage,
                non_usa_percentage=100 - estimated_usa_percentage,
                total_audience=total_engagement,
                usa_engagements=int(total_engagement * estimated_usa_percentage / 100),
                non_usa_engagements=int(total_engagement * (100 - estimated_usa_percentage) / 100),
                last_updated=datetime.utcnow(),
                confidence_score=0.8
            )
            
        finally:
            session.close()

    async def execute_warmup_session(self, account_username: str, duration_minutes: int = 30) -> WarmupSession:
        """
        Execute automated warm-up session to strengthen USA signals
        
        Args:
            account_username: TikTok account to warm up
            duration_minutes: Duration of warm-up session
            
        Returns:
            WarmupSession with engagement data
        """
        session_id = f"warmup_{account_username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.utcnow()
        
        logger.info(f"🔥 Starting warm-up session for {account_username}")
        
        # Initialize browser for TikTok interaction
        driver = self._setup_browser()
        
        try:
            keywords_searched = []
            profiles_engaged = []
            comments_made = 0
            follows_made = 0
            usa_signals_strengthened = 0
            
            # Search for USA-specific content
            for keyword in self.warmup_keywords[:5]:  # Limit to 5 keywords
                logger.info(f"🔍 Searching for: {keyword}")
                keywords_searched.append(keyword)
                
                # Navigate to search
                search_url = f"https://www.tiktok.com/search?q={keyword.replace(' ', '%20')}"
                driver.get(search_url)
                
                # Wait for results to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='search-card-item']"))
                )
                
                # Get first few video results
                video_elements = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='search-card-item']")[:3]
                
                for video_element in video_elements:
                    try:
                        # Click on video
                        video_element.click()
                        
                        # Wait for video to load
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='browse-video']"))
                        )
                        
                        # Watch video for full duration (simulate real viewing)
                        time_module.sleep(3)
                        
                        # Get creator info
                        creator_element = driver.find_element(By.CSS_SELECTOR, "[data-e2e='video-author-uniqueid']")
                        creator_username = creator_element.text.replace('@', '')
                        
                        # Analyze creator profile
                        creator_data = await self._scrape_profile_data(driver, creator_username)
                        profile_analysis = await self.analyze_profile_usa_signals(creator_data)
                        
                        if profile_analysis.is_usa and profile_analysis.confidence > 0.6:
                            # Engage with USA creator
                            await self._engage_with_usa_creator(driver, creator_username)
                            profiles_engaged.append(creator_username)
                            usa_signals_strengthened += 1
                            
                            # Make authentic comment
                            comment = self._generate_authentic_comment(keyword)
                            if await self._post_comment(driver, comment):
                                comments_made += 1
                            
                            # Follow if appropriate
                            if await self._follow_creator(driver, creator_username):
                                follows_made += 1
                        
                        # Go back to search results
                        driver.back()
                        time_module.sleep(2)
                        
                    except Exception as e:
                        logger.warning(f"Error processing video: {e}")
                        continue
                
                # Small delay between keywords
                time_module.sleep(5)
            
            return WarmupSession(
                session_id=session_id,
                start_time=start_time,
                duration_minutes=duration_minutes,
                keywords_searched=keywords_searched,
                profiles_engaged=profiles_engaged,
                comments_made=comments_made,
                follows_made=follows_made,
                usa_signals_strengthened=usa_signals_strengthened
            )
            
        finally:
            driver.quit()

    def _setup_browser(self):
        """Setup Chrome browser with TikTok-optimized settings"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to appear more human
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    async def _scrape_profile_data(self, driver, username: str) -> Dict[str, Any]:
        """Scrape profile data for analysis"""
        try:
            profile_url = f"https://www.tiktok.com/@{username}"
            driver.get(profile_url)
            
            # Wait for profile to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='user-title']"))
            )
            
            # Extract profile data
            profile_data = {
                'username': username,
                'display_name': driver.find_element(By.CSS_SELECTOR, "[data-e2e='user-title']").text,
                'bio': driver.find_element(By.CSS_SELECTOR, "[data-e2e='user-bio']").text,
                'followers': driver.find_element(By.CSS_SELECTOR, "[data-e2e='followers-count']").text,
                'following': driver.find_element(By.CSS_SELECTOR, "[data-e2e='following-count']").text,
                'recent_posts': []
            }
            
            # Get recent posts
            post_elements = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='user-post-item']")[:5]
            for post_element in post_elements:
                try:
                    post_data = {
                        'description': post_element.find_element(By.CSS_SELECTOR, "[data-e2e='user-post-item-desc']").text,
                        'hashtags': [tag.text for tag in post_element.find_elements(By.CSS_SELECTOR, "a[href*='hashtag']")]
                    }
                    profile_data['recent_posts'].append(post_data)
                except:
                    continue
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error scraping profile {username}: {e}")
            return {'username': username, 'display_name': '', 'bio': '', 'recent_posts': []}

    async def _engage_with_usa_creator(self, driver, username: str):
        """Engage with a verified USA creator"""
        try:
            # Like their recent posts (simulate natural behavior)
            like_buttons = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='browse-like']")
            if like_buttons:
                like_buttons[0].click()
                time_module.sleep(1)
            
            # Follow if not already following
            follow_button = driver.find_element(By.CSS_SELECTOR, "[data-e2e='follow-button']")
            if follow_button and "Follow" in follow_button.text:
                follow_button.click()
                time_module.sleep(1)
                
        except Exception as e:
            logger.warning(f"Error engaging with {username}: {e}")

    def _generate_authentic_comment(self, keyword: str) -> str:
        """Generate authentic USA-style comments"""
        comments = {
            "USA pickup truck": ["Looks like a classic Texas truck! 🇺🇸", "Nice ride bro! Where you from?"],
            "old pickup truck USA": ["That's a real American classic right there", "Love seeing these old trucks still running"],
            "blue collar USA": ["Respect the hustle 💪", "Hard work pays off, brother"],
            "construction Texas": ["Texas construction workers are built different", "Y'all work hard out there"],
            "American trucker": ["Truckers keep America moving 🇺🇸", "Safe travels on the road"],
            "Bubba truck": ["That's a proper Bubba truck right there", "Built Ford tough! 🇺🇸"]
        }
        
        import random
        return random.choice(comments.get(keyword, ["Nice post! 🇺🇸", "Great content bro"]))

    async def _post_comment(self, driver, comment: str) -> bool:
        """Post a comment on current video"""
        try:
            comment_input = driver.find_element(By.CSS_SELECTOR, "[data-e2e='comment-input']")
            comment_input.click()
            comment_input.send_keys(comment)
            
            post_button = driver.find_element(By.CSS_SELECTOR, "[data-e2e='comment-post']")
            post_button.click()
            
            time_module.sleep(2)
            return True
            
        except Exception as e:
            logger.warning(f"Error posting comment: {e}")
            return False

    async def _follow_creator(self, driver, username: str) -> bool:
        """Follow a creator"""
        try:
            follow_button = driver.find_element(By.CSS_SELECTOR, "[data-e2e='follow-button']")
            if follow_button and "Follow" in follow_button.text:
                follow_button.click()
                time_module.sleep(1)
                return True
        except Exception as e:
            logger.warning(f"Error following {username}: {e}")
        
        return False

    def calculate_optimal_posting_time(self, target_timezone: str = "America/New_York") -> List[Tuple[time, time]]:
        """
        Calculate optimal posting times based on target audience timezone
        
        Args:
            target_timezone: Target audience timezone (default: Eastern Time)
            
        Returns:
            List of optimal posting time windows
        """
        target_tz = pytz.timezone(target_timezone)
        pht = pytz.timezone("Asia/Manila")
        
        optimal_windows = []
        
        # Convert PHT optimal windows to target timezone
        for pht_start, pht_end in self.optimal_posting_windows:
            # Create datetime objects in PHT
            pht_dt_start = pht.localize(datetime.combine(datetime.today(), pht_start))
            pht_dt_end = pht.localize(datetime.combine(datetime.today(), pht_end))
            
            # Convert to target timezone
            target_dt_start = pht_dt_start.astimezone(target_tz)
            target_dt_end = pht_dt_end.astimezone(target_tz)
            
            optimal_windows.append((target_dt_start.time(), target_dt_end.time()))
        
        return optimal_windows

    async def analyze_sound_usa_audience(self, sound_url: str) -> Dict[str, Any]:
        """
        Analyze if a sound is popular with USA audience
        
        Args:
            sound_url: TikTok sound URL
            
        Returns:
            Analysis results with USA audience metrics
        """
        # This would integrate with TikTok's sound analytics
        # For now, return placeholder data
        
        return {
            'sound_url': sound_url,
            'usa_usage_percentage': 75.0,
            'total_uses': 12500,
            'usa_creators_using': 8900,
            'top_usa_creators': ['@texastrucker', '@floridabuilder', '@californiatrades'],
            'recommendation': '✅ GOOD - High USA usage detected',
            'confidence': 0.8
        }

    async def manage_post_comments(self, post_url: str, location_metrics: LocationMetrics) -> Dict[str, Any]:
        """
        Intelligently manage comments based on location percentage
        
        Args:
            post_url: TikTok post URL
            location_metrics: Current location metrics
            
        Returns:
            Comment management results
        """
        session = self.Session()
        try:
            # Get post comments
            comments = await self._scrape_post_comments(post_url)
            
            managed_comments = {
                'total_comments': len(comments),
                'usa_comments_replied': 0,
                'non_usa_comments_hidden': 0,
                'conversations_started': 0,
                'recommendations': []
            }
            
            for comment in comments:
                commenter_data = await self._scrape_profile_data(self._setup_browser(), comment['username'])
                profile_analysis = await self.analyze_profile_usa_signals(commenter_data)
                
                if location_metrics.usa_percentage >= 95:
                    # High USA % - reply to all comments
                    await self._reply_to_comment(post_url, comment['id'], self._generate_engagement_question())
                    managed_comments['usa_comments_replied'] += 1
                    managed_comments['conversations_started'] += 1
                    
                elif location_metrics.usa_percentage < 95:
                    # Lower USA % - only reply to confirmed USA users
                    if profile_analysis.is_usa and profile_analysis.confidence > 0.7:
                        await self._reply_to_comment(post_url, comment['id'], self._generate_engagement_question())
                        managed_comments['usa_comments_replied'] += 1
                        managed_comments['conversations_started'] += 1
                    else:
                        # Hide or delete non-USA comments
                        await self._hide_comment(post_url, comment['id'])
                        managed_comments['non_usa_comments_hidden'] += 1
            
            # Generate recommendations
            if location_metrics.usa_percentage < 70:
                managed_comments['recommendations'].append(
                    "🚨 URGENT: USA % below 70%. Execute full 30-min warm-up session immediately."
                )
            elif location_metrics.usa_percentage < 95:
                managed_comments['recommendations'].append(
                    "⚠️ USA % below 95%. Continue selective engagement with USA users only."
                )
            else:
                managed_comments['recommendations'].append(
                    "✅ Excellent USA %. Continue current engagement strategy."
                )
            
            return managed_comments
            
        finally:
            session.close()

    def _generate_engagement_question(self) -> str:
        """Generate open-ended questions to drive engagement"""
        questions = [
            "Where you from?",
            "Thank you, how are you doing?",
            "What do you think about this?",
            "Have you experienced this before?",
            "What's your take on this?",
            "Thanks for watching! What's your story?"
        ]
        
        import random
        return random.choice(questions)

    async def monitor_location_percentage(self, account_username: str) -> Dict[str, Any]:
        """
        Continuous monitoring of location percentage with alerts
        
        Args:
            account_username: Account to monitor
            
        Returns:
            Monitoring results and recommendations
        """
        current_metrics = await self.get_current_location_percentage(account_username)
        
        monitoring_results = {
            'account': account_username,
            'current_usa_percentage': current_metrics.usa_percentage,
            'trend': 'stable',  # Would calculate from historical data
            'alerts': [],
            'recommendations': [],
            'next_warmup_needed': False,
            'warmup_intensity': 'maintenance'
        }
        
        # Generate alerts and recommendations
        if current_metrics.usa_percentage < 70:
            monitoring_results['alerts'].append("🚨 CRITICAL: USA % below 70%")
            monitoring_results['recommendations'].append("Execute full 30-min warm-up session immediately")
            monitoring_results['next_warmup_needed'] = True
            monitoring_results['warmup_intensity'] = 'intensive'
            
        elif current_metrics.usa_percentage < 95:
            monitoring_results['alerts'].append("⚠️ WARNING: USA % below 95%")
            monitoring_results['recommendations'].append("Execute 10-min maintenance warm-up before next post")
            monitoring_results['next_warmup_needed'] = True
            monitoring_results['warmup_intensity'] = 'maintenance'
            
        else:
            monitoring_results['alerts'].append("✅ GOOD: USA % above 95%")
            monitoring_results['recommendations'].append("Continue current strategy")
            monitoring_results['warmup_intensity'] = 'maintenance'
        
        # Check posting time optimization
        optimal_windows = self.calculate_optimal_posting_time()
        current_time = datetime.now().time()
        
        in_optimal_window = any(
            start <= current_time <= end for start, end in optimal_windows
        )
        
        if not in_optimal_window:
            monitoring_results['recommendations'].append(
                f"⏰ Avoid posting now. Optimal windows: {optimal_windows}"
            )
        
        return monitoring_results

    async def generate_daily_report(self, account_username: str) -> Dict[str, Any]:
        """Generate comprehensive daily location optimization report"""
        
        location_metrics = await self.get_current_location_percentage(account_username)
        monitoring_results = await self.monitor_location_percentage(account_username)
        
        # Get recent warm-up sessions
        session = self.Session()
        try:
            recent_sessions = session.execute(text("""
                SELECT * FROM warmup_sessions 
                WHERE account = :account 
                AND created_at >= :date
                ORDER BY created_at DESC
            """), {
                "account": account_username,
                "date": datetime.utcnow().date()
            }).fetchall()
            
        finally:
            session.close()
        
        report = {
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'account': account_username,
            'location_metrics': {
                'usa_percentage': location_metrics.usa_percentage,
                'total_audience': location_metrics.total_audience,
                'last_updated': location_metrics.last_updated.isoformat()
            },
            'monitoring_alerts': monitoring_results['alerts'],
            'recommendations': monitoring_results['recommendations'],
            'warmup_sessions_today': len(recent_sessions),
            'next_optimal_posting': self.calculate_optimal_posting_time(),
            'sound_verification_needed': location_metrics.usa_percentage < 95,
            'comment_management_active': True,
            'system_status': 'operational'
        }
        
        return report

# Example usage and integration functions
async def main():
    """Example usage of the Location Optimization System"""
    
    # Initialize system
    system = LocationOptimizationSystem(
        database_url="sqlite:///tiktok_analytics.db",
        tiktok_session_cookies="path/to/cookies.json"
    )
    
    account_username = "example_account"
    
    # Get current location metrics
    print("📊 Getting current location metrics...")
    location_metrics = await system.get_current_location_percentage(account_username)
    print(f"USA Percentage: {location_metrics.usa_percentage}%")
    
    # Monitor location percentage
    print("\n🔍 Monitoring location percentage...")
    monitoring_results = await system.monitor_location_percentage(account_username)
    for alert in monitoring_results['alerts']:
        print(f"Alert: {alert}")
    
    # Execute warm-up if needed
    if monitoring_results['next_warmup_needed']:
        print(f"\n🔥 Executing {monitoring_results['warmup_intensity']} warm-up session...")
        warmup_session = await system.execute_warmup_session(
            account_username, 
            duration_minutes=30 if monitoring_results['warmup_intensity'] == 'intensive' else 10
        )
        print(f"Warm-up completed: {warmup_session.comments_made} comments, {warmup_session.follows_made} follows")
    
    # Generate daily report
    print("\n📋 Generating daily report...")
    daily_report = await system.generate_daily_report(account_username)
    print(f"Report generated for {daily_report['date']}")

if __name__ == "__main__":
    asyncio.run(main())
