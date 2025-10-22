#!/usr/bin/env python3
"""
Base Migrator Class for TikTok Analytics Database
Created for Issue #6: Complete Data Migration Plan
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import DataImportLog
from ..config import get_db


class BaseMigrator:
    """
    Base class for all data migration operations
    """
    
    def __init__(self, db_session: Session, migration_type: str):
        self.db = db_session
        self.migration_type = migration_type
        self.import_log = None
        self.stats = {
            'processed': 0,
            'imported': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }
        
        # Setup logging
        self.logger = logging.getLogger(f"migration.{migration_type}")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def start_migration(self, source: str, description: str = None) -> DataImportLog:
        """
        Start a new migration process
        """
        self.logger.info(f"Starting {self.migration_type} migration from {source}")
        
        self.import_log = DataImportLog(
            import_type=self.migration_type,
            source=source,
            status="running",
            started_at=datetime.utcnow()
        )
        
        if description:
            self.import_log.error_message = description  # Using error_message for description
        
        self.db.add(self.import_log)
        self.db.commit()
        
        return self.import_log
    
    def complete_migration(self, success: bool = True, error_message: str = None):
        """
        Complete the migration process
        """
        if self.import_log:
            self.import_log.status = "completed" if success else "failed"
            self.import_log.completed_at = datetime.utcnow()
            self.import_log.records_processed = self.stats['processed']
            self.import_log.records_imported = self.stats['imported']
            self.import_log.records_skipped = self.stats['skipped']
            self.import_log.records_failed = self.stats['failed']
            
            if error_message:
                self.import_log.error_message = error_message
            elif self.stats['errors']:
                self.import_log.error_message = f"Errors: {len(self.stats['errors'])}"
            
            self.db.commit()
        
        status = "completed" if success else "failed"
        self.logger.info(f"Migration {status}: {self.stats}")
    
    def log_error(self, error: Exception, context: str = None):
        """
        Log an error and add to stats
        """
        error_msg = str(error)
        if context:
            error_msg = f"{context}: {error_msg}"
        
        self.logger.error(error_msg)
        self.stats['errors'].append(error_msg)
        self.stats['failed'] += 1
    
    def log_progress(self, message: str, level: str = "info"):
        """
        Log progress message
        """
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
    
    def update_stats(self, processed: int = 0, imported: int = 0, skipped: int = 0, failed: int = 0):
        """
        Update migration statistics
        """
        self.stats['processed'] += processed
        self.stats['imported'] += imported
        self.stats['skipped'] += skipped
        self.stats['failed'] += failed
    
    def batch_commit(self, batch_size: int = 1000):
        """
        Commit changes in batches to avoid memory issues
        """
        try:
            self.db.commit()
            self.logger.debug(f"Committed batch of {batch_size} records")
        except Exception as e:
            self.db.rollback()
            self.log_error(e, "Batch commit failed")
            raise
    
    def safe_add_record(self, record, record_type: str = "record"):
        """
        Safely add a record to the database with error handling
        """
        try:
            self.db.add(record)
            self.stats['imported'] += 1
            return True
        except IntegrityError as e:
            self.log_error(e, f"Integrity error adding {record_type}")
            self.db.rollback()
            self.stats['skipped'] += 1
            return False
        except Exception as e:
            self.log_error(e, f"Error adding {record_type}")
            self.db.rollback()
            self.stats['failed'] += 1
            return False
    
    def get_migration_summary(self) -> Dict[str, Any]:
        """
        Get summary of migration statistics
        """
        return {
            'migration_type': self.migration_type,
            'stats': self.stats.copy(),
            'success_rate': (self.stats['imported'] / max(self.stats['processed'], 1)) * 100,
            'error_count': len(self.stats['errors']),
            'duration': None  # Will be calculated when migration completes
        }
    
    def validate_data(self, data: Any, required_fields: List[str]) -> bool:
        """
        Validate that data contains required fields
        """
        if isinstance(data, dict):
            missing_fields = [field for field in required_fields if field not in data or data[field] is None]
            if missing_fields:
                self.log_error(ValueError(f"Missing required fields: {missing_fields}"))
                return False
        return True
    
    def normalize_string(self, value: str) -> Optional[str]:
        """
        Normalize string values (trim, handle None)
        """
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip() if value.strip() else None
        return str(value).strip() if str(value).strip() else None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object
        """
        if not date_str:
            return None
        
        try:
            # Handle ISO format
            if 'T' in date_str or 'Z' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Handle YYYY-MM-DD format
            if len(date_str) == 10 and date_str.count('-') == 2:
                return datetime.strptime(date_str, '%Y-%m-%d')
            
            # Handle other common formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            self.log_error(ValueError(f"Unable to parse date: {date_str}"))
            return None
            
        except Exception as e:
            self.log_error(e, f"Date parsing error: {date_str}")
            return None
