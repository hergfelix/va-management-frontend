#!/usr/bin/env python3
"""
Complete Migration Orchestrator for TikTok Analytics Database
Created for Issue #6: Complete Data Migration Plan
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .base_migrator import BaseMigrator
from .migrate_csv_data import CSVDataMigrator
from .migrate_ocr_data import OCRDataMigrator
from .migrate_slides import SlidesMigrator
from .validate_migration import MigrationValidator
from ..config import get_session_factory, create_database_engine


class MigrationOrchestrator:
    """
    Orchestrates the complete migration process
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.start_time = None
        self.results = {}
        self.logger = BaseMigrator(db_session, "orchestrator").logger
    
    def run_complete_migration(
        self,
        csv_path: str,
        ocr_dir: str,
        batch_size: int = 1000,
        skip_csv: bool = False,
        skip_ocr: bool = False,
        skip_slides: bool = False,
        validate_only: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete migration process
        """
        self.start_time = time.time()
        self.logger.info("🚀 Starting complete TikTok Analytics migration")
        
        try:
            if validate_only:
                self.logger.info("📊 Running validation only")
                return self._run_validation()
            
            # Phase 1: CSV Data Migration
            if not skip_csv:
                self.logger.info("📁 Phase 1: Migrating CSV data")
                self.results['csv_migration'] = self._migrate_csv_data(csv_path, batch_size)
            else:
                self.logger.info("⏭️ Skipping CSV migration")
            
            # Phase 2: OCR Data Migration
            if not skip_ocr:
                self.logger.info("🔍 Phase 2: Migrating OCR data")
                self.results['ocr_migration'] = self._migrate_ocr_data(ocr_dir)
            else:
                self.logger.info("⏭️ Skipping OCR migration")
            
            # Phase 3: Slides Migration
            if not skip_slides:
                self.logger.info("🖼️ Phase 3: Migrating slides")
                self.results['slides_migration'] = self._migrate_slides()
            else:
                self.logger.info("⏭️ Skipping slides migration")
            
            # Phase 4: Validation
            self.logger.info("✅ Phase 4: Validating migration")
            self.results['validation'] = self._run_validation()
            
            # Generate final summary
            self.results['summary'] = self._generate_final_summary()
            
            duration = time.time() - self.start_time
            self.logger.info(f"🎉 Migration completed in {duration:.2f} seconds")
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"❌ Migration failed: {str(e)}")
            self.results['error'] = str(e)
            return self.results
    
    def _migrate_csv_data(self, csv_path: str, batch_size: int) -> Dict[str, Any]:
        """
        Migrate CSV data
        """
        try:
            migrator = CSVDataMigrator(self.db)
            
            # Validate CSV structure
            if not migrator.validate_csv_structure(csv_path):
                raise ValueError("CSV structure validation failed")
            
            # Get statistics
            stats = migrator.get_csv_statistics(csv_path)
            self.logger.info(f"CSV Statistics: {stats}")
            
            # Perform migration
            results = migrator.migrate_csv_file(csv_path, batch_size)
            
            self.logger.info(f"✅ CSV migration completed: {results}")
            return {
                'status': 'success',
                'results': results,
                'statistics': stats
            }
            
        except Exception as e:
            self.logger.error(f"❌ CSV migration failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _migrate_ocr_data(self, ocr_dir: str) -> Dict[str, Any]:
        """
        Migrate OCR data
        """
        try:
            migrator = OCRDataMigrator(self.db)
            
            # Validate OCR structure
            if not migrator.validate_ocr_structure(ocr_dir):
                raise ValueError("OCR structure validation failed")
            
            # Get statistics
            stats = migrator.get_ocr_statistics(ocr_dir)
            self.logger.info(f"OCR Statistics: {stats}")
            
            # Perform migration
            results = migrator.migrate_ocr_directory(ocr_dir)
            
            self.logger.info(f"✅ OCR migration completed: {results}")
            return {
                'status': 'success',
                'results': results,
                'statistics': stats
            }
            
        except Exception as e:
            self.logger.error(f"❌ OCR migration failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _migrate_slides(self) -> Dict[str, Any]:
        """
        Migrate slides
        """
        try:
            migrator = SlidesMigrator(self.db)
            
            # Get current statistics
            stats = migrator.get_slides_statistics()
            self.logger.info(f"Current slides statistics: {stats}")
            
            # Perform migration
            results = migrator.migrate_slides_from_posts()
            
            # Get updated statistics
            updated_stats = migrator.get_slides_statistics()
            
            # Validate integrity
            validation = migrator.validate_slides_integrity()
            
            self.logger.info(f"✅ Slides migration completed: {results}")
            return {
                'status': 'success',
                'results': results,
                'statistics': updated_stats,
                'validation': validation
            }
            
        except Exception as e:
            self.logger.error(f"❌ Slides migration failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _run_validation(self) -> Dict[str, Any]:
        """
        Run validation
        """
        try:
            validator = MigrationValidator(self.db)
            
            # Run complete validation
            validation_results = validator.validate_complete_migration()
            
            # Get migration summary
            migration_summary = validator.get_migration_summary()
            
            self.logger.info(f"✅ Validation completed: {validation_results['overall_status']}")
            return {
                'status': 'success',
                'validation': validation_results,
                'migration_summary': migration_summary
            }
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _generate_final_summary(self) -> Dict[str, Any]:
        """
        Generate final migration summary
        """
        duration = time.time() - self.start_time if self.start_time else 0
        
        summary = {
            'total_duration': duration,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            'end_time': datetime.now().isoformat(),
            'phases_completed': 0,
            'phases_failed': 0,
            'overall_status': 'success'
        }
        
        # Count completed phases
        for phase, result in self.results.items():
            if phase == 'summary':
                continue
            
            if result.get('status') == 'success':
                summary['phases_completed'] += 1
            else:
                summary['phases_failed'] += 1
                summary['overall_status'] = 'failed'
        
        # Add specific results
        if 'csv_migration' in self.results:
            summary['csv_results'] = self.results['csv_migration'].get('results', {})
        
        if 'ocr_migration' in self.results:
            summary['ocr_results'] = self.results['ocr_migration'].get('results', {})
        
        if 'slides_migration' in self.results:
            summary['slides_results'] = self.results['slides_migration'].get('results', {})
        
        if 'validation' in self.results:
            summary['validation_status'] = self.results['validation'].get('validation', {}).get('overall_status', 'unknown')
        
        return summary
    
    def print_summary(self):
        """
        Print migration summary
        """
        if 'summary' not in self.results:
            print("❌ No summary available")
            return
        
        summary = self.results['summary']
        
        print("\n" + "="*60)
        print("🎯 TIKTOK ANALYTICS MIGRATION SUMMARY")
        print("="*60)
        
        print(f"⏱️  Duration: {summary['total_duration']:.2f} seconds")
        print(f"📊 Overall Status: {summary['overall_status'].upper()}")
        print(f"✅ Phases Completed: {summary['phases_completed']}")
        print(f"❌ Phases Failed: {summary['phases_failed']}")
        
        if 'csv_results' in summary:
            csv = summary['csv_results']
            print(f"\n📁 CSV Migration:")
            print(f"   • Processed: {csv.get('processed', 0):,}")
            print(f"   • Imported: {csv.get('imported', 0):,}")
            print(f"   • Skipped: {csv.get('skipped', 0):,}")
            print(f"   • Failed: {csv.get('failed', 0):,}")
        
        if 'ocr_results' in summary:
            ocr = summary['ocr_results']
            print(f"\n🔍 OCR Migration:")
            print(f"   • Processed: {ocr.get('processed', 0):,}")
            print(f"   • Imported: {ocr.get('imported', 0):,}")
            print(f"   • Skipped: {ocr.get('skipped', 0):,}")
            print(f"   • Failed: {ocr.get('failed', 0):,}")
        
        if 'slides_results' in summary:
            slides = summary['slides_results']
            print(f"\n🖼️  Slides Migration:")
            print(f"   • Processed: {slides.get('processed', 0):,}")
            print(f"   • Imported: {slides.get('imported', 0):,}")
            print(f"   • Skipped: {slides.get('skipped', 0):,}")
            print(f"   • Failed: {slides.get('failed', 0):,}")
        
        if 'validation_status' in summary:
            print(f"\n✅ Validation Status: {summary['validation_status'].upper()}")
        
        print("="*60)


def run_migration(
    csv_path: str,
    ocr_dir: str,
    batch_size: int = 1000,
    skip_csv: bool = False,
    skip_ocr: bool = False,
    skip_slides: bool = False,
    validate_only: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to run complete migration
    """
    # Initialize database
    engine = create_database_engine()
    SessionLocal = get_session_factory(engine)
    session = SessionLocal()
    
    try:
        orchestrator = MigrationOrchestrator(session)
        results = orchestrator.run_complete_migration(
            csv_path=csv_path,
            ocr_dir=ocr_dir,
            batch_size=batch_size,
            skip_csv=skip_csv,
            skip_ocr=skip_ocr,
            skip_slides=skip_slides,
            validate_only=validate_only
        )
        
        orchestrator.print_summary()
        return results
        
    finally:
        session.close()


if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="TikTok Analytics Migration")
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--ocr", required=True, help="Path to OCR directory")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for processing")
    parser.add_argument("--skip-csv", action="store_true", help="Skip CSV migration")
    parser.add_argument("--skip-ocr", action="store_true", help="Skip OCR migration")
    parser.add_argument("--skip-slides", action="store_true", help="Skip slides migration")
    parser.add_argument("--validate-only", action="store_true", help="Run validation only")
    
    args = parser.parse_args()
    
    results = run_migration(
        csv_path=args.csv,
        ocr_dir=args.ocr,
        batch_size=args.batch_size,
        skip_csv=args.skip_csv,
        skip_ocr=args.skip_ocr,
        skip_slides=args.skip_slides,
        validate_only=args.validate_only
    )
    
    if results.get('error'):
        sys.exit(1)
