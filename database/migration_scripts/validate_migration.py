#!/usr/bin/env python3
"""
Migration Validation for TikTok Analytics Database
Created for Issue #6: Complete Data Migration Plan
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from .base_migrator import BaseMigrator
from ..models import VA, Post, Slide, MetricsHistory, DataImportLog


class MigrationValidator(BaseMigrator):
    """
    Validates migration results and data integrity
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, "validation")
    
    def validate_complete_migration(self) -> Dict[str, Any]:
        """
        Perform complete migration validation
        """
        self.log_progress("Starting complete migration validation")
        
        validation_results = {
            'overall_status': 'passed',
            'checks': {},
            'summary': {},
            'issues': []
        }
        
        try:
            # Run all validation checks
            validation_results['checks']['data_counts'] = self._validate_data_counts()
            validation_results['checks']['data_integrity'] = self._validate_data_integrity()
            validation_results['checks']['relationships'] = self._validate_relationships()
            validation_results['checks']['data_quality'] = self._validate_data_quality()
            validation_results['checks']['performance'] = self._validate_performance()
            
            # Generate summary
            validation_results['summary'] = self._generate_validation_summary(validation_results['checks'])
            
            # Determine overall status
            failed_checks = [name for name, result in validation_results['checks'].items() 
                           if not result.get('passed', False)]
            
            if failed_checks:
                validation_results['overall_status'] = 'failed'
                validation_results['issues'] = failed_checks
            
            self.log_progress(f"Validation completed: {validation_results['overall_status']}")
            return validation_results
            
        except Exception as e:
            self.log_error(e, "Validation failed")
            validation_results['overall_status'] = 'error'
            validation_results['issues'] = [str(e)]
            return validation_results
    
    def _validate_data_counts(self) -> Dict[str, Any]:
        """
        Validate expected data counts
        """
        self.log_progress("Validating data counts")
        
        try:
            counts = {
                'vas': self.db.query(VA).count(),
                'posts': self.db.query(Post).count(),
                'slides': self.db.query(Slide).count(),
                'metrics_history': self.db.query(MetricsHistory).count(),
                'import_logs': self.db.query(DataImportLog).count()
            }
            
            # Expected counts (from CSV analysis)
            expected = {
                'vas': 49,  # Approximate number of unique VAs
                'posts': 45077,  # Total posts in CSV
                'slides': 92367,  # Total slide URLs in CSV
                'metrics_history': 0,  # No historical data initially
                'import_logs': 0  # Will be created during migration
            }
            
            # Check if counts are reasonable
            passed = True
            issues = []
            
            # VA count should be reasonable (not 0, not too high)
            if counts['vas'] == 0:
                passed = False
                issues.append("No VAs found")
            elif counts['vas'] > 100:
                passed = False
                issues.append(f"Too many VAs: {counts['vas']}")
            
            # Post count should match expected
            if counts['posts'] == 0:
                passed = False
                issues.append("No posts found")
            elif counts['posts'] < expected['posts'] * 0.9:  # Allow 10% variance
                passed = False
                issues.append(f"Too few posts: {counts['posts']} (expected ~{expected['posts']})")
            
            # Slides count should be reasonable
            if counts['slides'] > 0 and counts['slides'] < expected['slides'] * 0.5:
                passed = False
                issues.append(f"Too few slides: {counts['slides']} (expected ~{expected['slides']})")
            
            return {
                'passed': passed,
                'counts': counts,
                'expected': expected,
                'issues': issues
            }
            
        except Exception as e:
            self.log_error(e, "Data counts validation failed")
            return {'passed': False, 'error': str(e)}
    
    def _validate_data_integrity(self) -> Dict[str, Any]:
        """
        Validate data integrity constraints
        """
        self.log_progress("Validating data integrity")
        
        try:
            issues = []
            
            # Check for orphaned slides
            orphaned_slides = self.db.query(Slide).filter(
                ~Slide.post_id.in_(self.db.query(Post.id))
            ).count()
            
            if orphaned_slides > 0:
                issues.append(f"Found {orphaned_slides} orphaned slides")
            
            # Check for posts with invalid VA references
            invalid_va_posts = self.db.query(Post).filter(
                Post.va_id.isnot(None),
                ~Post.va_id.in_(self.db.query(VA.id))
            ).count()
            
            if invalid_va_posts > 0:
                issues.append(f"Found {invalid_va_posts} posts with invalid VA references")
            
            # Check for duplicate post URLs
            duplicate_posts = self.db.query(
                Post.post_url,
                func.count(Post.id).label('count')
            ).group_by(Post.post_url).having(
                func.count(Post.id) > 1
            ).count()
            
            if duplicate_posts > 0:
                issues.append(f"Found {duplicate_posts} duplicate post URLs")
            
            # Check for negative metrics
            negative_metrics = self.db.query(Post).filter(
                (Post.views < 0) |
                (Post.likes < 0) |
                (Post.comments < 0) |
                (Post.shares < 0) |
                (Post.engagement < 0)
            ).count()
            
            if negative_metrics > 0:
                issues.append(f"Found {negative_metrics} posts with negative metrics")
            
            return {
                'passed': len(issues) == 0,
                'issues': issues,
                'orphaned_slides': orphaned_slides,
                'invalid_va_posts': invalid_va_posts,
                'duplicate_posts': duplicate_posts,
                'negative_metrics': negative_metrics
            }
            
        except Exception as e:
            self.log_error(e, "Data integrity validation failed")
            return {'passed': False, 'error': str(e)}
    
    def _validate_relationships(self) -> Dict[str, Any]:
        """
        Validate database relationships
        """
        self.log_progress("Validating relationships")
        
        try:
            issues = []
            
            # Check VA-Post relationships
            posts_without_va = self.db.query(Post).filter(Post.va_id.is_(None)).count()
            total_posts = self.db.query(Post).count()
            
            if posts_without_va > total_posts * 0.1:  # More than 10% without VA
                issues.append(f"Too many posts without VA: {posts_without_va}/{total_posts}")
            
            # Check Post-Slide relationships
            posts_with_slides = self.db.query(Post).filter(
                Post.slides.isnot(None),
                Post.slides != ''
            ).count()
            
            posts_with_slide_records = self.db.query(Post).join(Slide).distinct().count()
            
            if posts_with_slides > 0 and posts_with_slide_records == 0:
                issues.append("Posts have slide URLs but no slide records")
            
            # Check slide indexing
            slides_without_index = self.db.query(Slide).filter(
                Slide.slide_index.is_(None)
            ).count()
            
            if slides_without_index > 0:
                issues.append(f"Found {slides_without_index} slides without index")
            
            return {
                'passed': len(issues) == 0,
                'issues': issues,
                'posts_without_va': posts_without_va,
                'posts_with_slides': posts_with_slides,
                'posts_with_slide_records': posts_with_slide_records,
                'slides_without_index': slides_without_index
            }
            
        except Exception as e:
            self.log_error(e, "Relationships validation failed")
            return {'passed': False, 'error': str(e)}
    
    def _validate_data_quality(self) -> Dict[str, Any]:
        """
        Validate data quality
        """
        self.log_progress("Validating data quality")
        
        try:
            issues = []
            
            # Check for missing critical data
            posts_without_url = self.db.query(Post).filter(
                (Post.post_url.is_(None)) | (Post.post_url == '')
            ).count()
            
            if posts_without_url > 0:
                issues.append(f"Found {posts_without_url} posts without URL")
            
            # Check for missing dates
            posts_without_date = self.db.query(Post).filter(
                Post.created_date.is_(None)
            ).count()
            
            if posts_without_date > 0:
                issues.append(f"Found {posts_without_date} posts without date")
            
            # Check for unrealistic metrics
            unrealistic_views = self.db.query(Post).filter(Post.views > 10000000).count()
            if unrealistic_views > 0:
                issues.append(f"Found {unrealistic_views} posts with unrealistic view counts")
            
            # Check for missing account names
            posts_without_account = self.db.query(Post).filter(
                (Post.account.is_(None)) | (Post.account == '')
            ).count()
            
            if posts_without_account > 0:
                issues.append(f"Found {posts_without_account} posts without account")
            
            # Check OCR data quality
            slides_with_ocr = self.db.query(Slide).filter(
                Slide.ocr_text.isnot(None),
                Slide.ocr_text != ''
            ).count()
            
            total_slides = self.db.query(Slide).count()
            ocr_coverage = (slides_with_ocr / total_slides * 100) if total_slides > 0 else 0
            
            if ocr_coverage < 1:  # Less than 1% OCR coverage
                issues.append(f"Low OCR coverage: {ocr_coverage:.1f}%")
            
            return {
                'passed': len(issues) == 0,
                'issues': issues,
                'posts_without_url': posts_without_url,
                'posts_without_date': posts_without_date,
                'unrealistic_views': unrealistic_views,
                'posts_without_account': posts_without_account,
                'ocr_coverage': ocr_coverage
            }
            
        except Exception as e:
            self.log_error(e, "Data quality validation failed")
            return {'passed': False, 'error': str(e)}
    
    def _validate_performance(self) -> Dict[str, Any]:
        """
        Validate database performance
        """
        self.log_progress("Validating performance")
        
        try:
            issues = []
            performance_metrics = {}
            
            # Test query performance
            import time
            
            # Test VA query
            start_time = time.time()
            va_count = self.db.query(VA).count()
            va_query_time = time.time() - start_time
            performance_metrics['va_query_time'] = va_query_time
            
            if va_query_time > 1.0:  # More than 1 second
                issues.append(f"VA query too slow: {va_query_time:.2f}s")
            
            # Test Post query
            start_time = time.time()
            post_count = self.db.query(Post).count()
            post_query_time = time.time() - start_time
            performance_metrics['post_query_time'] = post_query_time
            
            if post_query_time > 2.0:  # More than 2 seconds
                issues.append(f"Post query too slow: {post_query_time:.2f}s")
            
            # Test complex query (posts with slides)
            start_time = time.time()
            posts_with_slides = self.db.query(Post).join(Slide).distinct().count()
            complex_query_time = time.time() - start_time
            performance_metrics['complex_query_time'] = complex_query_time
            
            if complex_query_time > 5.0:  # More than 5 seconds
                issues.append(f"Complex query too slow: {complex_query_time:.2f}s")
            
            return {
                'passed': len(issues) == 0,
                'issues': issues,
                'metrics': performance_metrics
            }
            
        except Exception as e:
            self.log_error(e, "Performance validation failed")
            return {'passed': False, 'error': str(e)}
    
    def _generate_validation_summary(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate validation summary
        """
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks.values() if check.get('passed', False))
        
        summary = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
        }
        
        # Add specific metrics
        if 'data_counts' in checks and checks['data_counts'].get('passed'):
            summary['data_counts'] = checks['data_counts']['counts']
        
        if 'data_quality' in checks and checks['data_quality'].get('passed'):
            summary['ocr_coverage'] = checks['data_quality'].get('ocr_coverage', 0)
        
        if 'performance' in checks and checks['performance'].get('passed'):
            summary['performance'] = checks['performance']['metrics']
        
        return summary
    
    def get_migration_summary(self) -> Dict[str, Any]:
        """
        Get summary of all migrations
        """
        try:
            import_logs = self.db.query(DataImportLog).order_by(DataImportLog.started_at.desc()).all()
            
            summary = {
                'total_migrations': len(import_logs),
                'successful_migrations': len([log for log in import_logs if log.status == 'completed']),
                'failed_migrations': len([log for log in import_logs if log.status == 'failed']),
                'migrations': []
            }
            
            for log in import_logs:
                migration_info = {
                    'type': log.import_type,
                    'source': log.source,
                    'status': log.status,
                    'started_at': log.started_at.isoformat() if log.started_at else None,
                    'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                    'records_processed': log.records_processed,
                    'records_imported': log.records_imported,
                    'records_skipped': log.records_skipped,
                    'records_failed': log.records_failed
                }
                summary['migrations'].append(migration_info)
            
            return summary
            
        except Exception as e:
            self.log_error(e, "Failed to get migration summary")
            return {}


def validate_migration(db_session: Session) -> Dict[str, Any]:
    """
    Convenience function to validate migration
    """
    validator = MigrationValidator(db_session)
    return validator.validate_complete_migration()


if __name__ == "__main__":
    # Example usage
    from ..config import get_session_factory, create_database_engine
    
    # Initialize database
    engine = create_database_engine()
    SessionLocal = get_session_factory(engine)
    session = SessionLocal()
    
    try:
        # Validate migration
        results = validate_migration(session)
        print(f"Validation results: {results}")
        
        # Get migration summary
        validator = MigrationValidator(session)
        summary = validator.get_migration_summary()
        print(f"Migration summary: {summary}")
    finally:
        session.close()
