#!/usr/bin/env python3
"""
OCR Data Migration for TikTok Analytics Database
Created for Issue #6: Complete Data Migration Plan
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from .base_migrator import BaseMigrator
from ..models import Post, Slide


class OCRDataMigrator(BaseMigrator):
    """
    Migrates OCR data from october_ocr_data directory
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, "ocr_import")
        self.post_cache = {}  # Cache for post lookups
    
    def migrate_ocr_directory(self, ocr_dir: str) -> Dict[str, int]:
        """
        Migrate OCR data from directory structure
        """
        ocr_path = Path(ocr_dir)
        if not ocr_path.exists():
            raise FileNotFoundError(f"OCR directory not found: {ocr_path}")
        
        self.start_migration(str(ocr_path), "Import OCR text data for slides")
        
        try:
            # Process all VA directories
            va_dirs = [d for d in ocr_path.glob("by_va/*") if d.is_dir()]
            self.log_progress(f"Found {len(va_dirs)} VA directories")
            
            for va_dir in va_dirs:
                va_name = va_dir.name
                self.log_progress(f"Processing VA: {va_name}")
                
                # Process OCR posts for this VA
                ocr_posts_file = va_dir / "ocr_posts.json"
                if ocr_posts_file.exists():
                    self._process_va_ocr_posts(ocr_posts_file, va_name)
                else:
                    self.log_progress(f"No ocr_posts.json found for {va_name}", "warning")
            
            # Final commit
            self.batch_commit(1000)
            
            self.complete_migration(success=True)
            self.log_progress(f"OCR migration completed: {self.stats}")
            
            return self.stats.copy()
            
        except Exception as e:
            self.complete_migration(success=False, error_message=str(e))
            raise
    
    def _process_va_ocr_posts(self, ocr_posts_file: Path, va_name: str):
        """
        Process OCR posts for a specific VA
        """
        try:
            with open(ocr_posts_file, 'r', encoding='utf-8') as f:
                ocr_posts = json.load(f)
            
            self.log_progress(f"Processing {len(ocr_posts)} OCR posts for {va_name}")
            
            for ocr_post in ocr_posts:
                try:
                    self._process_single_ocr_post(ocr_post)
                except Exception as e:
                    self.log_error(e, f"Error processing OCR post: {ocr_post.get('post_url', 'unknown')}")
                    continue
            
        except Exception as e:
            self.log_error(e, f"Error reading OCR posts file: {ocr_posts_file}")
    
    def _process_single_ocr_post(self, ocr_post: Dict[str, Any]):
        """
        Process a single OCR post and update slides
        """
        post_url = ocr_post.get('post_url')
        if not post_url:
            self.log_error(ValueError("Missing post_url in OCR data"))
            return
        
        # Find the post in database
        post = self._get_post_by_url(post_url)
        if not post:
            self.log_progress(f"Post not found in database: {post_url}", "warning")
            self.stats['skipped'] += 1
            return
        
        # Update slides with OCR data
        self._update_slides_with_ocr(post, ocr_post)
        
        self.stats['processed'] += 1
    
    def _get_post_by_url(self, post_url: str) -> Optional[Post]:
        """
        Get post by URL with caching
        """
        if post_url in self.post_cache:
            return self.post_cache[post_url]
        
        post = self.db.query(Post).filter(Post.post_url == post_url).first()
        if post:
            self.post_cache[post_url] = post
        
        return post
    
    def _update_slides_with_ocr(self, post: Post, ocr_post: Dict[str, Any]):
        """
        Update slides with OCR text data
        """
        # Get OCR text
        ocr_text = ocr_post.get('combined_text', '') or ocr_post.get('ocr_text', '')
        if not ocr_text:
            self.log_progress(f"No OCR text for post: {post.post_url}", "warning")
            return
        
        # Get or create text hash
        text_hash = ocr_post.get('text_hash')
        if not text_hash:
            text_hash = hashlib.md5(ocr_text.encode()).hexdigest()
        
        # Check if slides already exist for this post
        existing_slides = self.db.query(Slide).filter(Slide.post_id == post.id).all()
        
        if existing_slides:
            # Update existing slides with OCR text
            for slide in existing_slides:
                if not slide.ocr_text:  # Only update if no existing OCR text
                    slide.ocr_text = ocr_text
                    slide.image_hash = text_hash
                    slide.ocr_confidence = 0.95  # Default confidence
        else:
            # Create a single slide record with OCR text
            # This handles cases where slides weren't parsed yet
            slide = Slide(
                post_id=post.id,
                slide_url="",  # Will be updated when slides are parsed
                slide_index=1,
                ocr_text=ocr_text,
                image_hash=text_hash,
                ocr_confidence=0.95
            )
            
            if self.safe_add_record(slide, "slide"):
                self.stats['imported'] += 1
            else:
                self.stats['failed'] += 1
                return
        
        self.stats['imported'] += 1
    
    def migrate_single_ocr_file(self, ocr_file: str) -> Dict[str, int]:
        """
        Migrate OCR data from a single JSON file
        """
        ocr_path = Path(ocr_file)
        if not ocr_path.exists():
            raise FileNotFoundError(f"OCR file not found: {ocr_path}")
        
        self.start_migration(str(ocr_path), "Import OCR data from single file")
        
        try:
            with open(ocr_path, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)
            
            if isinstance(ocr_data, list):
                # Process list of OCR posts
                for ocr_post in ocr_data:
                    try:
                        self._process_single_ocr_post(ocr_post)
                    except Exception as e:
                        self.log_error(e, f"Error processing OCR post")
                        continue
            elif isinstance(ocr_data, dict):
                # Process single OCR post
                self._process_single_ocr_post(ocr_data)
            else:
                raise ValueError("Invalid OCR data format")
            
            # Final commit
            self.batch_commit(1000)
            
            self.complete_migration(success=True)
            self.log_progress(f"OCR file migration completed: {self.stats}")
            
            return self.stats.copy()
            
        except Exception as e:
            self.complete_migration(success=False, error_message=str(e))
            raise
    
    def get_ocr_statistics(self, ocr_dir: str) -> Dict[str, Any]:
        """
        Get statistics about OCR data
        """
        ocr_path = Path(ocr_dir)
        if not ocr_path.exists():
            return {}
        
        stats = {
            'total_vas': 0,
            'total_posts': 0,
            'posts_with_text': 0,
            'text_extraction_rate': 0.0,
            'va_breakdown': []
        }
        
        try:
            # Check overall summary
            summary_file = ocr_path / "overall_summary.json"
            if summary_file.exists():
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
                
                stats.update({
                    'total_vas': summary_data.get('total_vas', 0),
                    'total_posts': summary_data.get('total_posts', 0),
                    'posts_with_text': summary_data.get('total_posts_with_text', 0),
                    'text_extraction_rate': summary_data.get('text_extraction_rate', 0.0)
                })
            
            # Process VA directories
            va_dirs = [d for d in ocr_path.glob("by_va/*") if d.is_dir()]
            stats['total_vas'] = len(va_dirs)
            
            for va_dir in va_dirs:
                va_name = va_dir.name
                ocr_posts_file = va_dir / "ocr_posts.json"
                
                if ocr_posts_file.exists():
                    with open(ocr_posts_file, 'r', encoding='utf-8') as f:
                        ocr_posts = json.load(f)
                    
                    posts_with_text = sum(1 for post in ocr_posts if post.get('combined_text'))
                    
                    stats['va_breakdown'].append({
                        'va': va_name,
                        'total_posts': len(ocr_posts),
                        'posts_with_text': posts_with_text,
                        'text_rate': posts_with_text / len(ocr_posts) if ocr_posts else 0
                    })
            
        except Exception as e:
            self.log_error(e, "Failed to get OCR statistics")
        
        return stats
    
    def validate_ocr_structure(self, ocr_dir: str) -> bool:
        """
        Validate OCR directory structure
        """
        ocr_path = Path(ocr_dir)
        if not ocr_path.exists():
            self.log_error(FileNotFoundError(f"OCR directory not found: {ocr_path}"))
            return False
        
        # Check for required structure
        required_files = ['overall_summary.json']
        required_dirs = ['by_va']
        
        for file_name in required_files:
            if not (ocr_path / file_name).exists():
                self.log_error(FileNotFoundError(f"Required file missing: {file_name}"))
                return False
        
        for dir_name in required_dirs:
            if not (ocr_path / dir_name).is_dir():
                self.log_error(FileNotFoundError(f"Required directory missing: {dir_name}"))
                return False
        
        # Check VA directories
        va_dirs = list(ocr_path.glob("by_va/*"))
        if not va_dirs:
            self.log_error(ValueError("No VA directories found"))
            return False
        
        self.log_progress("OCR structure validation passed")
        return True


def migrate_ocr_data(ocr_dir: str, db_session: Session) -> Dict[str, int]:
    """
    Convenience function to migrate OCR data
    """
    migrator = OCRDataMigrator(db_session)
    
    # Validate OCR structure first
    if not migrator.validate_ocr_structure(ocr_dir):
        raise ValueError("OCR structure validation failed")
    
    # Get statistics
    stats = migrator.get_ocr_statistics(ocr_dir)
    migrator.log_progress(f"OCR Statistics: {stats}")
    
    # Perform migration
    return migrator.migrate_ocr_directory(ocr_dir)


if __name__ == "__main__":
    # Example usage
    from ..config import get_session_factory, create_database_engine
    
    # Initialize database
    engine = create_database_engine()
    SessionLocal = get_session_factory(engine)
    session = SessionLocal()
    
    try:
        # Migrate OCR data
        ocr_dir = "/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/october_ocr_data"
        results = migrate_ocr_data(ocr_dir, session)
        print(f"OCR migration completed: {results}")
    finally:
        session.close()
