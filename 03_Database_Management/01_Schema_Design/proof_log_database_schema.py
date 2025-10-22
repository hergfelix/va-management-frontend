"""
Proof Log Database Schema - Comprehensive Data Collection System
Built with SuperClaude Backend Architect Agent

This schema is designed to collect EVERYTHING from your current Telegram → Google Sheets workflow
and expand it into a comprehensive analytics system.

Key Features:
- Preserves existing workflow (Telegram → Google Sheets)
- Adds comprehensive data collection and analysis
- Enables slideshow performance tracking
- Supports cross-creator analysis
- Provides foundation for all future analytics
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean,
    ForeignKey, Index, UniqueConstraint, CheckConstraint,
    create_engine, func, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class TelegramGroup(Base):
    """
    Telegram groups where workers post their content
    """
    __tablename__ = 'telegram_groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(50), unique=True, nullable=False, index=True)
    group_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    proof_logs = relationship("ProofLog", back_populates="telegram_group")
    
    def __repr__(self):
        return f"<TelegramGroup(id={self.id}, chat_id='{self.chat_id}', name='{self.group_name}')>"

class Creator(Base):
    """
    Content creators (Tyra, Ariri, Naomi, etc.)
    """
    __tablename__ = 'creators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    status = Column(String(20), default='active', nullable=False)  # active, inactive, suspended
    
    # Creator attributes for cross-creator analysis
    attributes = Column(JSON, nullable=True)  # e.g., {"body_type": "curvy", "style": "fashion"}
    target_audience = Column(String(100), nullable=True)
    content_style = Column(String(100), nullable=True)
    
    # Performance tracking
    total_posts = Column(Integer, default=0, nullable=False)
    total_views = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_post_at = Column(DateTime, nullable=True)
    
    # Relationships
    proof_logs = relationship("ProofLog", back_populates="creator")
    content_sets = relationship("ContentSet", back_populates="creator")
    posts = relationship("Post", back_populates="creator")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='creator_status_check'),
        Index('idx_creator_name_status', 'name', 'status'),
        Index('idx_creator_performance', 'total_views', 'avg_engagement_rate'),
    )
    
    def __repr__(self):
        return f"<Creator(id={self.id}, name='{self.name}', posts={self.total_posts})>"

class VA(Base):
    """
    Virtual Assistants managing accounts
    """
    __tablename__ = 'vas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    status = Column(String(20), default='active', nullable=False)  # active, inactive, suspended
    
    # Performance tracking
    accounts_managed = Column(Integer, default=0, nullable=False)
    total_posts_managed = Column(Integer, default=0, nullable=False)
    avg_performance_score = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    proof_logs = relationship("ProofLog", back_populates="va")
    accounts = relationship("Account", back_populates="va")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='va_status_check'),
        Index('idx_va_name_status', 'name', 'status'),
        Index('idx_va_performance', 'avg_performance_score'),
    )
    
    def __repr__(self):
        return f"<VA(id={self.id}, name='{self.name}', accounts={self.accounts_managed})>"

class ContentSet(Base):
    """
    Content sets (Set ID from proof log)
    """
    __tablename__ = 'content_sets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    set_id = Column(Integer, nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey('creators.id'), nullable=False)
    
    # Content set metadata
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), default='slideshow', nullable=False)  # slideshow, video, image
    theme = Column(String(100), nullable=True)  # e.g., "fashion", "lifestyle", "food"
    
    # Performance tracking
    total_posts = Column(Integer, default=0, nullable=False)
    total_views = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    viral_posts = Column(Integer, default=0, nullable=False)  # Posts with >10K views
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("Creator", back_populates="content_sets")
    proof_logs = relationship("ProofLog", back_populates="content_set")
    posts = relationship("Post", back_populates="content_set")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("content_type IN ('slideshow', 'video', 'image')", name='content_type_check'),
        UniqueConstraint('set_id', 'creator_id', name='_set_creator_uc'),
        Index('idx_content_set_creator', 'creator_id', 'set_id'),
        Index('idx_content_set_performance', 'total_views', 'avg_engagement_rate'),
    )
    
    def __repr__(self):
        return f"<ContentSet(id={self.id}, set_id={self.set_id}, creator='{self.creator.name if self.creator else 'N/A'}')>"

class Account(Base):
    """
    TikTok accounts (to be populated from URL analysis)
    """
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=True)
    
    # Account metadata
    platform = Column(String(50), default='TikTok', nullable=False)
    account_type = Column(String(20), default='personal', nullable=False)  # personal, business, creator
    status = Column(String(20), default='active', nullable=False)  # active, suspended, deleted
    
    # Performance tracking
    followers = Column(Integer, default=0, nullable=False)
    following = Column(Integer, default=0, nullable=False)
    total_posts = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_scraped_at = Column(DateTime, nullable=True)
    
    # Relationships
    va = relationship("VA", back_populates="accounts")
    proof_logs = relationship("ProofLog", back_populates="account")
    posts = relationship("Post", back_populates="account")
    follower_snapshots = relationship("FollowerSnapshot", back_populates="account")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended', 'deleted')", name='account_status_check'),
        CheckConstraint("account_type IN ('personal', 'business', 'creator')", name='account_type_check'),
        Index('idx_account_username_status', 'username', 'status'),
        Index('idx_account_va_status', 'va_id', 'status'),
        Index('idx_account_performance', 'followers', 'avg_engagement_rate'),
    )
    
    def __repr__(self):
        return f"<Account(id={self.id}, username='{self.username}', va='{self.va.name if self.va else 'N/A'}')>"

class ProofLog(Base):
    """
    Main proof log table - captures everything from Telegram → Google Sheets
    """
    __tablename__ = 'proof_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram metadata
    timestamp = Column(DateTime, nullable=False, index=True)
    chat_id = Column(String(50), ForeignKey('telegram_groups.chat_id'), nullable=False)
    message_id = Column(String(50), nullable=False, index=True)
    
    # Content metadata
    creator_id = Column(Integer, ForeignKey('creators.id'), nullable=False)
    content_set_id = Column(Integer, ForeignKey('content_sets.id'), nullable=True)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    
    # Post metadata
    post_type = Column(String(20), nullable=False)  # NEW, REPOST
    platform = Column(String(50), default='tiktok', nullable=False)
    post_url = Column(String(500), nullable=False, index=True)
    dedupe_key = Column(String(500), nullable=True, index=True)
    
    # Performance data (to be populated by scraping)
    views = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    bookmarks = Column(Integer, default=0, nullable=False)
    engagement = Column(Integer, default=0, nullable=False)
    engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Scraping metadata
    scraped_at = Column(DateTime, nullable=True)
    scraping_status = Column(String(20), default='pending', nullable=False)  # pending, success, failed, retry
    scraping_attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    telegram_group = relationship("TelegramGroup", back_populates="proof_logs")
    creator = relationship("Creator", back_populates="proof_logs")
    content_set = relationship("ContentSet", back_populates="proof_logs")
    va = relationship("VA", back_populates="proof_logs")
    account = relationship("Account", back_populates="proof_logs")
    post = relationship("Post", back_populates="proof_log", uselist=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("post_type IN ('NEW', 'REPOST')", name='post_type_check'),
        CheckConstraint("scraping_status IN ('pending', 'success', 'failed', 'retry')", name='scraping_status_check'),
        CheckConstraint("views >= 0", name='views_positive_check'),
        CheckConstraint("likes >= 0", name='likes_positive_check'),
        CheckConstraint("comments >= 0", name='comments_positive_check'),
        CheckConstraint("shares >= 0", name='shares_positive_check'),
        CheckConstraint("bookmarks >= 0", name='bookmarks_positive_check'),
        CheckConstraint("engagement >= 0", name='engagement_positive_check'),
        CheckConstraint("engagement_rate >= 0.0", name='engagement_rate_positive_check'),
        UniqueConstraint('message_id', 'chat_id', name='_message_chat_uc'),
        Index('idx_proof_log_timestamp', 'timestamp'),
        Index('idx_proof_log_creator_va', 'creator_id', 'va_id'),
        Index('idx_proof_log_scraping_status', 'scraping_status'),
        Index('idx_proof_log_performance', 'views', 'engagement_rate'),
    )
    
    def __repr__(self):
        return f"<ProofLog(id={self.id}, creator='{self.creator.name if self.creator else 'N/A'}', type='{self.post_type}', url='{self.post_url[:50]}...')>"

class Post(Base):
    """
    Detailed post information (populated by scraping)
    """
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    proof_log_id = Column(Integer, ForeignKey('proof_logs.id'), nullable=False, unique=True)
    creator_id = Column(Integer, ForeignKey('creators.id'), nullable=False)
    content_set_id = Column(Integer, ForeignKey('content_sets.id'), nullable=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    
    # Post metadata
    post_url = Column(String(500), unique=True, nullable=False, index=True)
    post_id = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)  # Array of hashtags
    sound_url = Column(String(500), nullable=True)
    sound_title = Column(String(200), nullable=True)
    
    # Content metadata
    slides_count = Column(Integer, default=1, nullable=False)
    duration = Column(Float, nullable=True)  # in seconds
    content_type = Column(String(20), default='slideshow', nullable=False)  # slideshow, video, image
    
    # Performance metrics
    views = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    bookmarks = Column(Integer, default=0, nullable=False)
    engagement = Column(Integer, default=0, nullable=False)
    engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_date = Column(DateTime, nullable=True)
    created_time = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    proof_log = relationship("ProofLog", back_populates="post")
    creator = relationship("Creator", back_populates="posts")
    content_set = relationship("ContentSet", back_populates="posts")
    account = relationship("Account", back_populates="posts")
    slides = relationship("PostSlide", back_populates="post", cascade="all, delete-orphan")
    metrics_snapshots = relationship("MetricsSnapshot", back_populates="post", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("content_type IN ('slideshow', 'video', 'image')", name='post_content_type_check'),
        CheckConstraint("slides_count > 0", name='slides_count_positive_check'),
        CheckConstraint("views >= 0", name='post_views_positive_check'),
        CheckConstraint("likes >= 0", name='post_likes_positive_check'),
        CheckConstraint("comments >= 0", name='post_comments_positive_check'),
        CheckConstraint("shares >= 0", name='post_shares_positive_check'),
        CheckConstraint("bookmarks >= 0", name='post_bookmarks_positive_check'),
        CheckConstraint("engagement >= 0", name='post_engagement_positive_check'),
        CheckConstraint("engagement_rate >= 0.0", name='post_engagement_rate_positive_check'),
        Index('idx_post_creator_content_set', 'creator_id', 'content_set_id'),
        Index('idx_post_account_created', 'account_id', 'created_date'),
        Index('idx_post_performance', 'views', 'engagement_rate'),
        Index('idx_post_scraped_at', 'scraped_at'),
    )
    
    def __repr__(self):
        return f"<Post(id={self.id}, creator='{self.creator.name if self.creator else 'N/A'}', views={self.views})>"

class PostSlide(Base):
    """
    Individual slides within slideshow posts
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
    
    # Content analysis
    content_category = Column(String(100), nullable=True)  # e.g., "fashion", "lifestyle", "food"
    content_attributes = Column(JSON, nullable=True)  # e.g., {"colors": ["red", "blue"], "objects": ["car", "building"]}
    
    # Performance tracking (if individual slide metrics are available)
    slide_views = Column(Integer, nullable=True)
    slide_engagement = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="slides")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("slide_number > 0", name='slide_number_positive_check'),
        UniqueConstraint('post_id', 'slide_number', name='_post_slide_number_uc'),
        Index('idx_slide_post_number', 'post_id', 'slide_number'),
        Index('idx_slide_text_hash', 'text_hash'),
        Index('idx_slide_content_category', 'content_category'),
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
    
    # Constraints
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

class FollowerSnapshot(Base):
    """
    Account follower snapshots for growth tracking
    """
    __tablename__ = 'follower_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    
    # Metrics
    followers = Column(Integer, nullable=False)
    following = Column(Integer, nullable=True)
    posts_count = Column(Integer, nullable=True)
    likes_count = Column(Integer, nullable=True)
    
    # Snapshot metadata
    snapshot_type = Column(String(20), default='scheduled', nullable=False)  # scheduled, manual, api
    data_source = Column(String(50), default='scraper', nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="follower_snapshots")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("followers >= 0", name='follower_snapshot_followers_positive_check'),
        CheckConstraint("following >= 0", name='follower_snapshot_following_positive_check'),
        CheckConstraint("posts_count >= 0", name='follower_snapshot_posts_count_positive_check'),
        CheckConstraint("likes_count >= 0", name='follower_snapshot_likes_count_positive_check'),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name='follower_snapshot_confidence_score_range_check'),
        CheckConstraint("snapshot_type IN ('scheduled', 'manual', 'api')", name='follower_snapshot_snapshot_type_check'),
        UniqueConstraint('account_id', 'timestamp', name='_account_timestamp_uc'),
        Index('idx_follower_account_timestamp', 'account_id', 'timestamp'),
        Index('idx_follower_timestamp', 'timestamp'),
        Index('idx_follower_snapshot_type', 'snapshot_type'),
    )
    
    def __repr__(self):
        return f"<FollowerSnapshot(id={self.id}, account_id={self.account_id}, followers={self.followers}, timestamp='{self.timestamp}')>"

# Database utility functions
class ProofLogDatabaseManager:
    """
    Database management utilities for proof log system
    """
    
    def __init__(self, database_url: str = "sqlite:///proof_log_analytics.db"):
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables with proper constraints"""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def import_proof_log_csv(self, csv_path: str):
        """Import proof log data from CSV"""
        import pandas as pd
        from datetime import datetime
        
        session = self.get_session()
        try:
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                # Create or get telegram group
                telegram_group = session.query(TelegramGroup).filter(
                    TelegramGroup.chat_id == str(row['Chat ID'])
                ).first()
                
                if not telegram_group:
                    telegram_group = TelegramGroup(
                        chat_id=str(row['Chat ID']),
                        group_name=f"Chat {row['Chat ID']}"
                    )
                    session.add(telegram_group)
                    session.flush()
                
                # Create or get creator
                creator = session.query(Creator).filter(
                    Creator.name == row['Creator']
                ).first()
                
                if not creator:
                    creator = Creator(name=row['Creator'])
                    session.add(creator)
                    session.flush()
                
                # Create or get VA
                va = session.query(VA).filter(
                    VA.name == row['VA']
                ).first()
                
                if not va:
                    va = VA(name=row['VA'])
                    session.add(va)
                    session.flush()
                
                # Create or get content set
                content_set = None
                if pd.notna(row['Set ID']):
                    content_set = session.query(ContentSet).filter(
                        ContentSet.set_id == int(row['Set ID']),
                        ContentSet.creator_id == creator.id
                    ).first()
                    
                    if not content_set:
                        content_set = ContentSet(
                            set_id=int(row['Set ID']),
                            creator_id=creator.id
                        )
                        session.add(content_set)
                        session.flush()
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['Timestamp'].replace('Z', '+00:00'))
                
                # Create proof log entry
                proof_log = ProofLog(
                    timestamp=timestamp,
                    chat_id=telegram_group.chat_id,
                    message_id=str(row['Message ID']),
                    creator_id=creator.id,
                    content_set_id=content_set.id if content_set else None,
                    va_id=va.id,
                    post_type=row['Type'],
                    platform=row['Platform'],
                    post_url=row['Post URL'],
                    dedupe_key=row.get('Dedupe Key')
                )
                
                session.add(proof_log)
            
            session.commit()
            print(f"✅ Successfully imported {len(df)} proof log entries")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error importing proof log: {e}")
            raise
        finally:
            session.close()
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        session = self.get_session()
        try:
            stats = {
                'total_proof_logs': session.query(ProofLog).count(),
                'total_creators': session.query(Creator).count(),
                'total_vas': session.query(VA).count(),
                'total_content_sets': session.query(ContentSet).count(),
                'total_posts': session.query(Post).count(),
                'total_slides': session.query(PostSlide).count(),
                'pending_scraping': session.query(ProofLog).filter(ProofLog.scraping_status == 'pending').count(),
                'successful_scraping': session.query(ProofLog).filter(ProofLog.scraping_status == 'success').count(),
                'failed_scraping': session.query(ProofLog).filter(ProofLog.scraping_status == 'failed').count(),
            }
            return stats
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    # Initialize database
    db_manager = ProofLogDatabaseManager()
    db_manager.create_tables()
    
    # Import proof log data
    csv_path = "/Users/felixhergenroeder/Downloads/Proof Log v2 - Proof_Log.csv"
    db_manager.import_proof_log_csv(csv_path)
    
    # Get database statistics
    stats = db_manager.get_database_stats()
    print("📊 Proof Log Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:,}")
    
    print("\n✅ Proof Log database schema created successfully!")
    print("🎯 Ready for comprehensive data collection and analysis!")
