#!/usr/bin/env python3
"""
Automated Warm-up Scheduler for TikTok USA Audience Optimization
Schedules and executes warm-up sessions based on location percentage thresholds

Features:
- Intelligent scheduling based on USA percentage
- Automated warm-up session execution
- Integration with location optimization system
- Performance tracking and optimization
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from location_optimization_system import LocationOptimizationSystem
from database.location_optimization_models import (
    LocationMetrics, WarmupSession, LocationOptimizationAlert,
    LocationOptimizationUtils
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WarmupSchedule:
    """Warm-up schedule configuration for an account"""
    account: str
    schedule_type: str  # 'intensive', 'maintenance', 'light'
    frequency_hours: int
    duration_minutes: int
    keywords: List[str]
    is_active: bool = True
    last_executed: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None

class WarmupScheduler:
    """
    Automated scheduler for TikTok warm-up sessions
    """
    
    def __init__(self, database_url: str, tiktok_cookies: str = None):
        self.db_engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.db_engine)
        self.location_system = LocationOptimizationSystem(database_url, tiktok_cookies)
        
        # Schedule configurations for different USA percentage levels
        self.schedule_configs = {
            'critical': {  # USA % < 70%
                'type': 'intensive',
                'frequency_hours': 48,  # Every 2 days
                'duration_minutes': 30,
                'keywords': [
                    "USA pickup truck", "blue collar USA", "construction Texas",
                    "American trucker", "Bubba truck", "country road USA"
                ]
            },
            'warning': {  # USA % 70-95%
                'type': 'maintenance',
                'frequency_hours': 24,  # Daily
                'duration_minutes': 10,
                'keywords': [
                    "USA pickup truck", "blue collar USA", "construction Texas"
                ]
            },
            'optimal': {  # USA % > 95%
                'type': 'light',
                'frequency_hours': 72,  # Every 3 days
                'duration_minutes': 5,
                'keywords': [
                    "USA pickup truck", "blue collar USA"
                ]
            }
        }
        
        # Track active schedules
        self.active_schedules: Dict[str, WarmupSchedule] = {}

    async def initialize_account_schedules(self, accounts: List[str]):
        """
        Initialize warm-up schedules for all accounts based on current USA percentage
        
        Args:
            accounts: List of TikTok account usernames
        """
        logger.info(f"🔄 Initializing warm-up schedules for {len(accounts)} accounts")
        
        for account in accounts:
            try:
                # Get current location metrics
                location_metrics = await self.location_system.get_current_location_percentage(account)
                
                # Determine schedule configuration based on USA percentage
                if location_metrics.usa_percentage < 70:
                    config = self.schedule_configs['critical']
                    logger.warning(f"🚨 {account}: USA % {location_metrics.usa_percentage}% - Critical level")
                elif location_metrics.usa_percentage < 95:
                    config = self.schedule_configs['warning']
                    logger.warning(f"⚠️ {account}: USA % {location_metrics.usa_percentage}% - Warning level")
                else:
                    config = self.schedule_configs['optimal']
                    logger.info(f"✅ {account}: USA % {location_metrics.usa_percentage}% - Optimal level")
                
                # Create schedule
                schedule = WarmupSchedule(
                    account=account,
                    schedule_type=config['type'],
                    frequency_hours=config['frequency_hours'],
                    duration_minutes=config['duration_minutes'],
                    keywords=config['keywords'],
                    next_scheduled=datetime.utcnow() + timedelta(hours=config['frequency_hours'])
                )
                
                self.active_schedules[account] = schedule
                
                # Save to database
                await self._save_schedule_to_database(schedule)
                
                logger.info(f"📅 Scheduled {config['type']} warm-up for {account} every {config['frequency_hours']}h")
                
            except Exception as e:
                logger.error(f"❌ Error initializing schedule for {account}: {e}")

    async def check_and_execute_scheduled_warmups(self):
        """
        Check all active schedules and execute warm-ups that are due
        """
        current_time = datetime.utcnow()
        due_schedules = []
        
        # Find schedules that are due for execution
        for account, schedule in self.active_schedules.items():
            if (schedule.is_active and 
                schedule.next_scheduled and 
                current_time >= schedule.next_scheduled):
                due_schedules.append(schedule)
        
        if not due_schedules:
            logger.info("📅 No warm-up sessions due for execution")
            return
        
        logger.info(f"🔥 Executing {len(due_schedules)} warm-up sessions")
        
        # Execute warm-up sessions
        for schedule in due_schedules:
            try:
                await self._execute_warmup_session(schedule)
                
                # Update next scheduled time
                schedule.last_executed = current_time
                schedule.next_scheduled = current_time + timedelta(hours=schedule.frequency_hours)
                
                # Save updated schedule
                await self._save_schedule_to_database(schedule)
                
                logger.info(f"✅ Completed warm-up for {schedule.account}, next scheduled: {schedule.next_scheduled}")
                
            except Exception as e:
                logger.error(f"❌ Error executing warm-up for {schedule.account}: {e}")
                
                # Create alert for failed warm-up
                await self._create_failure_alert(schedule.account, str(e))

    async def _execute_warmup_session(self, schedule: WarmupSchedule):
        """
        Execute a warm-up session for a specific account
        
        Args:
            schedule: WarmupSchedule configuration
        """
        logger.info(f"🔥 Starting {schedule.schedule_type} warm-up for {schedule.account}")
        
        # Create warm-up session record
        session_id = f"auto_{schedule.account}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        session = self.Session()
        try:
            # Record session start
            warmup_record = WarmupSession(
                session_id=session_id,
                account=schedule.account,
                session_type=schedule.schedule_type,
                duration_minutes=schedule.duration_minutes,
                keywords_searched=schedule.keywords,
                started_at=datetime.utcnow()
            )
            session.add(warmup_record)
            session.commit()
            
            # Execute warm-up using location optimization system
            warmup_result = await self.location_system.execute_warmup_session(
                schedule.account,
                schedule.duration_minutes
            )
            
            # Update session record with results
            warmup_record.profiles_analyzed = len(warmup_result.profiles_engaged)
            warmup_record.profiles_engaged = len(warmup_result.profiles_engaged)
            warmup_record.comments_made = warmup_result.comments_made
            warmup_record.follows_made = warmup_result.follows_made
            warmup_record.usa_signals_strengthened = warmup_result.usa_signals_strengthened
            warmup_record.completed_at = datetime.utcnow()
            warmup_record.success_score = self._calculate_success_score(warmup_result)
            warmup_record.notes = f"Automated {schedule.schedule_type} warm-up completed"
            
            session.commit()
            
            # Check if USA percentage improved
            await self._check_improvement_and_adjust_schedule(schedule.account)
            
            logger.info(f"✅ Warm-up completed for {schedule.account}: {warmup_result.comments_made} comments, {warmup_result.follows_made} follows")
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error during warm-up execution for {schedule.account}: {e}")
            raise
        finally:
            session.close()

    def _calculate_success_score(self, warmup_result) -> float:
        """
        Calculate success score for a warm-up session (0-1)
        
        Args:
            warmup_result: WarmupSession result from location optimization system
            
        Returns:
            Success score between 0 and 1
        """
        # Weight different metrics
        comment_weight = 0.3
        follow_weight = 0.3
        engagement_weight = 0.2
        usa_signals_weight = 0.2
        
        # Normalize metrics (adjust thresholds based on experience)
        comment_score = min(warmup_result.comments_made / 10, 1.0)  # Target: 10 comments
        follow_score = min(warmup_result.follows_made / 5, 1.0)     # Target: 5 follows
        engagement_score = min(len(warmup_result.profiles_engaged) / 8, 1.0)  # Target: 8 profiles
        usa_signals_score = min(warmup_result.usa_signals_strengthened / 6, 1.0)  # Target: 6 signals
        
        # Calculate weighted score
        success_score = (
            comment_score * comment_weight +
            follow_score * follow_weight +
            engagement_score * engagement_weight +
            usa_signals_score * usa_signals_weight
        )
        
        return min(max(success_score, 0.0), 1.0)

    async def _check_improvement_and_adjust_schedule(self, account: str):
        """
        Check if USA percentage improved after warm-up and adjust schedule if needed
        
        Args:
            account: Account to check
        """
        try:
            # Get updated location metrics
            location_metrics = await self.location_system.get_current_location_percentage(account)
            
            # Determine if schedule needs adjustment
            current_schedule = self.active_schedules.get(account)
            if not current_schedule:
                return
            
            new_config = None
            if location_metrics.usa_percentage < 70:
                new_config = self.schedule_configs['critical']
            elif location_metrics.usa_percentage < 95:
                new_config = self.schedule_configs['warning']
            else:
                new_config = self.schedule_configs['optimal']
            
            # Check if schedule type changed
            if new_config['type'] != current_schedule.schedule_type:
                logger.info(f"📊 {account}: USA % improved to {location_metrics.usa_percentage}%, adjusting schedule to {new_config['type']}")
                
                # Update schedule configuration
                current_schedule.schedule_type = new_config['type']
                current_schedule.frequency_hours = new_config['frequency_hours']
                current_schedule.duration_minutes = new_config['duration_minutes']
                current_schedule.keywords = new_config['keywords']
                
                # Adjust next scheduled time based on new frequency
                if current_schedule.last_executed:
                    current_schedule.next_scheduled = (
                        current_schedule.last_executed + 
                        timedelta(hours=new_config['frequency_hours'])
                    )
                
                # Save updated schedule
                await self._save_schedule_to_database(current_schedule)
                
                # Create improvement alert
                await self._create_improvement_alert(account, location_metrics.usa_percentage, new_config['type'])
                
        except Exception as e:
            logger.error(f"❌ Error checking improvement for {account}: {e}")

    async def _save_schedule_to_database(self, schedule: WarmupSchedule):
        """Save schedule configuration to database"""
        session = self.Session()
        try:
            # This would save to a schedules table if it existed
            # For now, we'll use the existing tables to track schedule state
            pass
        finally:
            session.close()

    async def _create_failure_alert(self, account: str, error_message: str):
        """Create alert for warm-up failure"""
        session = self.Session()
        try:
            alert = LocationOptimizationAlert(
                account=account,
                alert_type='warmup_failed',
                alert_level='warning',
                message=f"Warm-up session failed: {error_message}",
                recommendation="Check system status and retry manually if needed"
            )
            session.add(alert)
            session.commit()
        finally:
            session.close()

    async def _create_improvement_alert(self, account: str, usa_percentage: float, new_schedule_type: str):
        """Create alert for USA percentage improvement"""
        session = self.Session()
        try:
            alert = LocationOptimizationAlert(
                account=account,
                alert_type='usa_percentage_improved',
                alert_level='info',
                message=f"USA percentage improved to {usa_percentage}%, schedule adjusted to {new_schedule_type}",
                current_value=usa_percentage,
                recommendation=f"Continue {new_schedule_type} warm-up schedule"
            )
            session.add(alert)
            session.commit()
        finally:
            session.close()

    async def emergency_warmup(self, account: str, reason: str = "Manual emergency warm-up"):
        """
        Execute emergency warm-up session immediately
        
        Args:
            account: Account for emergency warm-up
            reason: Reason for emergency warm-up
        """
        logger.warning(f"🚨 Executing emergency warm-up for {account}: {reason}")
        
        # Create emergency schedule
        emergency_schedule = WarmupSchedule(
            account=account,
            schedule_type='intensive',
            frequency_hours=0,  # Immediate execution
            duration_minutes=30,
            keywords=self.schedule_configs['critical']['keywords']
        )
        
        try:
            await self._execute_warmup_session(emergency_schedule)
            logger.info(f"✅ Emergency warm-up completed for {account}")
        except Exception as e:
            logger.error(f"❌ Emergency warm-up failed for {account}: {e}")
            await self._create_failure_alert(account, f"Emergency warm-up failed: {e}")

    async def pause_account_schedule(self, account: str, reason: str = "Manual pause"):
        """Pause warm-up schedule for an account"""
        if account in self.active_schedules:
            self.active_schedules[account].is_active = False
            logger.info(f"⏸️ Paused warm-up schedule for {account}: {reason}")

    async def resume_account_schedule(self, account: str):
        """Resume warm-up schedule for an account"""
        if account in self.active_schedules:
            self.active_schedules[account].is_active = True
            logger.info(f"▶️ Resumed warm-up schedule for {account}")

    async def get_schedule_status(self) -> Dict[str, Dict]:
        """
        Get status of all active schedules
        
        Returns:
            Dictionary with schedule status for each account
        """
        status = {}
        
        for account, schedule in self.active_schedules.items():
            status[account] = {
                'schedule_type': schedule.schedule_type,
                'is_active': schedule.is_active,
                'last_executed': schedule.last_executed.isoformat() if schedule.last_executed else None,
                'next_scheduled': schedule.next_scheduled.isoformat() if schedule.next_scheduled else None,
                'duration_minutes': schedule.duration_minutes,
                'frequency_hours': schedule.frequency_hours
            }
        
        return status

    async def run_scheduler_loop(self):
        """
        Main scheduler loop - runs continuously to check and execute warm-ups
        """
        logger.info("🔄 Starting warm-up scheduler loop")
        
        while True:
            try:
                await self.check_and_execute_scheduled_warmups()
                
                # Sleep for 5 minutes before next check
                await asyncio.sleep(300)
                
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

# Example usage and integration
async def main():
    """Example usage of the Warmup Scheduler"""
    
    # Initialize scheduler
    scheduler = WarmupScheduler(
        database_url="sqlite:///tiktok_analytics.db",
        tiktok_cookies="path/to/cookies.json"
    )
    
    # List of accounts to manage
    accounts = ["account1", "account2", "account3"]
    
    # Initialize schedules for all accounts
    await scheduler.initialize_account_schedules(accounts)
    
    # Get initial status
    status = await scheduler.get_schedule_status()
    print("📊 Initial Schedule Status:")
    for account, info in status.items():
        print(f"  {account}: {info['schedule_type']} - Next: {info['next_scheduled']}")
    
    # Run scheduler loop (in production, this would run as a service)
    print("\n🔄 Starting scheduler loop (Ctrl+C to stop)...")
    await scheduler.run_scheduler_loop()

if __name__ == "__main__":
    asyncio.run(main())
