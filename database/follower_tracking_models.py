"""
Follower Tracking Database Models
Professional TikTok account follower tracking system
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean,
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class VA(Base):
    """
    Virtual Assistant (Employee) tracking
    """
    __tablename__ = 'vas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default='active')  # active, inactive, training
    joined_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    accounts = relationship("Account", back_populates="va")

class Account(Base):
    """
    TikTok Account tracking
    """
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    
    # VA Assignment
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=True, index=True)
    
    # Account Status
    status = Column(String(20), nullable=False, default='active')  # active, inactive, suspended, deleted
    created_date = Column(DateTime, nullable=True)  # When account was created
    last_checked = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    va = relationship("VA", back_populates="accounts")
    follower_snapshots = relationship("FollowerSnapshot", back_populates="account", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_account_va_status', 'va_id', 'status'),
        Index('idx_account_username_status', 'username', 'status'),
    )

class FollowerSnapshot(Base):
    """
    Daily follower count snapshots for growth tracking
    """
    __tablename__ = 'follower_snapshots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Snapshot data
    snapshot_date = Column(DateTime, nullable=False, index=True)
    followers = Column(Integer, nullable=False, default=0)
    following = Column(Integer, nullable=True, default=0)
    likes = Column(Integer, nullable=True, default=0)
    videos = Column(Integer, nullable=True, default=0)
    
    # Growth calculations
    followers_change = Column(Integer, nullable=True, default=0)  # Change from previous day
    followers_growth_rate = Column(Float, nullable=True, default=0.0)  # Percentage growth
    
    # Scraping metadata
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scraping_method = Column(String(50), nullable=True)  # playwright, apify, manual
    scraping_status = Column(String(20), nullable=False, default='success')  # success, failed, partial
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="follower_snapshots")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('account_id', 'snapshot_date', name='unique_account_date'),
        Index('idx_snapshot_date_account', 'snapshot_date', 'account_id'),
        Index('idx_snapshot_followers', 'followers'),
        Index('idx_snapshot_growth', 'followers_growth_rate'),
    )

class ScrapingJob(Base):
    """
    Track scraping jobs and their status
    """
    __tablename__ = 'scraping_jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # follower_scraping, account_discovery, etc.
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed, cancelled
    
    # Job details
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    accounts_processed = Column(Integer, default=0)
    accounts_successful = Column(Integer, default=0)
    accounts_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Configuration
    config = Column(Text, nullable=True)  # JSON configuration
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_job_status_type', 'status', 'job_type'),
        Index('idx_job_created', 'created_at'),
    )

class GrowthMilestone(Base):
    """
    Track follower growth milestones
    """
    __tablename__ = 'growth_milestones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    
    # Milestone details
    milestone_type = Column(String(50), nullable=False)  # follower_count, growth_rate, etc.
    milestone_value = Column(Integer, nullable=False)  # 1000, 10000, 100000, etc.
    achieved_at = Column(DateTime, nullable=False, index=True)
    
    # Context
    previous_value = Column(Integer, nullable=True)
    days_to_achieve = Column(Integer, nullable=True)  # Days since last milestone
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account")
    
    # Indexes
    __table_args__ = (
        Index('idx_milestone_account_type', 'account_id', 'milestone_type'),
        Index('idx_milestone_achieved', 'achieved_at'),
    )

class VAPerformance(Base):
    """
    VA performance metrics and rankings
    """
    __tablename__ = 'va_performance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=False, index=True)
    
    # Performance period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly
    
    # Metrics
    total_accounts = Column(Integer, default=0)
    total_followers = Column(Integer, default=0)
    total_followers_gained = Column(Integer, default=0)
    average_growth_rate = Column(Float, default=0.0)
    best_performing_account = Column(String(100), nullable=True)
    worst_performing_account = Column(String(100), nullable=True)
    
    # Rankings
    follower_rank = Column(Integer, nullable=True)  # Rank among all VAs
    growth_rank = Column(Integer, nullable=True)    # Rank by growth rate
    account_rank = Column(Integer, nullable=True)   # Rank by number of accounts
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    va = relationship("VA")
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('va_id', 'period_start', 'period_end', 'period_type', name='unique_va_period'),
        Index('idx_performance_period', 'period_start', 'period_end'),
        Index('idx_performance_ranks', 'follower_rank', 'growth_rank'),
    )

# Create views for common queries
class AccountSummary(Base):
    """
    View for account summary with latest follower count
    """
    __tablename__ = 'account_summary'
    
    # This would be a materialized view in production
    account_id = Column(Integer, primary_key=True)
    username = Column(String(100))
    va_name = Column(String(50))
    current_followers = Column(Integer)
    followers_change_7d = Column(Integer)
    followers_growth_rate_7d = Column(Float)
    last_updated = Column(DateTime)
    status = Column(String(20))

class VASummary(Base):
    """
    View for VA summary with performance metrics
    """
    __tablename__ = 'va_summary'
    
    # This would be a materialized view in production
    va_id = Column(Integer, primary_key=True)
    va_name = Column(String(50))
    total_accounts = Column(Integer)
    total_followers = Column(Integer)
    total_followers_gained_7d = Column(Integer)
    average_growth_rate_7d = Column(Float)
    best_account = Column(String(100))
    worst_account = Column(String(100))
    last_updated = Column(DateTime)
