#!/usr/bin/env python3
"""
Slides Migration for TikTok Analytics Database
Created for Issue #6: Complete Data Migration Plan
"""

import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from .base_migrator import BaseMigrator
from ..models import Post, Slide


class SlidesMigrator(BaseMigrator):
    """
    Migrates slide URLs from posts and creates individual slide records
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, "slides_import")
        self.slide_cache = {}  # Cache for slide lookups
    
    def migrate_slides_from_posts(self, batch_size: int = 1000) -> Dict[str, int]:
        """
        Migrate slides from posts that have slide URLs
        """
        self.start_migration("posts.slides", "Parse slide URLs and create slide records")
        
        try:
            # Get all posts with slides
            posts_with_slides = self.db.query(Post).filter(
                Post.slides.isnot(None),
                Post.slides != ''
            ).all()
            
            self.log_progress(f"Found {len(posts_with_slides)} posts with slides")
            
            # Process posts in batches
            for i in range(0, len(posts_with_slides), batch_size):
                batch = posts_with_slides[i:i + batch_size]
                self.log_progress(f"Processing batch {i//batch_size + 1}: {len(batch)} posts")
                
                for post in batch:
                    try:
                        self._process_post_slides(post)
                    except Exception as e:
                        self.log_error(e, f"Error processing slides for post: {post.post_url}")
                        continue
                
                # Commit batch
                self.batch_commit(batch_size)
                self.log_progress(f"Progress: {self.stats['processed']} processed, {self.stats['imported']} slides created")
            
            self.complete_migration(success=True)
            self.log_progress(f"Slides migration completed: {self.stats}")
            
            return self.stats.copy()
            
        except Exception as e:
            self.complete_migration(success=False, error_message=str(e))
            raise
    
    def _process_post_slides(self, post: Post):
        """
        Process slides for a single post
        """
        if not post.slides:
            return
        
        # Parse slide URLs
        slide_urls = self._parse_slide_urls(post.slides)
        if not slide_urls:
            return
        
        # Check if slides already exist for this post
        existing_slides = self.db.query(Slide).filter(Slide.post_id == post.id).all()
        if existing_slides:
            self.log_progress(f"Slides already exist for post: {post.post_url}", "warning")
            self.stats['skipped'] += 1
            return
        
        # Create slide records
        for i, slide_url in enumerate(slide_urls, 1):
            slide = self._create_slide_record(post, slide_url, i)
            if slide:
                if self.safe_add_record(slide, "slide"):
                    self.stats['imported'] += 1
                else:
                    self.stats['failed'] += 1
        
        self.stats['processed'] += 1
    
    def _parse_slide_urls(self, slides_str: str) -> List[str]:
        """
        Parse pipe-separated slide URLs
        """
        if not slides_str:
            return []
        
        # Split by pipe and clean URLs
        urls = [url.strip() for url in slides_str.split('|') if url.strip()]
        
        # Filter out invalid URLs
        valid_urls = []
        for url in urls:
            if self._is_valid_slide_url(url):
                valid_urls.append(url)
            else:
                self.log_progress(f"Invalid slide URL: {url[:50]}...", "warning")
        
        return valid_urls
    
    def _is_valid_slide_url(self, url: str) -> bool:
        """
        Validate slide URL format
        """
        if not url or len(url) < 10:
            return False
        
        # Check for common image URL patterns
        valid_domains = [
            'tiktokcdn-us.com',
            'tiktokcdn.com',
            'p16-common-sign.tiktokcdn-us.com',
            'p19-sign.tiktokcdn-us.com'
        ]
        
        return any(domain in url for domain in valid_domains)
    
    def _create_slide_record(self, post: Post, slide_url: str, slide_index: int) -> Optional[Slide]:
        """
        Create a slide record
        """
        try:
            # Generate image hash for duplicate detection
            image_hash = hashlib.md5(slide_url.encode()).hexdigest()
            
            # Check for duplicates
            existing_slide = self.db.query(Slide).filter(
                Slide.image_hash == image_hash
            ).first()
            
            if existing_slide:
                self.log_progress(f"Duplicate slide found: {slide_url[:50]}...", "warning")
                return None
            
            slide = Slide(
                post_id=post.id,
                slide_url=slide_url,
                slide_index=slide_index,
                image_hash=image_hash
            )
            
            return slide
            
        except Exception as e:
            self.log_error(e, f"Error creating slide record: {slide_url}")
            return None
    
    def migrate_slides_from_csv(self, csv_path: str, batch_size: int = 1000) -> Dict[str, int]:
        """
        Migrate slides directly from CSV file
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        self.start_migration(str(csv_path), "Import slides from CSV file")
        
        try:
            import pandas as pd
            
            # Read CSV in chunks
            chunk_iter = pd.read_csv(
                csv_path,
                chunksize=batch_size,
                quotechar='"',
                escapechar='\\'
            )
            
            total_chunks = 0
            for chunk in chunk_iter:
                total_chunks += 1
                self.log_progress(f"Processing chunk {total_chunks} ({len(chunk)} records)")
                
                for _, row in chunk.iterrows():
                    try:
                        if pd.notna(row.get('slides')) and row['slides']:
                            self._process_csv_row_slides(row)
                    except Exception as e:
                        self.log_error(e, f"Error processing CSV row: {row.get('post_url', 'unknown')}")
                        continue
                
                # Commit batch
                if total_chunks % 10 == 0:
                    self.batch_commit(batch_size)
                    self.log_progress(f"Progress: {self.stats['processed']} processed, {self.stats['imported']} slides created")
            
            # Final commit
            self.batch_commit(batch_size)
            
            self.complete_migration(success=True)
            self.log_progress(f"CSV slides migration completed: {self.stats}")
            
            return self.stats.copy()
            
        except Exception as e:
            self.complete_migration(success=False, error_message=str(e))
            raise
    
    def _process_csv_row_slides(self, row):
        """
        Process slides from a CSV row
        """
        post_url = row['post_url']
        slides_str = row['slides']
        
        # Find the post in database
        post = self.db.query(Post).filter(Post.post_url == post_url).first()
        if not post:
            self.log_progress(f"Post not found in database: {post_url}", "warning")
            self.stats['skipped'] += 1
            return
        
        # Check if slides already exist
        existing_slides = self.db.query(Slide).filter(Slide.post_id == post.id).all()
        if existing_slides:
            self.stats['skipped'] += 1
            return
        
        # Parse and create slides
        slide_urls = self._parse_slide_urls(slides_str)
        for i, slide_url in enumerate(slide_urls, 1):
            slide = self._create_slide_record(post, slide_url, i)
            if slide:
                if self.safe_add_record(slide, "slide"):
                    self.stats['imported'] += 1
                else:
                    self.stats['failed'] += 1
        
        self.stats['processed'] += 1
    
    def get_slides_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about slides in the database
        """
        try:
            # Count posts with slides
            posts_with_slides = self.db.query(Post).filter(
                Post.slides.isnot(None),
                Post.slides != ''
            ).count()
            
            # Count total slides
            total_slides = self.db.query(Slide).count()
            
            # Count slides by post
            slides_by_post = self.db.query(
                Slide.post_id,
                self.db.func.count(Slide.id).label('slide_count')
            ).group_by(Slide.post_id).all()
            
            # Calculate statistics
            slide_counts = [count for _, count in slides_by_post]
            avg_slides_per_post = sum(slide_counts) / len(slide_counts) if slide_counts else 0
            
            stats = {
                'posts_with_slides': posts_with_slides,
                'total_slides': total_slides,
                'posts_with_slide_records': len(slides_by_post),
                'avg_slides_per_post': avg_slides_per_post,
                'max_slides_per_post': max(slide_counts) if slide_counts else 0,
                'min_slides_per_post': min(slide_counts) if slide_counts else 0
            }
            
            return stats
            
        except Exception as e:
            self.log_error(e, "Failed to get slides statistics")
            return {}
    
    def validate_slides_integrity(self) -> Dict[str, Any]:
        """
        Validate slides data integrity
        """
        issues = []
        
        try:
            # Check for orphaned slides
            orphaned_slides = self.db.query(Slide).filter(
                ~Slide.post_id.in_(self.db.query(Post.id))
            ).count()
            
            if orphaned_slides > 0:
                issues.append(f"Found {orphaned_slides} orphaned slides")
            
            # Check for duplicate slide URLs
            duplicate_urls = self.db.query(
                Slide.slide_url,
                self.db.func.count(Slide.id).label('count')
            ).group_by(Slide.slide_url).having(
                self.db.func.count(Slide.id) > 1
            ).all()
            
            if duplicate_urls:
                issues.append(f"Found {len(duplicate_urls)} duplicate slide URLs")
            
            # Check for missing slide indexes
            missing_indexes = self.db.query(Slide).filter(
                Slide.slide_index.is_(None)
            ).count()
            
            if missing_indexes > 0:
                issues.append(f"Found {missing_indexes} slides with missing indexes")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'orphaned_slides': orphaned_slides,
                'duplicate_urls': len(duplicate_urls),
                'missing_indexes': missing_indexes
            }
            
        except Exception as e:
            self.log_error(e, "Failed to validate slides integrity")
            return {'valid': False, 'issues': [str(e)]}


def migrate_slides_from_posts(db_session: Session, batch_size: int = 1000) -> Dict[str, int]:
    """
    Convenience function to migrate slides from posts
    """
    migrator = SlidesMigrator(db_session)
    return migrator.migrate_slides_from_posts(batch_size)


def migrate_slides_from_csv(csv_path: str, db_session: Session, batch_size: int = 1000) -> Dict[str, int]:
    """
    Convenience function to migrate slides from CSV
    """
    migrator = SlidesMigrator(db_session)
    return migrator.migrate_slides_from_csv(csv_path, batch_size)


if __name__ == "__main__":
    # Example usage
    from ..config import get_session_factory, create_database_engine
    
    # Initialize database
    engine = create_database_engine()
    SessionLocal = get_session_factory(engine)
    session = SessionLocal()
    
    try:
        # Migrate slides from posts
        results = migrate_slides_from_posts(session)
        print(f"Slides migration completed: {results}")
        
        # Get statistics
        migrator = SlidesMigrator(session)
        stats = migrator.get_slides_statistics()
        print(f"Slides statistics: {stats}")
        
        # Validate integrity
        validation = migrator.validate_slides_integrity()
        print(f"Slides validation: {validation}")
    finally:
        session.close()
