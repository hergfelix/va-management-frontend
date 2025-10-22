"""
Production Database Schema for TikTok Analytics
Built with SuperClaude Backend Architect Agent

Features:
- ACID compliant database design
- Optimized indexing for performance
- Comprehensive data integrity
- Scalable architecture for 100K+ records
- Security-first implementation
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean,
    ForeignKey, Index, UniqueConstraint, CheckConstraint,
    create_engine, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class VA(Base):
    """
    Virtual Assistant entity with comprehensive tracking
    """
    __tablename__ = 'vas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    status = Column(String(20), default='active', nullable=False)  # active, inactive, suspended
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    accounts = relationship("Account", back_populates="va")
    scraping_jobs = relationship("ScrapingJob", back_populates="va")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='va_status_check'),
        Index('idx_va_name_status', 'name', 'status'),
    )
    
    def __repr__(self):
        return f"<VA(id={self.id}, name='{self.name}', status='{self.status}')>"

class Account(Base):
    """
    TikTok Account entity with comprehensive metadata
    """
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    platform = Column(String(50), default='TikTok', nullable=False)
    account_type = Column(String(20), default='personal', nullable=False)  # personal, business, creator
    status = Column(String(20), default='active', nullable=False)  # active, suspended, deleted
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=True)
    
    # Account metadata
    bio = Column(Text, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    private = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_scraped_at = Column(DateTime, nullable=True)
    
    # Relationships
    va = relationship("VA", back_populates="accounts")
    follower_snapshots = relationship("FollowerSnapshot", back_populates="account", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="account", cascade="all, delete-orphan")
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended', 'deleted')", name='account_status_check'),
        CheckConstraint("account_type IN ('personal', 'business', 'creator')", name='account_type_check'),
        Index('idx_account_username_status', 'username', 'status'),
        Index('idx_account_va_status', 'va_id', 'status'),
        Index('idx_account_last_scraped', 'last_scraped_at'),
    )
    
    def __repr__(self):
        return f"<Account(id={self.id}, username='{self.username}', va='{self.va.name if self.va else 'N/A'}')>"

class FollowerSnapshot(Base):
    """
    Follower count snapshots with comprehensive tracking
    """
    __tablename__ = 'follower_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    followers = Column(Integer, nullable=False)
    following = Column(Integer, nullable=True)
    posts_count = Column(Integer, nullable=True)
    likes_count = Column(Integer, nullable=True)
    
    # Engagement metrics
    avg_engagement_rate = Column(Float, nullable=True)
    total_views = Column(Integer, nullable=True)
    
    # Snapshot metadata
    snapshot_type = Column(String(20), default='scheduled', nullable=False)  # scheduled, manual, api
    data_source = Column(String(50), default='scraper', nullable=False)  # scraper, api, manual
    confidence_score = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="follower_snapshots")
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("followers >= 0", name='followers_positive_check'),
        CheckConstraint("following >= 0", name='following_positive_check'),
        CheckConstraint("posts_count >= 0", name='posts_count_positive_check'),
        CheckConstraint("likes_count >= 0", name='likes_count_positive_check'),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name='confidence_score_range_check'),
        CheckConstraint("snapshot_type IN ('scheduled', 'manual', 'api')", name='snapshot_type_check'),
        UniqueConstraint('account_id', 'timestamp', name='_account_timestamp_uc'),
        Index('idx_follower_account_timestamp', 'account_id', 'timestamp'),
        Index('idx_follower_timestamp', 'timestamp'),
        Index('idx_follower_snapshot_type', 'snapshot_type'),
    )
    
    def __repr__(self):
        return f"<FollowerSnapshot(id={self.id}, account_id={self.account_id}, followers={self.followers}, timestamp='{self.timestamp}')>"

class Post(Base):
    """
    TikTok Post entity with comprehensive metrics
    """
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_url = Column(String(500), unique=True, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    
    # Post metadata
    post_id = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)  # JSON array of hashtags
    sound_url = Column(String(500), nullable=True)
    sound_title = Column(String(200), nullable=True)
    
    # Content metadata
    slides_count = Column(Integer, default=1, nullable=False)
    duration = Column(Float, nullable=True)  # in seconds
    content_type = Column(String(20), default='video', nullable=False)  # video, image, slideshow
    
    # Performance metrics
    views = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    bookmarks = Column(Integer, default=0, nullable=False)
    
    # Calculated metrics
    engagement = Column(Integer, default=0, nullable=False)  # likes + comments + shares + bookmarks
    engagement_rate = Column(Float, default=0.0, nullable=False)  # engagement / views * 100
    
    # Timestamps
    created_date = Column(DateTime, nullable=True)
    created_time = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="posts")
    slides = relationship("PostSlide", back_populates="post", cascade="all, delete-orphan")
    metrics_snapshots = relationship("MetricsSnapshot", back_populates="post", cascade="all, delete-orphan")
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("views >= 0", name='views_positive_check'),
        CheckConstraint("likes >= 0", name='likes_positive_check'),
        CheckConstraint("comments >= 0", name='comments_positive_check'),
        CheckConstraint("shares >= 0", name='shares_positive_check'),
        CheckConstraint("bookmarks >= 0", name='bookmarks_positive_check'),
        CheckConstraint("engagement >= 0", name='engagement_positive_check'),
        CheckConstraint("engagement_rate >= 0.0", name='engagement_rate_positive_check'),
        CheckConstraint("slides_count > 0", name='slides_count_positive_check'),
        CheckConstraint("content_type IN ('video', 'image', 'slideshow')", name='content_type_check'),
        Index('idx_post_account_created', 'account_id', 'created_date'),
        Index('idx_post_views', 'views'),
        Index('idx_post_engagement_rate', 'engagement_rate'),
        Index('idx_post_scraped_at', 'scraped_at'),
    )
    
    def __repr__(self):
        return f"<Post(id={self.id}, post_url='{self.post_url[:50]}...', views={self.views})>"

class PostSlide(Base):
    """
    Individual slides within TikTok posts
    """
    __tablename__ = 'post_slides'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    slide_number = Column(Integer, nullable=False)
    slide_url = Column(String(500), nullable=False)
    
    # OCR and content analysis
    ocr_text = Column(Text, nullable=True)
    text_hash = Column(String(64), nullable=True, index=True)
    has_text = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="slides")
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("slide_number > 0", name='slide_number_positive_check'),
        UniqueConstraint('post_id', 'slide_number', name='_post_slide_number_uc'),
        Index('idx_slide_post_number', 'post_id', 'slide_number'),
        Index('idx_slide_text_hash', 'text_hash'),
        Index('idx_slide_has_text', 'has_text'),
    )
    
    def __repr__(self):
        return f"<PostSlide(id={self.id}, post_id={self.post_id}, slide_number={self.slide_number})>"

class MetricsSnapshot(Base):
    """
    Time-series metrics snapshots for posts
    """
    __tablename__ = 'metrics_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    
    # Metrics
    views = Column(Integer, nullable=False)
    likes = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    shares = Column(Integer, nullable=False)
    bookmarks = Column(Integer, nullable=False)
    engagement = Column(Integer, nullable=False)
    engagement_rate = Column(Float, nullable=False)
    
    # Snapshot metadata
    snapshot_type = Column(String(20), default='scheduled', nullable=False)  # scheduled, manual, api
    data_source = Column(String(50), default='scraper', nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="metrics_snapshots")
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("views >= 0", name='snapshot_views_positive_check'),
        CheckConstraint("likes >= 0", name='snapshot_likes_positive_check'),
        CheckConstraint("comments >= 0", name='snapshot_comments_positive_check'),
        CheckConstraint("shares >= 0", name='snapshot_shares_positive_check'),
        CheckConstraint("bookmarks >= 0", name='snapshot_bookmarks_positive_check'),
        CheckConstraint("engagement >= 0", name='snapshot_engagement_positive_check'),
        CheckConstraint("engagement_rate >= 0.0", name='snapshot_engagement_rate_positive_check'),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name='snapshot_confidence_score_range_check'),
        CheckConstraint("snapshot_type IN ('scheduled', 'manual', 'api')", name='snapshot_snapshot_type_check'),
        UniqueConstraint('post_id', 'timestamp', name='_post_timestamp_uc'),
        Index('idx_metrics_post_timestamp', 'post_id', 'timestamp'),
        Index('idx_metrics_timestamp', 'timestamp'),
        Index('idx_metrics_snapshot_type', 'snapshot_type'),
    )
    
    def __repr__(self):
        return f"<MetricsSnapshot(id={self.id}, post_id={self.post_id}, views={self.views}, timestamp='{self.timestamp}')>"

class ScrapingJob(Base):
    """
    Track scraping jobs and their status
    """
    __tablename__ = 'scraping_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # follower_tracking, post_metrics, full_scrape
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed, cancelled
    
    # Job metadata
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=True)
    target_accounts = Column(Text, nullable=True)  # JSON array of account IDs or usernames
    target_posts = Column(Text, nullable=True)  # JSON array of post URLs
    
    # Execution tracking
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    posts_processed = Column(Integer, default=0)
    posts_updated = Column(Integer, default=0)
    posts_failed = Column(Integer, default=0)
    accounts_processed = Column(Integer, default=0)
    accounts_updated = Column(Integer, default=0)
    accounts_failed = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Configuration
    config = Column(Text, nullable=True)  # JSON configuration
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    va = relationship("VA", back_populates="scraping_jobs")
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name='job_status_check'),
        CheckConstraint("job_type IN ('follower_tracking', 'post_metrics', 'full_scrape')", name='job_type_check'),
        CheckConstraint("posts_processed >= 0", name='posts_processed_positive_check'),
        CheckConstraint("posts_updated >= 0", name='posts_updated_positive_check'),
        CheckConstraint("posts_failed >= 0", name='posts_failed_positive_check'),
        CheckConstraint("accounts_processed >= 0", name='accounts_processed_positive_check'),
        CheckConstraint("accounts_updated >= 0", name='accounts_updated_positive_check'),
        CheckConstraint("accounts_failed >= 0", name='accounts_failed_positive_check'),
        CheckConstraint("retry_count >= 0", name='retry_count_positive_check'),
        CheckConstraint("max_retries >= 0", name='max_retries_positive_check'),
        Index('idx_job_name_status', 'job_name', 'status'),
        Index('idx_job_type_status', 'job_type', 'status'),
        Index('idx_job_va_status', 'va_id', 'status'),
        Index('idx_job_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ScrapingJob(id={self.id}, job_name='{self.job_name}', status='{self.status}')>"

# Database utility functions
class DatabaseManager:
    """
    Database management utilities with connection pooling and error handling
    """
    
    def __init__(self, database_url: str = "sqlite:///tiktok_analytics.db"):
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables with proper constraints"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def get_table_counts(self):
        """Get row counts for all tables"""
        counts = {}
        session = self.get_session()
        try:
            for table in Base.metadata.tables.values():
                result = session.execute(f"SELECT COUNT(*) FROM {table.name}")
                counts[table.name] = result.scalar()
            return counts
        finally:
            session.close()
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        session = self.get_session()
        try:
            stats = {
                'total_accounts': session.query(Account).count(),
                'active_accounts': session.query(Account).filter(Account.status == 'active').count(),
                'total_posts': session.query(Post).count(),
                'total_follower_snapshots': session.query(FollowerSnapshot).count(),
                'total_metrics_snapshots': session.query(MetricsSnapshot).count(),
                'total_scraping_jobs': session.query(ScrapingJob).count(),
                'active_scraping_jobs': session.query(ScrapingJob).filter(ScrapingJob.status == 'running').count(),
            }
            return stats
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.create_tables()
    
    # Get database statistics
    stats = db_manager.get_database_stats()
    print("📊 Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:,}")
    
    print("\n✅ Production database schema created successfully!")
    print("🎯 Ready for TikTok Analytics with comprehensive tracking!")
