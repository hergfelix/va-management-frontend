#!/usr/bin/env python3
"""
SQLAlchemy Models for TikTok Analytics Master Database
Created for Issue #1: Setup Master Database Schema
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.postgresql import JSONB, UUID  # Only for PostgreSQL
from datetime import datetime
import uuid

Base = declarative_base()


class VA(Base):
    """
    Virtual Assistants table
    Tracks VA information including creator, set_id, set_code
    """
    __tablename__ = 'vas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    creator = Column(String(100), nullable=True)
    set_id = Column(String(50), nullable=True)
    set_code = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="va")
    metrics_history = relationship("MetricsHistory", back_populates="va")
    
    def __repr__(self):
        return f"<VA(name='{self.name}', creator='{self.creator}')>"


class Post(Base):
    """
    Main posts table with all TikTok post data
    """
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_url = Column(String(500), nullable=False, unique=True, index=True)
    account = Column(String(100), nullable=False, index=True)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=True, index=True)
    
    # Timestamps
    created_date = Column(DateTime, nullable=False, index=True)
    created_time = Column(String(10), nullable=True)  # Store as string for now
    
    # Metrics
    views = Column(Integer, nullable=False, default=0)
    likes = Column(Integer, nullable=False, default=0)
    comments = Column(Integer, nullable=False, default=0)
    shares = Column(Integer, nullable=False, default=0)
    engagement = Column(Integer, nullable=False, default=0)
    engagement_rate = Column(Float, nullable=True)
    
    # Content
    hashtags = Column(Text, nullable=True)
    sound = Column(Text, nullable=True)
    slides = Column(Text, nullable=True)  # Pipe-separated URLs
    
    # Metadata
    source = Column(String(50), nullable=False, index=True)  # old_clean, current_metrics, etc.
    scraping_status = Column(String(20), default='active', nullable=False)  # active, paused, completed
    days_since_posted = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    va = relationship("VA", back_populates="posts")
    metrics_history = relationship("MetricsHistory", back_populates="post")
    slides_data = relationship("Slide", back_populates="post")
    
    # Indexes
    __table_args__ = (
        Index('idx_posts_va_date', 'va_id', 'created_date'),
        Index('idx_posts_account_date', 'account', 'created_date'),
        Index('idx_posts_views', 'views'),
        Index('idx_posts_engagement', 'engagement'),
        CheckConstraint('views >= 0', name='check_views_positive'),
        CheckConstraint('likes >= 0', name='check_likes_positive'),
        CheckConstraint('comments >= 0', name='check_comments_positive'),
        CheckConstraint('shares >= 0', name='check_shares_positive'),
        CheckConstraint('engagement >= 0', name='check_engagement_positive'),
    )
    
    def __repr__(self):
        return f"<Post(account='{self.account}', views={self.views}, date='{self.created_date}')>"


class MetricsHistory(Base):
    """
    Time series data for tracking metrics over time
    """
    __tablename__ = 'metrics_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, index=True)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=True, index=True)
    
    # Metrics snapshot
    views = Column(Integer, nullable=False)
    likes = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    shares = Column(Integer, nullable=False)
    engagement = Column(Integer, nullable=False)
    engagement_rate = Column(Float, nullable=True)
    
    # Metadata
    snapshot_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    days_since_posted = Column(Integer, nullable=True)
    
    # Relationships
    post = relationship("Post", back_populates="metrics_history")
    va = relationship("VA", back_populates="metrics_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_post_date', 'post_id', 'snapshot_date'),
        Index('idx_metrics_va_date', 'va_id', 'snapshot_date'),
        UniqueConstraint('post_id', 'snapshot_date', name='unique_post_snapshot'),
    )
    
    def __repr__(self):
        return f"<MetricsHistory(post_id={self.post_id}, views={self.views}, date='{self.snapshot_date}')>"


class Slide(Base):
    """
    Individual slides with OCR text and metadata
    """
    __tablename__ = 'slides'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, index=True)
    
    # Slide data
    slide_url = Column(String(1000), nullable=False)
    slide_index = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, nullable=True)
    
    # Metadata
    image_hash = Column(String(64), nullable=True, index=True)  # MD5 hash for duplicate detection
    file_size = Column(Integer, nullable=True)
    dimensions = Column(String(20), nullable=True)  # "1920x1080"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("Post", back_populates="slides_data")
    
    # Indexes
    __table_args__ = (
        Index('idx_slides_post_index', 'post_id', 'slide_index'),
        Index('idx_slides_hash', 'image_hash'),
        UniqueConstraint('post_id', 'slide_index', name='unique_post_slide'),
    )
    
    def __repr__(self):
        return f"<Slide(post_id={self.post_id}, index={self.slide_index}, has_text={bool(self.ocr_text)})>"


class ScrapingJob(Base):
    """
    Track scraping jobs and their status
    """
    __tablename__ = 'scraping_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_name = Column(String(100), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)  # 'daily_update', 'full_scrape', 'manual'
    
    # Status tracking
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    posts_processed = Column(Integer, default=0)
    posts_updated = Column(Integer, default=0)
    posts_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Configuration
    config = Column(Text, nullable=True)  # Store job configuration as JSON (Text for SQLite compatibility)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ScrapingJob(name='{self.job_name}', status='{self.status}')>"


class ContentTemplate(Base):
    """
    Generated content templates for reposting
    """
    __tablename__ = 'content_templates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, index=True)
    
    # Template data
    original_text = Column(Text, nullable=False)
    variation_1 = Column(Text, nullable=True)
    variation_2 = Column(Text, nullable=True)
    variation_3 = Column(Text, nullable=True)
    
    # Performance metrics
    avg_views = Column(Integer, nullable=True)
    category = Column(String(50), nullable=True)
    
    # Metadata
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ContentTemplate(post_id={self.original_post_id}, category='{self.category}')>"


class RepostCandidate(Base):
    """
    Posts identified as good candidates for reposting
    """
    __tablename__ = 'repost_candidates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_post_id = Column(Integer, ForeignKey('posts.id'), nullable=False, index=True)
    
    # Candidate data
    repost_type = Column(String(50), nullable=False)  # 'same_account', 'cross_account', 'viral_recycle'
    score = Column(Float, nullable=False)  # 0-100 score for repost potential
    reason = Column(Text, nullable=True)  # Why this is a good candidate
    
    # Performance prediction
    predicted_views = Column(Integer, nullable=True)
    predicted_engagement = Column(Integer, nullable=True)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RepostCandidate(post_id={self.original_post_id}, type='{self.repost_type}', score={self.score})>"


# Additional utility tables for system management

class SystemConfig(Base):
    """
    System configuration and settings
    """
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value}')>"


class DataImportLog(Base):
    """
    Log of data imports and migrations
    """
    __tablename__ = 'data_import_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    import_type = Column(String(50), nullable=False)  # 'csv_import', 'google_sheets', 'migration'
    source = Column(String(200), nullable=False)
    
    # Results
    records_processed = Column(Integer, default=0)
    records_imported = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), nullable=False, default='running')  # running, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DataImportLog(type='{self.import_type}', status='{self.status}')>"
