"""
TikTok Analytics Database - Simplified for Level 1
Focus: Tracking & Scraping for Team Inspiration

This simplified schema focuses on:
1. Tracking TikTok posts and their performance
2. Scraping current metrics
3. Providing team with performance insights
4. Basic creator and VA tracking

Revenue and conversion tracking will be added later.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Text, Boolean,
    ForeignKey, Index, UniqueConstraint, CheckConstraint,
    create_engine, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class Creator(Base):
    """
    Content creators (Tyra, Ariri, Naomi, etc.)
    """
    __tablename__ = 'creators'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    
    # Basic tracking
    total_posts = Column(Integer, default=0, nullable=False)
    total_views = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Status
    status = Column(String(20), default='active', nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_post_at = Column(DateTime, nullable=True)
    
    # Relationships
    content_sets = relationship("ContentSet", back_populates="creator")
    tiktok_posts = relationship("TikTokPost", back_populates="creator")
    
    def __repr__(self):
        return f"<Creator(id={self.id}, name='{self.name}', posts={self.total_posts})>"

class VA(Base):
    """
    Virtual Assistants managing TikTok accounts
    """
    __tablename__ = 'vas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    
    # Basic performance tracking
    accounts_managed = Column(Integer, default=0, nullable=False)
    total_posts_managed = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Status
    status = Column(String(20), default='active', nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tiktok_accounts = relationship("TikTokAccount", back_populates="va")
    tiktok_posts = relationship("TikTokPost", back_populates="va")
    
    def __repr__(self):
        return f"<VA(id={self.id}, name='{self.name}', accounts={self.accounts_managed})>"

class TikTokAccount(Base):
    """
    TikTok accounts for content promotion
    """
    __tablename__ = 'tiktok_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=False)
    
    # Account metrics
    followers = Column(Integer, default=0, nullable=False)
    following = Column(Integer, default=0, nullable=False)
    total_posts = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Status
    status = Column(String(20), default='active', nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_scraped_at = Column(DateTime, nullable=True)
    last_post_at = Column(DateTime, nullable=True)
    
    # Relationships
    va = relationship("VA", back_populates="tiktok_accounts")
    tiktok_posts = relationship("TikTokPost", back_populates="account")
    follower_snapshots = relationship("FollowerSnapshot", back_populates="account")
    
    def __repr__(self):
        return f"<TikTokAccount(id={self.id}, username='{self.username}', followers={self.followers})>"

class ContentSet(Base):
    """
    Content sets (slideshow collections) for creators
    """
    __tablename__ = 'content_sets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    set_id = Column(Integer, nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey('creators.id'), nullable=False)
    
    # Content metadata
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), default='slideshow', nullable=False)
    theme = Column(String(100), nullable=True)
    
    # Performance tracking
    total_posts = Column(Integer, default=0, nullable=False)
    total_views = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Content analysis
    slides_count = Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("Creator", back_populates="content_sets")
    tiktok_posts = relationship("TikTokPost", back_populates="content_set")
    slides = relationship("ContentSlide", back_populates="content_set", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContentSet(id={self.id}, set_id={self.set_id}, creator='{self.creator.name if self.creator else 'N/A'}')>"

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
    
    # Performance tracking
    total_views = Column(Integer, default=0, nullable=False)
    total_engagement = Column(Integer, default=0, nullable=False)
    avg_engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    content_set = relationship("ContentSet", back_populates="slides")
    
    def __repr__(self):
        return f"<ContentSlide(id={self.id}, content_set_id={self.content_set_id}, slide_number={self.slide_number})>"

class TikTokPost(Base):
    """
    TikTok posts (slideshows) for content promotion
    """
    __tablename__ = 'tiktok_posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_url = Column(String(500), unique=True, nullable=False, index=True)
    creator_id = Column(Integer, ForeignKey('creators.id'), nullable=False)
    content_set_id = Column(Integer, ForeignKey('content_sets.id'), nullable=True)
    account_id = Column(Integer, ForeignKey('tiktok_accounts.id'), nullable=False)
    va_id = Column(Integer, ForeignKey('vas.id'), nullable=False)
    
    # Post metadata
    post_type = Column(String(20), nullable=False)  # NEW, REPOST
    post_id = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)  # JSON string for simplicity
    sound_url = Column(String(500), nullable=True)
    sound_title = Column(String(200), nullable=True)
    
    # Content metadata
    slides_count = Column(Integer, default=1, nullable=False)
    duration = Column(Float, nullable=True)
    content_type = Column(String(20), default='slideshow', nullable=False)
    
    # TikTok performance metrics
    views = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    bookmarks = Column(Integer, default=0, nullable=False)
    engagement = Column(Integer, default=0, nullable=False)
    engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Performance analysis
    viral_score = Column(Float, default=0.0, nullable=False)  # 1-10 rating
    performance_trend = Column(String(20), default='stable', nullable=False)  # growing, stable, declining
    
    # Timestamps
    created_date = Column(DateTime, nullable=True)
    created_time = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("Creator", back_populates="tiktok_posts")
    content_set = relationship("ContentSet", back_populates="tiktok_posts")
    account = relationship("TikTokAccount", back_populates="tiktok_posts")
    va = relationship("VA", back_populates="tiktok_posts")
    metrics_snapshots = relationship("MetricsSnapshot", back_populates="tiktok_post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TikTokPost(id={self.id}, creator='{self.creator.name if self.creator else 'N/A'}', views={self.views})>"

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
    
    # Snapshot metadata
    snapshot_type = Column(String(20), default='scheduled', nullable=False)
    data_source = Column(String(50), default='scraper', nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tiktok_post = relationship("TikTokPost", back_populates="metrics_snapshots")
    
    def __repr__(self):
        return f"<MetricsSnapshot(id={self.id}, tiktok_post_id={self.tiktok_post_id}, views={self.views}, timestamp='{self.timestamp}')>"

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
    snapshot_type = Column(String(20), default='scheduled', nullable=False)
    data_source = Column(String(50), default='scraper', nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("TikTokAccount", back_populates="follower_snapshots")
    
    def __repr__(self):
        return f"<FollowerSnapshot(id={self.id}, account_id={self.account_id}, followers={self.followers}, timestamp='{self.timestamp}')>"

# Database utility functions
class TikTokAnalyticsDatabase:
    """
    Simplified database manager for TikTok analytics tracking
    """
    
    def __init__(self, database_url: str = "sqlite:///tiktok_analytics.db"):
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        print("✅ TikTok analytics database tables created")
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def import_proof_log_data(self, csv_path: str):
        """Import proof log data from CSV"""
        import pandas as pd
        from datetime import datetime
        import re
        
        session = self.get_session()
        try:
            df = pd.read_csv(csv_path)
            print(f"📊 Importing {len(df)} posts from Proof Log...")
            
            imported_count = 0
            for _, row in df.iterrows():
                # Create or get creator
                creator = session.query(Creator).filter(
                    Creator.name == row['Creator']
                ).first()
                
                if not creator:
                    creator = Creator(
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
                
                # Extract username from URL
                account_username = self._extract_username_from_url(row['Post URL'])
                account = None
                if account_username:
                    account = session.query(TikTokAccount).filter(
                        TikTokAccount.username == account_username
                    ).first()
                    
                    if not account:
                        account = TikTokAccount(
                            username=account_username,
                            va_id=va.id
                        )
                        session.add(account)
                        session.flush()
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['Timestamp'].replace('Z', '+00:00'))
                
                # Create TikTok post
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
                imported_count += 1
            
            session.commit()
            print(f"✅ Successfully imported {imported_count} posts")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error importing Proof Log data: {e}")
            raise
        finally:
            session.close()
    
    def import_master_database(self, csv_path: str):
        """Import master TikTok database"""
        import pandas as pd
        from datetime import datetime
        
        session = self.get_session()
        try:
            df = pd.read_csv(csv_path)
            print(f"📊 Importing {len(df)} posts from Master Database...")
            
            imported_count = 0
            for _, row in df.iterrows():
                # Create or get creator
                creator = session.query(Creator).filter(
                    Creator.name == row['creator']
                ).first()
                
                if not creator:
                    creator = Creator(
                        name=row['creator'],
                        display_name=row['creator']
                    )
                    session.add(creator)
                    session.flush()
                
                # Create or get VA
                va = session.query(VA).filter(
                    VA.name == row['va']
                ).first()
                
                if not va:
                    va = VA(name=row['va'])
                    session.add(va)
                    session.flush()
                
                # Extract username from URL
                account_username = self._extract_username_from_url(row['post_url'])
                account = None
                if account_username:
                    account = session.query(TikTokAccount).filter(
                        TikTokAccount.username == account_username
                    ).first()
                    
                    if not account:
                        account = TikTokAccount(
                            username=account_username,
                            va_id=va.id
                        )
                        session.add(account)
                        session.flush()
                
                # Parse timestamp
                created_date = datetime.strptime(row['created_date'], '%Y-%m-%d')
                created_time = datetime.strptime(row['created_time'], '%H:%M:%S')
                
                # Create TikTok post with metrics
                tiktok_post = TikTokPost(
                    post_url=row['post_url'],
                    creator_id=creator.id,
                    account_id=account.id if account else None,
                    va_id=va.id,
                    post_type='NEW',  # Default for master database
                    created_date=created_date,
                    created_time=created_time,
                    views=row['views'],
                    likes=row['likes'],
                    comments=row['comments'],
                    shares=row['shares'],
                    engagement=row['engagement'],
                    engagement_rate=row['engagement_rate'],
                    hashtags=row['hashtags'],
                    sound_url=row['sound'],
                    slides_count=row['slides']
                )
                
                session.add(tiktok_post)
                imported_count += 1
            
            session.commit()
            print(f"✅ Successfully imported {imported_count} posts from Master Database")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error importing Master Database: {e}")
            raise
        finally:
            session.close()
    
    def _extract_username_from_url(self, url: str) -> str:
        """Extract TikTok username from URL"""
        import re
        match = re.search(r'tiktok\.com/@([^/?]+)', url)
        return match.group(1) if match else None
    
    def get_team_insights(self):
        """Get insights for team inspiration"""
        session = self.get_session()
        try:
            insights = {
                'total_creators': session.query(Creator).count(),
                'total_vas': session.query(VA).count(),
                'total_accounts': session.query(TikTokAccount).count(),
                'total_posts': session.query(TikTokPost).count(),
                'total_views': session.query(func.sum(TikTokPost.views)).scalar() or 0,
                'total_likes': session.query(func.sum(TikTokPost.likes)).scalar() or 0,
                'avg_engagement_rate': session.query(func.avg(TikTokPost.engagement_rate)).scalar() or 0,
                'top_performing_creator': self._get_top_performing_creator(session),
                'top_performing_va': self._get_top_performing_va(session),
                'top_performing_account': self._get_top_performing_account(session),
                'recent_viral_posts': self._get_recent_viral_posts(session)
            }
            return insights
        finally:
            session.close()
    
    def _get_top_performing_creator(self, session):
        """Get top performing creator by engagement rate"""
        result = session.query(Creator).order_by(
            Creator.avg_engagement_rate.desc()
        ).first()
        return result.name if result else None
    
    def _get_top_performing_va(self, session):
        """Get top performing VA by engagement rate"""
        result = session.query(VA).order_by(
            VA.avg_engagement_rate.desc()
        ).first()
        return result.name if result else None
    
    def _get_top_performing_account(self, session):
        """Get top performing account by engagement rate"""
        result = session.query(TikTokAccount).order_by(
            TikTokAccount.avg_engagement_rate.desc()
        ).first()
        return result.username if result else None
    
    def _get_recent_viral_posts(self, session, limit=5):
        """Get recent viral posts"""
        results = session.query(TikTokPost).order_by(
            TikTokPost.views.desc()
        ).limit(limit).all()
        
        return [
            {
                'post_url': post.post_url,
                'creator': post.creator.name,
                'views': post.views,
                'likes': post.likes,
                'engagement_rate': post.engagement_rate
            }
            for post in results
        ]

# Example usage
if __name__ == "__main__":
    # Initialize database
    db = TikTokAnalyticsDatabase()
    db.create_tables()
    
    # Import data
    proof_log_path = "/Users/felixhergenroeder/Downloads/Proof Log v2 - Proof_Log.csv"
    master_db_path = "MASTER_TIKTOK_DATABASE.csv"
    
    try:
        db.import_proof_log_data(proof_log_path)
    except Exception as e:
        print(f"⚠️ Could not import Proof Log: {e}")
    
    try:
        db.import_master_database(master_db_path)
    except Exception as e:
        print(f"⚠️ Could not import Master Database: {e}")
    
    # Get team insights
    insights = db.get_team_insights()
    print("\n📊 TEAM INSIGHTS:")
    for key, value in insights.items():
        print(f"  {key}: {value}")
    
    print("\n✅ TikTok analytics database setup complete!")
