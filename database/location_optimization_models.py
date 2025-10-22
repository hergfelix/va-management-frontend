#!/usr/bin/env python3
"""
Database Models for TikTok USA Location Optimization System
Extends the main database schema with location tracking capabilities

New Tables:
- location_metrics: Track USA percentage over time
- warmup_sessions: Log warm-up engagement sessions
- profile_analyses: Store USA profile analysis results
- comment_management: Track comment engagement strategies
- posting_optimization: Optimal posting time tracking
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from database.models import Base

class LocationMetrics(Base):
    """
    Track location percentage metrics over time for each account
    """
    __tablename__ = 'location_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(100), nullable=False, index=True)
    post_url = Column(String(500), nullable=True, index=True)  # Optional: specific post metrics
    
    # Location percentages
    usa_percentage = Column(Float, nullable=False)
    non_usa_percentage = Column(Float, nullable=False)
    total_audience = Column(Integer, nullable=False, default=0)
    
    # Engagement breakdown
    usa_engagements = Column(Integer, nullable=False, default=0)
    non_usa_engagements = Column(Integer, nullable=False, default=0)
    
    # Confidence and metadata
    confidence_score = Column(Float, nullable=False, default=0.0)  # 0-1 confidence in data
    data_source = Column(String(50), nullable=False)  # 'analytics_api', 'scraped', 'estimated'
    
    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('usa_percentage >= 0 AND usa_percentage <= 100', name='check_usa_percentage_range'),
        CheckConstraint('non_usa_percentage >= 0 AND non_usa_percentage <= 100', name='check_non_usa_percentage_range'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_range'),
        Index('idx_location_metrics_account_date', 'account', 'recorded_at'),
        Index('idx_location_metrics_usa_percentage', 'usa_percentage'),
    )
    
    def __repr__(self):
        return f"<LocationMetrics(account='{self.account}', usa_percentage={self.usa_percentage}%, confidence={self.confidence_score})>"

class WarmupSession(Base):
    """
    Track warm-up engagement sessions for location optimization
    """
    __tablename__ = 'warmup_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    account = Column(String(100), nullable=False, index=True)
    
    # Session details
    session_type = Column(String(20), nullable=False)  # 'intensive', 'maintenance', 'emergency'
    duration_minutes = Column(Integer, nullable=False)
    keywords_searched = Column(JSON, nullable=True)  # List of search keywords used
    
    # Engagement metrics
    profiles_analyzed = Column(Integer, nullable=False, default=0)
    profiles_engaged = Column(Integer, nullable=False, default=0)
    comments_made = Column(Integer, nullable=False, default=0)
    follows_made = Column(Integer, nullable=False, default=0)
    likes_given = Column(Integer, nullable=False, default=0)
    
    # USA signal strengthening
    usa_signals_strengthened = Column(Integer, nullable=False, default=0)
    usa_creators_followed = Column(Integer, nullable=False, default=0)
    
    # Session results
    success_score = Column(Float, nullable=True)  # 0-1 rating of session success
    notes = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_positive_duration'),
        CheckConstraint('success_score >= 0 AND success_score <= 1', name='check_success_score_range'),
        Index('idx_warmup_sessions_account_date', 'account', 'started_at'),
    )
    
    def __repr__(self):
        return f"<WarmupSession(session_id='{self.session_id}', account='{self.account}', type='{self.session_type}')>"

class ProfileAnalysis(Base):
    """
    Store USA profile analysis results for reuse and learning
    """
    __tablename__ = 'profile_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, index=True)
    
    # Analysis results
    is_usa = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1 confidence score
    usa_signals = Column(JSON, nullable=True)  # List of detected USA signals
    risk_factors = Column(JSON, nullable=True)  # List of non-USA risk factors
    
    # Profile metadata
    followers_count = Column(Integer, nullable=True)
    following_count = Column(Integer, nullable=True)
    bio_text = Column(Text, nullable=True)
    display_name = Column(String(200), nullable=True)
    
    # Analysis metadata
    analysis_method = Column(String(50), nullable=False)  # 'automated', 'manual', 'hybrid'
    data_freshness_hours = Column(Integer, nullable=True)  # How fresh the profile data was
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    profile_last_updated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence_range'),
        UniqueConstraint('username', 'analyzed_at', name='unique_username_analysis'),
        Index('idx_profile_analyses_usa_confidence', 'is_usa', 'confidence'),
    )
    
    def __repr__(self):
        return f"<ProfileAnalysis(username='{self.username}', is_usa={self.is_usa}, confidence={self.confidence})>"

class CommentManagement(Base):
    """
    Track comment management strategies and results
    """
    __tablename__ = 'comment_management'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_url = Column(String(500), nullable=False, index=True)
    account = Column(String(100), nullable=False, index=True)
    
    # Comment strategy
    strategy_type = Column(String(20), nullable=False)  # 'reply_all', 'selective_usa', 'hide_non_usa'
    location_threshold = Column(Float, nullable=False)  # USA % threshold for strategy decision
    
    # Management results
    total_comments = Column(Integer, nullable=False, default=0)
    usa_comments_replied = Column(Integer, nullable=False, default=0)
    non_usa_comments_hidden = Column(Integer, nullable=False, default=0)
    conversations_started = Column(Integer, nullable=False, default=0)
    
    # Engagement questions used
    engagement_questions = Column(JSON, nullable=True)  # List of questions asked
    
    # Results and feedback
    engagement_increase = Column(Float, nullable=True)  # % increase in engagement
    usa_percentage_improvement = Column(Float, nullable=True)  # Improvement in USA %
    
    # Timestamps
    managed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('location_threshold >= 0 AND location_threshold <= 100', name='check_threshold_range'),
        Index('idx_comment_management_account_date', 'account', 'managed_at'),
    )
    
    def __repr__(self):
        return f"<CommentManagement(post_url='{self.post_url}', strategy='{self.strategy_type}', replies={self.usa_comments_replied})>"

class PostingOptimization(Base):
    """
    Track optimal posting times and results
    """
    __tablename__ = 'posting_optimization'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(100), nullable=False, index=True)
    
    # Posting details
    post_url = Column(String(500), nullable=True, index=True)
    posted_at = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), nullable=False, default='America/New_York')
    
    # Optimal time analysis
    was_optimal_time = Column(Boolean, nullable=False)
    optimal_window_start = Column(String(10), nullable=True)  # HH:MM format
    optimal_window_end = Column(String(10), nullable=True)    # HH:MM format
    hours_from_optimal = Column(Float, nullable=True)  # How far from optimal window
    
    # Performance results
    views_24h = Column(Integer, nullable=True)
    engagement_24h = Column(Integer, nullable=True)
    usa_percentage_24h = Column(Float, nullable=True)
    
    # Recommendations
    recommended_posting_times = Column(JSON, nullable=True)  # List of optimal windows
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('usa_percentage_24h >= 0 AND usa_percentage_24h <= 100', name='check_usa_percentage_range'),
        Index('idx_posting_optimization_account_date', 'account', 'posted_at'),
        Index('idx_posting_optimization_optimal', 'was_optimal_time', 'posted_at'),
    )
    
    def __repr__(self):
        return f"<PostingOptimization(account='{self.account}', optimal={self.was_optimal_time}, posted_at='{self.posted_at}')>"

class SoundVerification(Base):
    """
    Track sound verification for USA audience targeting
    """
    __tablename__ = 'sound_verification'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sound_url = Column(String(500), nullable=False, index=True)
    sound_title = Column(String(200), nullable=True)
    
    # USA audience analysis
    usa_usage_percentage = Column(Float, nullable=False)
    total_uses = Column(Integer, nullable=False, default=0)
    usa_creators_using = Column(Integer, nullable=False, default=0)
    
    # Top USA creators using this sound
    top_usa_creators = Column(JSON, nullable=True)  # List of usernames
    
    # Verification results
    is_usa_approved = Column(Boolean, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0-1 confidence in verification
    recommendation = Column(String(100), nullable=True)  # 'approved', 'avoid', 'verify_manually'
    
    # Analysis metadata
    analysis_method = Column(String(50), nullable=False)  # 'automated', 'manual', 'hybrid'
    sample_size = Column(Integer, nullable=True)  # Number of videos analyzed
    
    # Timestamps
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('usa_usage_percentage >= 0 AND usa_usage_percentage <= 100', name='check_usage_percentage_range'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_range'),
        Index('idx_sound_verification_approved', 'is_usa_approved', 'confidence_score'),
    )
    
    def __repr__(self):
        return f"<SoundVerification(sound_title='{self.sound_title}', usa_approved={self.is_usa_approved}, confidence={self.confidence_score})>"

class LocationOptimizationAlert(Base):
    """
    Track alerts and notifications for location optimization
    """
    __tablename__ = 'location_optimization_alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String(100), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # 'usa_percentage_low', 'warmup_needed', 'posting_time_suboptimal'
    alert_level = Column(String(20), nullable=False)  # 'info', 'warning', 'critical'
    message = Column(Text, nullable=False)
    
    # Alert data
    current_value = Column(Float, nullable=True)  # Current metric value
    threshold_value = Column(Float, nullable=True)  # Threshold that triggered alert
    recommendation = Column(Text, nullable=True)
    
    # Status
    is_resolved = Column(Boolean, nullable=False, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(50), nullable=True)  # 'automated', 'manual'
    
    # Timestamps
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint('alert_level IN ("info", "warning", "critical")', name='check_alert_level'),
        Index('idx_alerts_account_status', 'account', 'is_resolved', 'triggered_at'),
        Index('idx_alerts_level_date', 'alert_level', 'triggered_at'),
    )
    
    def __repr__(self):
        return f"<LocationOptimizationAlert(account='{self.account}', type='{self.alert_type}', level='{self.alert_level}')>"

# Utility functions for location optimization
class LocationOptimizationUtils:
    """Utility functions for location optimization calculations"""
    
    @staticmethod
    def calculate_usa_percentage_trend(location_metrics_list):
        """Calculate trend in USA percentage over time"""
        if len(location_metrics_list) < 2:
            return 'insufficient_data'
        
        recent_avg = sum(m.usa_percentage for m in location_metrics_list[-3:]) / min(3, len(location_metrics_list))
        older_avg = sum(m.usa_percentage for m in location_metrics_list[:-3]) / max(1, len(location_metrics_list) - 3)
        
        if recent_avg > older_avg + 5:
            return 'improving'
        elif rate_avg < older_avg - 5:
            return 'declining'
        else:
            return 'stable'
    
    @staticmethod
    def get_warmup_intensity_recommendation(usa_percentage):
        """Get warm-up intensity recommendation based on USA percentage"""
        if usa_percentage < 70:
            return 'intensive'  # 30-minute full warm-up
        elif usa_percentage < 95:
            return 'maintenance'  # 10-minute maintenance warm-up
        else:
            return 'light'  # 5-minute light warm-up
    
    @staticmethod
    def calculate_optimal_posting_score(posted_time, timezone='America/New_York'):
        """Calculate how optimal a posting time is (0-100 score)"""
        import pytz
        from datetime import time
        
        target_tz = pytz.timezone(timezone)
        pht = pytz.timezone('Asia/Manila')
        
        # Convert posted time to target timezone
        posted_dt = target_tz.localize(posted_time)
        pht_time = posted_dt.astimezone(pht).time()
        
        # Optimal windows in PHT
        optimal_windows = [
            (time(6, 0), time(12, 0)),   # Morning to Midday
            (time(22, 0), time(23, 59))  # Late Night
        ]
        
        # Check if time is in optimal window
        for start, end in optimal_windows:
            if start <= pht_time <= end:
                return 100  # Perfect score
        
        # Calculate distance from optimal windows
        min_distance = float('inf')
        for start, end in optimal_windows:
            if pht_time < start:
                distance = (start.hour * 60 + start.minute) - (pht_time.hour * 60 + pht_time.minute)
            elif pht_time > end:
                distance = (pht_time.hour * 60 + pht_time.minute) - (end.hour * 60 + end.minute)
            else:
                distance = 0
            
            min_distance = min(min_distance, distance)
        
        # Convert distance to score (farther = lower score)
        score = max(0, 100 - (min_distance * 2))  # 2 points per minute away
        return score

# Export all models
__all__ = [
    'LocationMetrics', 'WarmupSession', 'ProfileAnalysis', 'CommentManagement',
    'PostingOptimization', 'SoundVerification', 'LocationOptimizationAlert',
    'LocationOptimizationUtils'
]
