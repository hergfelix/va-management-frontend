#!/usr/bin/env python3
"""
Comprehensive tests for TikTok Analytics Database Models
Created for Issue #1: Setup Master Database Schema
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import our models
from database.models import (
    Base, VA, Post, MetricsHistory, Slide, ScrapingJob,
    ContentTemplate, RepostCandidate, SystemConfig, DataImportLog
)


@pytest.fixture
def db_session():
    """Create a temporary database for testing"""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create engine with SQLite
    engine = create_engine(
        f'sqlite:///{db_path}',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    os.close(db_fd)
    os.unlink(db_path)


class TestVAModel:
    """Test VA model functionality"""
    
    def test_create_va(self, db_session):
        """Test creating a VA"""
        va = VA(
            name="TestVA",
            creator="TestCreator",
            set_id="SET123",
            set_code="CODE456"
        )
        db_session.add(va)
        db_session.commit()
        
        assert va.id is not None
        assert va.name == "TestVA"
        assert va.creator == "TestCreator"
        assert va.set_id == "SET123"
        assert va.set_code == "CODE456"
        assert va.is_active is True
        assert va.created_at is not None
        assert va.updated_at is not None
    
    def test_va_unique_name(self, db_session):
        """Test VA name uniqueness constraint"""
        va1 = VA(name="TestVA")
        va2 = VA(name="TestVA")  # Same name
        
        db_session.add(va1)
        db_session.commit()
        
        db_session.add(va2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_va_relationships(self, db_session):
        """Test VA relationships with posts"""
        va = VA(name="TestVA")
        db_session.add(va)
        db_session.commit()
        
        # Create a post for this VA
        post = Post(
            post_url="https://tiktok.com/test",
            account="test_account",
            va_id=va.id,
            created_date=datetime.now(),
            views=1000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        # Test relationship
        assert len(va.posts) == 1
        assert va.posts[0].post_url == "https://tiktok.com/test"


class TestPostModel:
    """Test Post model functionality"""
    
    def test_create_post(self, db_session):
        """Test creating a post"""
        post = Post(
            post_url="https://tiktok.com/test",
            account="test_account",
            created_date=datetime.now(),
            views=1000,
            likes=50,
            comments=10,
            shares=5,
            engagement=65,
            engagement_rate=6.5,
            hashtags="#test #viral",
            sound="https://tiktok.com/music/test",
            slides="https://image1.jpg|https://image2.jpg",
            source="test_source"
        )
        db_session.add(post)
        db_session.commit()
        
        assert post.id is not None
        assert post.post_url == "https://tiktok.com/test"
        assert post.account == "test_account"
        assert post.views == 1000
        assert post.engagement == 65
        assert post.engagement_rate == 6.5
        assert post.scraping_status == "active"
    
    def test_post_unique_url(self, db_session):
        """Test post URL uniqueness constraint"""
        post1 = Post(
            post_url="https://tiktok.com/test",
            account="test1",
            created_date=datetime.now(),
            views=1000,
            source="test"
        )
        post2 = Post(
            post_url="https://tiktok.com/test",  # Same URL
            account="test2",
            created_date=datetime.now(),
            views=2000,
            source="test"
        )
        
        db_session.add(post1)
        db_session.commit()
        
        db_session.add(post2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_post_positive_constraints(self, db_session):
        """Test post positive value constraints"""
        # Test negative views
        post = Post(
            post_url="https://tiktok.com/test",
            account="test",
            created_date=datetime.now(),
            views=-100,  # Negative value
            source="test"
        )
        db_session.add(post)
        with pytest.raises(Exception):  # Should raise constraint error
            db_session.commit()
    
    def test_post_relationships(self, db_session):
        """Test post relationships"""
        va = VA(name="TestVA")
        db_session.add(va)
        db_session.commit()
        
        post = Post(
            post_url="https://tiktok.com/test",
            account="test_account",
            va_id=va.id,
            created_date=datetime.now(),
            views=1000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        # Test VA relationship
        assert post.va.name == "TestVA"
        
        # Test metrics history relationship
        metrics = MetricsHistory(
            post_id=post.id,
            va_id=va.id,
            views=1200,
            likes=60,
            comments=12,
            shares=6,
            engagement=78,
            engagement_rate=6.5
        )
        db_session.add(metrics)
        db_session.commit()
        
        assert len(post.metrics_history) == 1
        assert post.metrics_history[0].views == 1200


class TestMetricsHistoryModel:
    """Test MetricsHistory model functionality"""
    
    def test_create_metrics_history(self, db_session):
        """Test creating metrics history entry"""
        post = Post(
            post_url="https://tiktok.com/test",
            account="test",
            created_date=datetime.now(),
            views=1000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        metrics = MetricsHistory(
            post_id=post.id,
            views=1200,
            likes=60,
            comments=12,
            shares=6,
            engagement=78,
            engagement_rate=6.5,
            days_since_posted=1
        )
        db_session.add(metrics)
        db_session.commit()
        
        assert metrics.id is not None
        assert metrics.post_id == post.id
        assert metrics.views == 1200
        assert metrics.days_since_posted == 1
        assert metrics.snapshot_date is not None
    
    def test_metrics_unique_constraint(self, db_session):
        """Test unique constraint on post_id and snapshot_date"""
        post = Post(
            post_url="https://tiktok.com/test",
            account="test",
            created_date=datetime.now(),
            views=1000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        # Create first metrics entry
        metrics1 = MetricsHistory(
            post_id=post.id,
            views=1000,
            likes=50,
            comments=10,
            shares=5,
            engagement=65
        )
        db_session.add(metrics1)
        db_session.commit()
        
        # Try to create second entry with same post_id and snapshot_date
        metrics2 = MetricsHistory(
            post_id=post.id,
            views=1200,
            likes=60,
            comments=12,
            shares=6,
            engagement=78
        )
        db_session.add(metrics2)
        with pytest.raises(Exception):  # Should raise unique constraint error
            db_session.commit()


class TestSlideModel:
    """Test Slide model functionality"""
    
    def test_create_slide(self, db_session):
        """Test creating a slide"""
        post = Post(
            post_url="https://tiktok.com/test",
            account="test",
            created_date=datetime.now(),
            views=1000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        slide = Slide(
            post_id=post.id,
            slide_url="https://image1.jpg",
            slide_index=1,
            ocr_text="This is test text",
            ocr_confidence=0.95,
            image_hash="abc123def456",
            file_size=1024000,
            dimensions="1920x1080"
        )
        db_session.add(slide)
        db_session.commit()
        
        assert slide.id is not None
        assert slide.post_id == post.id
        assert slide.slide_index == 1
        assert slide.ocr_text == "This is test text"
        assert slide.ocr_confidence == 0.95
        assert slide.image_hash == "abc123def456"
    
    def test_slide_unique_constraint(self, db_session):
        """Test unique constraint on post_id and slide_index"""
        post = Post(
            post_url="https://tiktok.com/test",
            account="test",
            created_date=datetime.now(),
            views=1000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        # Create first slide
        slide1 = Slide(
            post_id=post.id,
            slide_url="https://image1.jpg",
            slide_index=1
        )
        db_session.add(slide1)
        db_session.commit()
        
        # Try to create second slide with same post_id and slide_index
        slide2 = Slide(
            post_id=post.id,
            slide_url="https://image2.jpg",
            slide_index=1  # Same index
        )
        db_session.add(slide2)
        with pytest.raises(Exception):  # Should raise unique constraint error
            db_session.commit()


class TestScrapingJobModel:
    """Test ScrapingJob model functionality"""
    
    def test_create_scraping_job(self, db_session):
        """Test creating a scraping job"""
        job = ScrapingJob(
            job_name="daily_update",
            job_type="daily_update",
            status="pending",
            posts_processed=0,
            posts_updated=0,
            posts_failed=0,
            config='{"interval": "daily", "batch_size": 100}'
        )
        db_session.add(job)
        db_session.commit()
        
        assert job.id is not None
        assert job.job_name == "daily_update"
        assert job.job_type == "daily_update"
        assert job.status == "pending"
        assert job.config == '{"interval": "daily", "batch_size": 100}'
    
    def test_scraping_job_status_transitions(self, db_session):
        """Test scraping job status transitions"""
        job = ScrapingJob(
            job_name="test_job",
            job_type="manual",
            status="pending"
        )
        db_session.add(job)
        db_session.commit()
        
        # Start job
        job.status = "running"
        job.started_at = datetime.now()
        db_session.commit()
        
        # Complete job
        job.status = "completed"
        job.completed_at = datetime.now()
        job.posts_processed = 100
        job.posts_updated = 95
        job.posts_failed = 5
        db_session.commit()
        
        assert job.status == "completed"
        assert job.started_at is not None
        assert job.completed_at is not None
        assert job.posts_processed == 100


class TestContentTemplateModel:
    """Test ContentTemplate model functionality"""
    
    def test_create_content_template(self, db_session):
        """Test creating a content template"""
        post = Post(
            post_url="https://tiktok.com/test",
            account="test",
            created_date=datetime.now(),
            views=10000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        template = ContentTemplate(
            original_post_id=post.id,
            original_text="Original viral text",
            variation_1="Variation 1 text",
            variation_2="Variation 2 text",
            variation_3="Variation 3 text",
            avg_views=10000,
            category="viral"
        )
        db_session.add(template)
        db_session.commit()
        
        assert template.id is not None
        assert template.original_post_id == post.id
        assert template.original_text == "Original viral text"
        assert template.variation_1 == "Variation 1 text"
        assert template.avg_views == 10000
        assert template.category == "viral"
        assert template.is_used is False


class TestRepostCandidateModel:
    """Test RepostCandidate model functionality"""
    
    def test_create_repost_candidate(self, db_session):
        """Test creating a repost candidate"""
        post = Post(
            post_url="https://tiktok.com/test",
            account="test",
            created_date=datetime.now(),
            views=50000,
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        candidate = RepostCandidate(
            original_post_id=post.id,
            repost_type="same_account",
            score=85.5,
            reason="High engagement rate and viral potential",
            predicted_views=45000,
            predicted_engagement=3000
        )
        db_session.add(candidate)
        db_session.commit()
        
        assert candidate.id is not None
        assert candidate.original_post_id == post.id
        assert candidate.repost_type == "same_account"
        assert candidate.score == 85.5
        assert candidate.predicted_views == 45000
        assert candidate.is_used is False


class TestSystemConfigModel:
    """Test SystemConfig model functionality"""
    
    def test_create_system_config(self, db_session):
        """Test creating system configuration"""
        config = SystemConfig(
            key="scraping_interval",
            value="3600",
            description="Scraping interval in seconds"
        )
        db_session.add(config)
        db_session.commit()
        
        assert config.id is not None
        assert config.key == "scraping_interval"
        assert config.value == "3600"
        assert config.description == "Scraping interval in seconds"
    
    def test_system_config_unique_key(self, db_session):
        """Test system config key uniqueness"""
        config1 = SystemConfig(key="test_key", value="value1")
        config2 = SystemConfig(key="test_key", value="value2")  # Same key
        
        db_session.add(config1)
        db_session.commit()
        
        db_session.add(config2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()


class TestDataImportLogModel:
    """Test DataImportLog model functionality"""
    
    def test_create_data_import_log(self, db_session):
        """Test creating data import log"""
        log = DataImportLog(
            import_type="csv_import",
            source="MASTER_TIKTOK_DATABASE.csv",
            records_processed=1000,
            records_imported=950,
            records_skipped=30,
            records_failed=20,
            status="completed"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.id is not None
        assert log.import_type == "csv_import"
        assert log.source == "MASTER_TIKTOK_DATABASE.csv"
        assert log.records_processed == 1000
        assert log.records_imported == 950
        assert log.status == "completed"
        assert log.started_at is not None


class TestModelRelationships:
    """Test complex relationships between models"""
    
    def test_full_post_workflow(self, db_session):
        """Test complete post workflow with all related data"""
        # Create VA
        va = VA(name="TestVA", creator="TestCreator")
        db_session.add(va)
        db_session.commit()
        
        # Create post
        post = Post(
            post_url="https://tiktok.com/test",
            account="test_account",
            va_id=va.id,
            created_date=datetime.now(),
            views=10000,
            likes=500,
            comments=100,
            shares=50,
            engagement=650,
            engagement_rate=6.5,
            slides="https://image1.jpg|https://image2.jpg",
            source="test"
        )
        db_session.add(post)
        db_session.commit()
        
        # Create slides
        slide1 = Slide(
            post_id=post.id,
            slide_url="https://image1.jpg",
            slide_index=1,
            ocr_text="First slide text",
            image_hash="hash1"
        )
        slide2 = Slide(
            post_id=post.id,
            slide_url="https://image2.jpg",
            slide_index=2,
            ocr_text="Second slide text",
            image_hash="hash2"
        )
        db_session.add_all([slide1, slide2])
        db_session.commit()
        
        # Create metrics history
        metrics = MetricsHistory(
            post_id=post.id,
            va_id=va.id,
            views=12000,
            likes=600,
            comments=120,
            shares=60,
            engagement=780,
            engagement_rate=6.5,
            days_since_posted=1
        )
        db_session.add(metrics)
        db_session.commit()
        
        # Create content template
        template = ContentTemplate(
            original_post_id=post.id,
            original_text="Original text",
            variation_1="Variation 1",
            avg_views=10000,
            category="viral"
        )
        db_session.add(template)
        db_session.commit()
        
        # Create repost candidate
        candidate = RepostCandidate(
            original_post_id=post.id,
            repost_type="same_account",
            score=90.0,
            reason="High viral potential"
        )
        db_session.add(candidate)
        db_session.commit()
        
        # Test all relationships
        assert len(va.posts) == 1
        assert len(post.slides_data) == 2
        assert len(post.metrics_history) == 1
        assert post.va.name == "TestVA"
        assert slide1.post.account == "test_account"
        assert metrics.post.post_url == "https://tiktok.com/test"
        assert template.original_post_id == post.id
        assert candidate.original_post_id == post.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
