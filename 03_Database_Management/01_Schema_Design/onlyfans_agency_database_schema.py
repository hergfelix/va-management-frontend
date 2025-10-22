"""
OnlyFans Agency Database Schema - TikTok to OnlyFans Conversion Analytics
Built with SuperClaude Backend Architect Agent

This schema is specifically designed for OnlyFans agencies using TikTok slideshows
to drive traffic and conversions to OnlyFans subscriptions.

Key Features:
- TikTok slideshow performance tracking
- OnlyFans conversion attribution
- Creator performance analysis
- VA effectiveness measurement
- Cross-platform content optimization
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

class OnlyFansCreator(Base):
    """
    OnlyFans creators (Tyra, Ariri, Naomi, etc.)
    """
    __tablename__ = 'onlyfans_creators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    
    # OnlyFans specific data
    onlyfans_username = Column(String(100), nullable=True, index=True)
    onlyfans_url = Column(String(500), nullable=True)
    subscription_price = Column(Float, nullable=True)  # Monthly subscription price
    content_type = Column(String(100), nullable=True)  # e.g., "fitness", "lifestyle", "fashion"
    
    # Creator attributes for content optimization
    creator_attributes = Column(JSON, nullable=True)  # e.g., {"body_type": "curvy", "style": "fitness", "age_range": "25-30"}
    target_demographics = Column(JSON, nullable=True)  # e.g., {"gender": "male", "age": "18-35", "interests": ["fitness", "lifestyle"]}
    
    # Performance tracking
    total_tiktok_posts = Column(Integer, default=0, nullable=False)
    total_onlyfans_subscribers = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(Float, default=0.0, nullable=False)  # TikTok views to OnlyFans conversions
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    revenue_per_month = Column(Float, default=0.0, nullable=False)
    
    # Status and management
    status = Column(String(20), default='active', nullable=False)  # active, inactive, suspended
    contract_start_date = Column(DateTime, nullable=True)
    contract_end_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_post_at = Column(DateTime, nullable=True)
    
    # Relationships
    content_sets = relationship("ContentSet", back_populates="creator")
    tiktok_posts = relationship("TikTokPost", back_populates="creator")
    conversion_events = relationship("ConversionEvent", back_populates="creator")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='creator_status_check'),
        CheckConstraint("subscription_price >= 0", name='subscription_price_positive_check'),
        CheckConstraint("conversion_rate >= 0.0", name='conversion_rate_positive_check'),
        CheckConstraint("revenue_per_month >= 0.0", name='revenue_positive_check'),
        Index('idx_creator_name_status', 'name', 'status'),
        Index('idx_creator_performance', 'conversion_rate', 'revenue_per_month'),
        Index('idx_creator_onlyfans_username', 'onlyfans_username'),
    )
    
    def __repr__(self):
        return f"<OnlyFansCreator(id={self.id}, name='{self.name}', subscribers={self.total_onlyfans_subscribers})>"

class VA(Base):
    """
    Virtual Assistants managing TikTok accounts
    """
    __tablename__ = 'vas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    
    # VA performance metrics
    accounts_managed = Column(Integer, default=0, nullable=False)
    total_posts_managed = Column(Integer, default=0, nullable=False)
    avg_conversion_rate = Column(Float, default=0.0, nullable=False)  # TikTok to OnlyFans conversion
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    total_revenue_generated = Column(Float, default=0.0, nullable=False)
    
    # VA attributes
    specializations = Column(JSON, nullable=True)  # e.g., ["fitness", "lifestyle", "fashion"]
    working_hours = Column(String(100), nullable=True)  # e.g., "9AM-5PM EST"
    timezone = Column(String(50), nullable=True)
    
    # Status and management
    status = Column(String(20), default='active', nullable=False)  # active, inactive, suspended
    hire_date = Column(DateTime, nullable=True)
    performance_rating = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tiktok_accounts = relationship("TikTokAccount", back_populates="va")
    tiktok_posts = relationship("TikTokPost", back_populates="va")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='va_status_check'),
        CheckConstraint("performance_rating >= 0.0 AND performance_rating <= 10.0", name='performance_rating_range_check'),
        CheckConstraint("avg_conversion_rate >= 0.0", name='va_conversion_rate_positive_check'),
        CheckConstraint("total_revenue_generated >= 0.0", name='va_revenue_positive_check'),
        Index('idx_va_name_status', 'name', 'status'),
        Index('idx_va_performance', 'performance_rating', 'avg_conversion_rate'),
    )
    
    def __repr__(self):
        return f"<VA(id={self.id}, name='{self.name}', rating={self.performance_rating}, revenue={self.total_revenue_generated})>"

class TikTokAccount(Base):
    """
    TikTok accounts used for OnlyFans promotion
    """
    __tablename__ = 'tiktok_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=False)
    
    # Account metadata
    bio = Column(Text, nullable=True)
    link_in_bio = Column(String(500), nullable=True)  # OnlyFans link
    verified = Column(Boolean, default=False, nullable=False)
    private = Column(Boolean, default=False, nullable=False)
    
    # Performance metrics
    followers = Column(Integer, default=0, nullable=False)
    following = Column(Integer, default=0, nullable=False)
    total_posts = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # OnlyFans conversion metrics
    total_conversions = Column(Integer, default=0, nullable=False)  # TikTok viewers who subscribed to OnlyFans
    conversion_rate = Column(Float, default=0.0, nullable=False)  # Views to OnlyFans conversions
    revenue_generated = Column(Float, default=0.0, nullable=False)  # Revenue from this account
    
    # Account strategy
    primary_creator_id = Column(Integer, ForeignKey('onlyfans_creators.id'), nullable=True)
    content_focus = Column(String(100), nullable=True)  # e.g., "fitness", "lifestyle", "fashion"
    target_audience = Column(JSON, nullable=True)  # e.g., {"gender": "male", "age": "18-35"}
    
    # Status and management
    status = Column(String(20), default='active', nullable=False)  # active, suspended, deleted
    account_quality_score = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_scraped_at = Column(DateTime, nullable=True)
    last_post_at = Column(DateTime, nullable=True)
    
    # Relationships
    va = relationship("VA", back_populates="tiktok_accounts")
    primary_creator = relationship("OnlyFansCreator")
    tiktok_posts = relationship("TikTokPost", back_populates="account")
    follower_snapshots = relationship("FollowerSnapshot", back_populates="account")
    conversion_events = relationship("ConversionEvent", back_populates="tiktok_account")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('active', 'suspended', 'deleted')", name='account_status_check'),
        CheckConstraint("followers >= 0", name='followers_positive_check'),
        CheckConstraint("conversion_rate >= 0.0", name='account_conversion_rate_positive_check'),
        CheckConstraint("revenue_generated >= 0.0", name='account_revenue_positive_check'),
        CheckConstraint("account_quality_score >= 0.0 AND account_quality_score <= 10.0", name='account_quality_score_range_check'),
        Index('idx_account_username_status', 'username', 'status'),
        Index('idx_account_va_status', 'va_id', 'status'),
        Index('idx_account_performance', 'conversion_rate', 'revenue_generated'),
        Index('idx_account_creator', 'primary_creator_id'),
    )
    
    def __repr__(self):
        return f"<TikTokAccount(id={self.id}, username='{self.username}', conversions={self.total_conversions})>"

class ContentSet(Base):
    """
    Content sets (slideshow collections) for OnlyFans creators
    """
    __tablename__ = 'content_sets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    set_id = Column(Integer, nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey('onlyfans_creators.id'), nullable=False)
    
    # Content set metadata
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), default='slideshow', nullable=False)  # slideshow, video, image
    theme = Column(String(100), nullable=True)  # e.g., "fitness", "lifestyle", "fashion"
    
    # OnlyFans specific content
    onlyfans_content_type = Column(String(100), nullable=True)  # e.g., "teaser", "preview", "promo"
    content_maturity = Column(String(20), default='safe', nullable=False)  # safe, suggestive, explicit
    target_conversion_goal = Column(Integer, nullable=True)  # Expected OnlyFans conversions
    
    # Performance tracking
    total_posts = Column(Integer, default=0, nullable=False)
    total_views = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    total_conversions = Column(Integer, default=0, nullable=False)  # OnlyFans conversions
    conversion_rate = Column(Float, default=0.0, nullable=False)  # Views to OnlyFans conversions
    revenue_generated = Column(Float, default=0.0, nullable=False)
    
    # Content analysis
    slides_count = Column(Integer, default=1, nullable=False)
    avg_slide_performance = Column(Float, default=0.0, nullable=False)
    best_performing_slides = Column(JSON, nullable=True)  # Array of slide numbers that perform best
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("OnlyFansCreator", back_populates="content_sets")
    tiktok_posts = relationship("TikTokPost", back_populates="content_set")
    slides = relationship("ContentSlide", back_populates="content_set", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("content_type IN ('slideshow', 'video', 'image')", name='content_type_check'),
        CheckConstraint("content_maturity IN ('safe', 'suggestive', 'explicit')", name='content_maturity_check'),
        CheckConstraint("slides_count > 0", name='slides_count_positive_check'),
        CheckConstraint("conversion_rate >= 0.0", name='content_set_conversion_rate_positive_check'),
        CheckConstraint("revenue_generated >= 0.0", name='content_set_revenue_positive_check'),
        UniqueConstraint('set_id', 'creator_id', name='_set_creator_uc'),
        Index('idx_content_set_creator', 'creator_id', 'set_id'),
        Index('idx_content_set_performance', 'conversion_rate', 'revenue_generated'),
        Index('idx_content_set_theme', 'theme'),
    )
    
    def __repr__(self):
        return f"<ContentSet(id={self.id}, set_id={self.set_id}, creator='{self.creator.name if self.creator else 'N/A'}', conversions={self.total_conversions})>"

class ContentSlide(Base):
    """
    Individual slides within content sets
    """
    __tablename__ = 'content_slides'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_set_id = Column(Integer, ForeignKey('content_sets.id'), nullable=False)
    slide_number = Column(Integer, nullable=False)
    slide_url = Column(String(500), nullable=False)
    
    # Content analysis
    ocr_text = Column(Text, nullable=True)
    text_hash = Column(String(64), nullable=True, index=True)
    has_text = Column(Boolean, default=False, nullable=False)
    
    # OnlyFans specific analysis
    content_category = Column(String(100), nullable=True)  # e.g., "teaser", "preview", "promo"
    visual_elements = Column(JSON, nullable=True)  # e.g., {"colors": ["red", "blue"], "objects": ["person", "clothing"]}
    appeal_factors = Column(JSON, nullable=True)  # e.g., ["fitness", "lifestyle", "fashion"]
    
    # Performance tracking
    total_views = Column(Integer, default=0, nullable=False)
    total_engagement = Column(Integer, default=0, nullable=False)
    conversions_generated = Column(Integer, default=0, nullable=False)  # OnlyFans conversions from this slide
    conversion_rate = Column(Float, default=0.0, nullable=False)
    
    # Slide effectiveness
    viral_potential_score = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    conversion_potential_score = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    reusability_score = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    content_set = relationship("ContentSet", back_populates="slides")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("slide_number > 0", name='slide_number_positive_check'),
        CheckConstraint("viral_potential_score >= 0.0 AND viral_potential_score <= 10.0", name='viral_potential_score_range_check'),
        CheckConstraint("conversion_potential_score >= 0.0 AND conversion_potential_score <= 10.0", name='conversion_potential_score_range_check'),
        CheckConstraint("reusability_score >= 0.0 AND reusability_score <= 10.0", name='reusability_score_range_check'),
        UniqueConstraint('content_set_id', 'slide_number', name='_content_set_slide_number_uc'),
        Index('idx_slide_content_set_number', 'content_set_id', 'slide_number'),
        Index('idx_slide_performance', 'conversion_rate', 'viral_potential_score'),
        Index('idx_slide_content_category', 'content_category'),
    )
    
    def __repr__(self):
        return f"<ContentSlide(id={self.id}, content_set_id={self.content_set_id}, slide_number={self.slide_number}, conversions={self.conversions_generated})>"

class TikTokPost(Base):
    """
    TikTok posts (slideshows) for OnlyFans promotion
    """
    __tablename__ = 'tiktok_posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_url = Column(String(500), unique=True, nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey('onlyfans_creators.id'), nullable=False)
    content_set_id = Column(Integer, ForeignKey('content_sets.id'), nullable=True)
    account_id = Column(Integer, ForeignKey('tiktok_accounts.id'), nullable=False)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=False)
    
    # Post metadata
    post_type = Column(String(20), nullable=False)  # NEW, REPOST
    post_id = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)  # Array of hashtags
    sound_url = Column(String(500), nullable=True)
    sound_title = Column(String(200), nullable=True)
    
    # Content metadata
    slides_count = Column(Integer, default=1, nullable=False)
    duration = Column(Float, nullable=True)  # in seconds
    content_type = Column(String(20), default='slideshow', nullable=False)  # slideshow, video, image
    
    # TikTok performance metrics
    views = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    bookmarks = Column(Integer, default=0, nullable=False)
    engagement = Column(Integer, default=0, nullable=False)
    engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # OnlyFans conversion metrics
    onlyfans_clicks = Column(Integer, default=0, nullable=False)  # Clicks on OnlyFans link
    onlyfans_conversions = Column(Integer, default=0, nullable=False)  # Actual OnlyFans subscriptions
    conversion_rate = Column(Float, default=0.0, nullable=False)  # Views to OnlyFans conversions
    revenue_generated = Column(Float, default=0.0, nullable=False)  # Revenue from this post
    
    # Performance analysis
    viral_score = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    conversion_score = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    roi_score = Column(Float, default=0.0, nullable=False)  # Return on investment score
    
    # Timestamps
    created_date = Column(DateTime, nullable=True)
    created_time = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("OnlyFansCreator", back_populates="tiktok_posts")
    content_set = relationship("ContentSet", back_populates="tiktok_posts")
    account = relationship("TikTokAccount", back_populates="tiktok_posts")
    va = relationship("VA", back_populates="tiktok_posts")
    metrics_snapshots = relationship("MetricsSnapshot", back_populates="tiktok_post", cascade="all, delete-orphan")
    conversion_events = relationship("ConversionEvent", back_populates="tiktok_post")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("post_type IN ('NEW', 'REPOST')", name='post_type_check'),
        CheckConstraint("content_type IN ('slideshow', 'video', 'image')", name='post_content_type_check'),
        CheckConstraint("slides_count > 0", name='post_slides_count_positive_check'),
        CheckConstraint("views >= 0", name='post_views_positive_check'),
        CheckConstraint("onlyfans_conversions >= 0", name='onlyfans_conversions_positive_check'),
        CheckConstraint("conversion_rate >= 0.0", name='post_conversion_rate_positive_check'),
        CheckConstraint("revenue_generated >= 0.0", name='post_revenue_positive_check'),
        CheckConstraint("viral_score >= 0.0 AND viral_score <= 10.0", name='viral_score_range_check'),
        CheckConstraint("conversion_score >= 0.0 AND conversion_score <= 10.0", name='conversion_score_range_check'),
        CheckConstraint("roi_score >= 0.0 AND roi_score <= 10.0", name='roi_score_range_check'),
        Index('idx_post_creator_content_set', 'creator_id', 'content_set_id'),
        Index('idx_post_account_created', 'account_id', 'created_date'),
        Index('idx_post_performance', 'views', 'conversion_rate'),
        Index('idx_post_va_performance', 'va_id', 'conversion_rate'),
    )
    
    def __repr__(self):
        return f"<TikTokPost(id={self.id}, creator='{self.creator.name if self.creator else 'N/A'}', views={self.views}, conversions={self.onlyfans_conversions})>"

class ConversionEvent(Base):
    """
    OnlyFans conversion events (when TikTok viewers subscribe)
    """
    __tablename__ = 'conversion_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tiktok_post_id = Column(Integer, ForeignKey('tiktok_posts.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('onlyfans_creators.id'), nullable=False)
    tiktok_account_id = Column(Integer, ForeignKey('tiktok_accounts.id'), nullable=False)
    
    # Conversion details
    conversion_type = Column(String(50), nullable=False)  # subscription, tip, message, etc.
    conversion_value = Column(Float, nullable=False)  # Revenue from this conversion
    subscription_duration = Column(Integer, nullable=True)  # Days subscribed
    
    # Attribution data
    attribution_source = Column(String(100), nullable=True)  # Which slide/content led to conversion
    user_demographics = Column(JSON, nullable=True)  # e.g., {"age": "25", "gender": "male", "location": "US"}
    conversion_path = Column(JSON, nullable=True)  # User journey from TikTok to OnlyFans
    
    # Timestamps
    conversion_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tiktok_post = relationship("TikTokPost", back_populates="conversion_events")
    creator = relationship("OnlyFansCreator", back_populates="conversion_events")
    tiktok_account = relationship("TikTokAccount", back_populates="conversion_events")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("conversion_type IN ('subscription', 'tip', 'message', 'custom_content')", name='conversion_type_check'),
        CheckConstraint("conversion_value >= 0.0", name='conversion_value_positive_check'),
        CheckConstraint("subscription_duration >= 0", name='subscription_duration_positive_check'),
        Index('idx_conversion_post', 'tiktok_post_id'),
        Index('idx_conversion_creator', 'creator_id'),
        Index('idx_conversion_timestamp', 'conversion_timestamp'),
        Index('idx_conversion_value', 'conversion_value'),
    )
    
    def __repr__(self):
        return f"<ConversionEvent(id={self.id}, creator='{self.creator.name if self.creator else 'N/A'}', value={self.conversion_value}, type='{self.conversion_type}')>"

class MetricsSnapshot(Base):
    """
    Time-series metrics snapshots for TikTok posts
    """
    __tablename__ = 'metrics_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tiktok_post_id = Column(Integer, ForeignKey('tiktok_posts.id'), nullable=False)
    
    # TikTok metrics
    views = Column(Integer, nullable=False)
    likes = Column(Integer, nullable=False)
    comments = Column(Integer, nullable=False)
    shares = Column(Integer, nullable=False)
    bookmarks = Column(Integer, nullable=False)
    engagement = Column(Integer, nullable=False)
    engagement_rate = Column(Float, nullable=False)
    
    # OnlyFans metrics
    onlyfans_clicks = Column(Integer, nullable=False)
    onlyfans_conversions = Column(Integer, nullable=False)
    conversion_rate = Column(Float, nullable=False)
    revenue_generated = Column(Float, nullable=False)
    
    # Snapshot metadata
    snapshot_type = Column(String(20), default='scheduled', nullable=False)  # scheduled, manual, api
    data_source = Column(String(50), default='scraper', nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tiktok_post = relationship("TikTokPost", back_populates="metrics_snapshots")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("views >= 0", name='snapshot_views_positive_check'),
        CheckConstraint("onlyfans_conversions >= 0", name='snapshot_conversions_positive_check'),
        CheckConstraint("conversion_rate >= 0.0", name='snapshot_conversion_rate_positive_check'),
        CheckConstraint("revenue_generated >= 0.0", name='snapshot_revenue_positive_check'),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name='snapshot_confidence_score_range_check'),
        UniqueConstraint('tiktok_post_id', 'timestamp', name='_tiktok_post_timestamp_uc'),
        Index('idx_metrics_post_timestamp', 'tiktok_post_id', 'timestamp'),
        Index('idx_metrics_timestamp', 'timestamp'),
        Index('idx_metrics_conversion_rate', 'conversion_rate'),
    )
    
    def __repr__(self):
        return f"<MetricsSnapshot(id={self.id}, tiktok_post_id={self.tiktok_post_id}, conversions={self.onlyfans_conversions}, timestamp='{self.timestamp}')>"

class FollowerSnapshot(Base):
    """
    TikTok account follower snapshots for growth tracking
    """
    __tablename__ = 'follower_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('tiktok_accounts.id'), nullable=False)
    
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
    account = relationship("TikTokAccount", back_populates="follower_snapshots")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("followers >= 0", name='follower_snapshot_followers_positive_check'),
        CheckConstraint("following >= 0", name='follower_snapshot_following_positive_check'),
        CheckConstraint("posts_count >= 0", name='follower_snapshot_posts_count_positive_check'),
        CheckConstraint("likes_count >= 0", name='follower_snapshot_likes_count_positive_check'),
        CheckConstraint("confidence_score >= 0.0 AND confidence_score <= 1.0", name='follower_snapshot_confidence_score_range_check'),
        UniqueConstraint('account_id', 'timestamp', name='_account_timestamp_uc'),
        Index('idx_follower_account_timestamp', 'account_id', 'timestamp'),
        Index('idx_follower_timestamp', 'timestamp'),
        Index('idx_follower_snapshot_type', 'snapshot_type'),
    )
    
    def __repr__(self):
        return f"<FollowerSnapshot(id={self.id}, account_id={self.account_id}, followers={self.followers}, timestamp='{self.timestamp}')>"

# Database utility functions
class OnlyFansAgencyDatabaseManager:
    """
    Database management utilities for OnlyFans agency analytics
    """
    
    def __init__(self, database_url: str = "sqlite:///onlyfans_agency_analytics.db"):
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
    
    def import_proof_log_data(self, csv_path: str):
        """Import proof log data from CSV and map to OnlyFans agency structure"""
        import pandas as pd
        from datetime import datetime
        
        session = self.get_session()
        try:
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                # Create or get OnlyFans creator
                creator = session.query(OnlyFansCreator).filter(
                    OnlyFansCreator.name == row['Creator']
                ).first()
                
                if not creator:
                    creator = OnlyFansCreator(
                        name=row['Creator'],
                        display_name=row['Creator']
                    )
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
                            creator_id=creator.id,
                            name=f"Set {row['Set ID']} - {creator.name}"
                        )
                        session.add(content_set)
                        session.flush()
                
                # Create or get TikTok account (extract from URL)
                account_username = self._extract_username_from_url(row['Post URL'])
                account = None
                if account_username:
                    account = session.query(TikTokAccount).filter(
                        TikTokAccount.username == account_username
                    ).first()
                    
                    if not account:
                        account = TikTokAccount(
                            username=account_username,
                            va_id=va.id,
                            primary_creator_id=creator.id
                        )
                        session.add(account)
                        session.flush()
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['Timestamp'].replace('Z', '+00:00'))
                
                # Create TikTok post entry
                tiktok_post = TikTokPost(
                    post_url=row['Post URL'],
                    creator_id=creator.id,
                    content_set_id=content_set.id if content_set else None,
                    account_id=account.id if account else None,
                    va_id=va.id,
                    post_type=row['Type'],
                    created_date=timestamp,
                    created_time=timestamp
                )
                
                session.add(tiktok_post)
            
            session.commit()
            print(f"✅ Successfully imported {len(df)} OnlyFans agency posts")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error importing OnlyFans agency data: {e}")
            raise
        finally:
            session.close()
    
    def _extract_username_from_url(self, url: str) -> str:
        """Extract TikTok username from URL"""
        import re
        match = re.search(r'tiktok\.com/@([^/?]+)', url)
        return match.group(1) if match else None
    
    def get_agency_analytics(self):
        """Get comprehensive OnlyFans agency analytics"""
        session = self.get_session()
        try:
            analytics = {
                'total_creators': session.query(OnlyFansCreator).count(),
                'total_vas': session.query(VA).count(),
                'total_tiktok_accounts': session.query(TikTokAccount).count(),
                'total_content_sets': session.query(ContentSet).count(),
                'total_tiktok_posts': session.query(TikTokPost).count(),
                'total_conversions': session.query(ConversionEvent).count(),
                'total_revenue': session.query(func.sum(ConversionEvent.conversion_value)).scalar() or 0,
                'avg_conversion_rate': session.query(func.avg(TikTokPost.conversion_rate)).scalar() or 0,
                'top_performing_creator': self._get_top_performing_creator(session),
                'top_performing_va': self._get_top_performing_va(session),
                'top_converting_content_set': self._get_top_converting_content_set(session)
            }
            return analytics
        finally:
            session.close()
    
    def _get_top_performing_creator(self, session):
        """Get top performing OnlyFans creator"""
        result = session.query(OnlyFansCreator).order_by(
            OnlyFansCreator.conversion_rate.desc()
        ).first()
        return result.name if result else None
    
    def _get_top_performing_va(self, session):
        """Get top performing VA"""
        result = session.query(VA).order_by(
            VA.avg_conversion_rate.desc()
        ).first()
        return result.name if result else None
    
    def _get_top_converting_content_set(self, session):
        """Get top converting content set"""
        result = session.query(ContentSet).order_by(
            ContentSet.conversion_rate.desc()
        ).first()
        return f"Set {result.set_id} - {result.creator.name}" if result else None

# Example usage
if __name__ == "__main__":
    # Initialize database
    db_manager = OnlyFansAgencyDatabaseManager()
    db_manager.create_tables()
    
    # Import proof log data
    csv_path = "/Users/felixhergenroeder/Downloads/Proof Log v2 - Proof_Log.csv"
    db_manager.import_proof_log_data(csv_path)
    
    # Get agency analytics
    analytics = db_manager.get_agency_analytics()
    print("📊 OnlyFans Agency Analytics:")
    for key, value in analytics.items():
        print(f"  {key}: {value}")
    
    print("\n✅ OnlyFans agency database schema created successfully!")
    print("🎯 Ready for TikTok to OnlyFans conversion analytics!")
