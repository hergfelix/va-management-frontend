#!/usr/bin/env python3
"""
Data Import Utilities for TikTok Analytics Master Database
Created for Issue #1: Setup Master Database Schema
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import (
    VA, Post, MetricsHistory, Slide, ScrapingJob,
    ContentTemplate, RepostCandidate, SystemConfig, DataImportLog
)
from .config import get_db


class DataImporter:
    """
    Main class for importing data into the TikTok Analytics database
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.import_log = None
    
    def start_import(self, import_type: str, source: str) -> DataImportLog:
        """
        Start a new data import process
        """
        self.import_log = DataImportLog(
            import_type=import_type,
            source=source,
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(self.import_log)
        self.db.commit()
        return self.import_log
    
    def complete_import(self, success: bool = True, error_message: str = None):
        """
        Complete the data import process
        """
        if self.import_log:
            self.import_log.status = "completed" if success else "failed"
            self.import_log.completed_at = datetime.utcnow()
            if error_message:
                self.import_log.error_message = error_message
            self.db.commit()
    
    def import_csv_data(self, csv_path: str, batch_size: int = 1000) -> Dict[str, int]:
        """
        Import data from CSV file (MASTER_TIKTOK_DATABASE.csv)
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Start import log
        self.start_import("csv_import", str(csv_path))
        
        try:
            # Read CSV in chunks
            chunk_iter = pd.read_csv(
                csv_path,
                chunksize=batch_size,
                quotechar='"',
                escapechar='\\'
            )
            
            total_processed = 0
            total_imported = 0
            total_skipped = 0
            total_failed = 0
            
            for chunk in chunk_iter:
                processed, imported, skipped, failed = self._process_csv_chunk(chunk)
                total_processed += processed
                total_imported += imported
                total_skipped += skipped
                total_failed += failed
                
                # Update import log
                self.import_log.records_processed = total_processed
                self.import_log.records_imported = total_imported
                self.import_log.records_skipped = total_skipped
                self.import_log.records_failed = total_failed
                self.db.commit()
            
            self.complete_import(success=True)
            
            return {
                "processed": total_processed,
                "imported": total_imported,
                "skipped": total_skipped,
                "failed": total_failed
            }
            
        except Exception as e:
            self.complete_import(success=False, error_message=str(e))
            raise
    
    def _process_csv_chunk(self, chunk: pd.DataFrame) -> tuple:
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
                self.db.add(post)
                self.db.flush()  # Get the ID
                
                # Create slides if they exist
                if pd.notna(row.get('slides')) and row['slides']:
                    self._create_slides_from_post(post, row['slides'])
                
                imported += 1
                
            except Exception as e:
                print(f"Error processing row: {e}")
                failed += 1
                continue
        
        # Commit the chunk
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error committing chunk: {e}")
            failed += processed - imported - skipped
            imported = 0
        
        return processed, imported, skipped, failed
    
    def _get_or_create_va(self, va_name: str) -> Optional[VA]:
        """
        Get existing VA or create new one
        """
        if pd.isna(va_name) or not va_name:
            return None
        
        va = self.db.query(VA).filter(VA.name == va_name).first()
        if not va:
            va = VA(name=va_name)
            self.db.add(va)
            self.db.flush()
        
        return va
    
    def _create_post_from_row(self, row: pd.Series, va: Optional[VA]) -> Post:
        """
        Create Post object from CSV row
        """
        # Parse created_date
        created_date = pd.to_datetime(row['created_date'])
        
        # Parse slides (pipe-separated URLs)
        slides = row.get('slides') if pd.notna(row.get('slides')) else None
        
        post = Post(
            post_url=row['post_url'],
            account=row['account'],
            va_id=va.id if va else None,
            created_date=created_date,
            created_time=row.get('created_time'),
            views=int(row['views']) if pd.notna(row['views']) else 0,
            likes=int(row['likes']) if pd.notna(row['likes']) else 0,
            comments=int(row['comments']) if pd.notna(row['comments']) else 0,
            shares=int(row['shares']) if pd.notna(row['shares']) else 0,
            engagement=int(row['engagement']) if pd.notna(row['engagement']) else 0,
            engagement_rate=float(row['engagement_rate']) if pd.notna(row['engagement_rate']) else None,
            hashtags=row.get('hashtags') if pd.notna(row.get('hashtags')) else None,
            sound=row.get('sound') if pd.notna(row.get('sound')) else None,
            slides=slides,
            source=row['source']
        )
        
        return post
    
    def _create_slides_from_post(self, post: Post, slides_str: str):
        """
        Create Slide objects from pipe-separated URLs
        """
        if not slides_str:
            return
        
        slide_urls = [url.strip() for url in slides_str.split('|') if url.strip()]
        
        for i, url in enumerate(slide_urls, 1):
            slide = Slide(
                post_id=post.id,
                slide_url=url,
                slide_index=i
            )
            self.db.add(slide)
    
    def import_va_data(self, va_data: List[Dict[str, Any]]):
        """
        Import VA data from list of dictionaries
        """
        self.start_import("va_import", "manual_va_data")
        
        try:
            imported = 0
            for va_info in va_data:
                va = VA(
                    name=va_info['name'],
                    creator=va_info.get('creator'),
                    set_id=va_info.get('set_id'),
                    set_code=va_info.get('set_code'),
                    is_active=va_info.get('is_active', True)
                )
                self.db.add(va)
                imported += 1
            
            self.db.commit()
            self.complete_import(success=True)
            
            return {"imported": imported}
            
        except Exception as e:
            self.db.rollback()
            self.complete_import(success=False, error_message=str(e))
            raise
    
    def import_metrics_history(self, metrics_data: List[Dict[str, Any]]):
        """
        Import metrics history data
        """
        self.start_import("metrics_import", "manual_metrics_data")
        
        try:
            imported = 0
            for metrics_info in metrics_data:
                metrics = MetricsHistory(
                    post_id=metrics_info['post_id'],
                    va_id=metrics_info.get('va_id'),
                    views=metrics_info['views'],
                    likes=metrics_info['likes'],
                    comments=metrics_info['comments'],
                    shares=metrics_info['shares'],
                    engagement=metrics_info['engagement'],
                    engagement_rate=metrics_info.get('engagement_rate'),
                    days_since_posted=metrics_info.get('days_since_posted')
                )
                self.db.add(metrics)
                imported += 1
            
            self.db.commit()
            self.complete_import(success=True)
            
            return {"imported": imported}
            
        except Exception as e:
            self.db.rollback()
            self.complete_import(success=False, error_message=str(e))
            raise
    
    def import_content_templates(self, templates_data: List[Dict[str, Any]]):
        """
        Import content templates data
        """
        self.start_import("templates_import", "manual_templates_data")
        
        try:
            imported = 0
            for template_info in templates_data:
                template = ContentTemplate(
                    original_post_id=template_info['original_post_id'],
                    original_text=template_info['original_text'],
                    variation_1=template_info.get('variation_1'),
                    variation_2=template_info.get('variation_2'),
                    variation_3=template_info.get('variation_3'),
                    avg_views=template_info.get('avg_views'),
                    category=template_info.get('category')
                )
                self.db.add(template)
                imported += 1
            
            self.db.commit()
            self.complete_import(success=True)
            
            return {"imported": imported}
            
        except Exception as e:
            self.db.rollback()
            self.complete_import(success=False, error_message=str(e))
            raise
    
    def import_repost_candidates(self, candidates_data: List[Dict[str, Any]]):
        """
        Import repost candidates data
        """
        self.start_import("candidates_import", "manual_candidates_data")
        
        try:
            imported = 0
            for candidate_info in candidates_data:
                candidate = RepostCandidate(
                    original_post_id=candidate_info['original_post_id'],
                    repost_type=candidate_info['repost_type'],
                    score=candidate_info['score'],
                    reason=candidate_info.get('reason'),
                    predicted_views=candidate_info.get('predicted_views'),
                    predicted_engagement=candidate_info.get('predicted_engagement')
                )
                self.db.add(candidate)
                imported += 1
            
            self.db.commit()
            self.complete_import(success=True)
            
            return {"imported": imported}
            
        except Exception as e:
            self.db.rollback()
            self.complete_import(success=False, error_message=str(e))
            raise


class DataExporter:
    """
    Class for exporting data from the database
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def export_posts_to_csv(self, output_path: str, filters: Dict[str, Any] = None):
        """
        Export posts to CSV file
        """
        query = self.db.query(Post)
        
        if filters:
            if 'va_name' in filters:
                query = query.join(VA).filter(VA.name == filters['va_name'])
            if 'date_from' in filters:
                query = query.filter(Post.created_date >= filters['date_from'])
            if 'date_to' in filters:
                query = query.filter(Post.created_date <= filters['date_to'])
            if 'min_views' in filters:
                query = query.filter(Post.views >= filters['min_views'])
        
        posts = query.all()
        
        # Convert to DataFrame
        data = []
        for post in posts:
            data.append({
                'id': post.id,
                'post_url': post.post_url,
                'account': post.account,
                'va_name': post.va.name if post.va else None,
                'created_date': post.created_date,
                'views': post.views,
                'likes': post.likes,
                'comments': post.comments,
                'shares': post.shares,
                'engagement': post.engagement,
                'engagement_rate': post.engagement_rate,
                'hashtags': post.hashtags,
                'sound': post.sound,
                'slides': post.slides,
                'source': post.source,
                'scraping_status': post.scraping_status
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        
        return len(data)
    
    def export_va_performance(self, output_path: str):
        """
        Export VA performance data
        """
        # Get VA performance data
        vas = self.db.query(VA).all()
        
        data = []
        for va in vas:
            posts = self.db.query(Post).filter(Post.va_id == va.id).all()
            
            if posts:
                total_views = sum(post.views for post in posts)
                total_engagement = sum(post.engagement for post in posts)
                avg_views = total_views / len(posts)
                avg_engagement_rate = sum(
                    post.engagement_rate for post in posts 
                    if post.engagement_rate
                ) / len([p for p in posts if p.engagement_rate])
                
                data.append({
                    'va_name': va.name,
                    'creator': va.creator,
                    'total_posts': len(posts),
                    'total_views': total_views,
                    'total_engagement': total_engagement,
                    'avg_views': avg_views,
                    'avg_engagement_rate': avg_engagement_rate,
                    'is_active': va.is_active
                })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        
        return len(data)


def import_master_database(csv_path: str, db_session: Session) -> Dict[str, int]:
    """
    Convenience function to import the master database CSV
    """
    importer = DataImporter(db_session)
    return importer.import_csv_data(csv_path)


def export_va_report(output_path: str, db_session: Session) -> int:
    """
    Convenience function to export VA performance report
    """
    exporter = DataExporter(db_session)
    return exporter.export_va_performance(output_path)
