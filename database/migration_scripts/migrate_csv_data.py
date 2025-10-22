#!/usr/bin/env python3
"""
CSV Data Migration for TikTok Analytics Database
Created for Issue #6: Complete Data Migration Plan
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from .base_migrator import BaseMigrator
from ..models import VA, Post


class CSVDataMigrator(BaseMigrator):
    """
    Migrates data from MASTER_TIKTOK_DATABASE.csv
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, "csv_import")
        self.va_cache = {}  # Cache for VA lookups
    
    def migrate_csv_file(self, csv_path: str, batch_size: int = 1000) -> Dict[str, int]:
        """
        Migrate data from CSV file
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        self.start_migration(str(csv_path), "Import 45k+ TikTok posts from master CSV")
        
        try:
            # Read CSV in chunks
            self.log_progress(f"Reading CSV file: {csv_path}")
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
                
                processed, imported, skipped, failed = self._process_chunk(chunk)
                self.update_stats(processed, imported, skipped, failed)
                
                # Commit batch
                if total_chunks % 10 == 0:  # Commit every 10 chunks
                    self.batch_commit(batch_size)
                    self.log_progress(f"Progress: {self.stats['processed']} processed, {self.stats['imported']} imported")
            
            # Final commit
            self.batch_commit(batch_size)
            
            self.complete_migration(success=True)
            self.log_progress(f"CSV migration completed: {self.stats}")
            
            return self.stats.copy()
            
        except Exception as e:
            self.complete_migration(success=False, error_message=str(e))
            raise
    
    def _process_chunk(self, chunk: pd.DataFrame) -> tuple:
        """
        Process a chunk of CSV data
        """
        processed = len(chunk)
        imported = 0
        skipped = 0
        failed = 0
        
        for _, row in chunk.iterrows():
            try:
                # Check if post already exists
                existing_post = self.db.query(Post).filter(
                    Post.post_url == row['post_url']
                ).first()
                
                if existing_post:
                    skipped += 1
                    continue
                
                # Create or get VA
                va = self._get_or_create_va(row.get('va'))
                
                # Create post
                post = self._create_post_from_row(row, va)
                
                if self.safe_add_record(post, "post"):
                    imported += 1
                else:
                    failed += 1
                
            except Exception as e:
                self.log_error(e, f"Error processing row: {row.get('post_url', 'unknown')}")
                failed += 1
                continue
        
        return processed, imported, skipped, failed
    
    def _get_or_create_va(self, va_name: str) -> Optional[VA]:
        """
        Get existing VA or create new one
        """
        if not va_name or pd.isna(va_name):
            return None
        
        va_name = self.normalize_string(va_name)
        if not va_name:
            return None
        
        # Check cache first
        if va_name in self.va_cache:
            return self.va_cache[va_name]
        
        # Check database
        va = self.db.query(VA).filter(VA.name == va_name).first()
        
        if not va:
            va = VA(name=va_name)
            self.db.add(va)
            self.db.flush()  # Get the ID
        
        # Cache for future use
        self.va_cache[va_name] = va
        return va
    
    def _create_post_from_row(self, row: pd.Series, va: Optional[VA]) -> Post:
        """
        Create Post object from CSV row
        """
        # Parse created_date
        created_date = self.parse_date(row['created_date'])
        if not created_date:
            raise ValueError(f"Invalid date: {row['created_date']}")
        
        # Parse slides (pipe-separated URLs)
        slides = self.normalize_string(row.get('slides'))
        
        # Create post
        post = Post(
            post_url=row['post_url'],
            account=self.normalize_string(row['account']),
            va_id=va.id if va else None,
            created_date=created_date,
            created_time=self.normalize_string(row.get('created_time')),
            views=int(row['views']) if pd.notna(row['views']) else 0,
            likes=int(row['likes']) if pd.notna(row['likes']) else 0,
            comments=int(row['comments']) if pd.notna(row['comments']) else 0,
            shares=int(row['shares']) if pd.notna(row['shares']) else 0,
            engagement=int(row['engagement']) if pd.notna(row['engagement']) else 0,
            engagement_rate=float(row['engagement_rate']) if pd.notna(row['engagement_rate']) else None,
            hashtags=self.normalize_string(row.get('hashtags')),
            sound=self.normalize_string(row.get('sound')),
            slides=slides,
            source=self.normalize_string(row['source'])
        )
        
        return post
    
    def validate_csv_structure(self, csv_path: str) -> bool:
        """
        Validate CSV file structure before migration
        """
        try:
            # Read first few rows to check structure
            df = pd.read_csv(csv_path, nrows=5, quotechar='"', escapechar='\\')
            
            required_columns = [
                'created_date', 'created_time', 'account', 'va', 'post_url',
                'views', 'likes', 'comments', 'shares', 'engagement',
                'engagement_rate', 'hashtags', 'sound', 'slides', 'source'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.log_error(ValueError(f"Missing required columns: {missing_columns}"))
                return False
            
            # Check for duplicate URLs in sample
            if df['post_url'].duplicated().any():
                self.log_progress("Warning: Duplicate URLs found in sample data", "warning")
            
            self.log_progress("CSV structure validation passed")
            return True
            
        except Exception as e:
            self.log_error(e, "CSV structure validation failed")
            return False
    
    def get_csv_statistics(self, csv_path: str) -> Dict[str, Any]:
        """
        Get statistics about the CSV file
        """
        try:
            # Read entire file for statistics
            df = pd.read_csv(csv_path, quotechar='"', escapechar='\\')
            
            stats = {
                'total_rows': len(df),
                'unique_posts': df['post_url'].nunique(),
                'duplicate_posts': len(df) - df['post_url'].nunique(),
                'unique_accounts': df['account'].nunique(),
                'unique_vas': df['va'].nunique(),
                'date_range': {
                    'start': df['created_date'].min(),
                    'end': df['created_date'].max()
                },
                'posts_with_slides': df['slides'].notna().sum(),
                'total_views': df['views'].sum(),
                'sources': df['source'].value_counts().to_dict()
            }
            
            return stats
            
        except Exception as e:
            self.log_error(e, "Failed to get CSV statistics")
            return {}


def migrate_master_csv(csv_path: str, db_session: Session, batch_size: int = 1000) -> Dict[str, int]:
    """
    Convenience function to migrate the master CSV file
    """
    migrator = CSVDataMigrator(db_session)
    
    # Validate CSV structure first
    if not migrator.validate_csv_structure(csv_path):
        raise ValueError("CSV structure validation failed")
    
    # Get statistics
    stats = migrator.get_csv_statistics(csv_path)
    migrator.log_progress(f"CSV Statistics: {stats}")
    
    # Perform migration
    return migrator.migrate_csv_file(csv_path, batch_size)


if __name__ == "__main__":
    # Example usage
    from ..config import get_session_factory, create_database_engine
    
    # Initialize database
    engine = create_database_engine()
    SessionLocal = get_session_factory(engine)
    session = SessionLocal()
    
    try:
        # Migrate CSV
        csv_path = "/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv"
        results = migrate_master_csv(csv_path, session)
        print(f"Migration completed: {results}")
    finally:
        session.close()
