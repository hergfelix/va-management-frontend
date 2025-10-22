#!/usr/bin/env python3
"""
Database package for TikTok Analytics Master Database
Created for Issue #1: Setup Master Database Schema
"""

from .models import (
    Base, VA, Post, MetricsHistory, Slide, ScrapingJob,
    ContentTemplate, RepostCandidate, SystemConfig, DataImportLog
)
from .config import (
    DatabaseConfig, get_database_url, create_database_engine,
    get_session_factory, init_database, drop_database, reset_database,
    get_table_counts, get_database_info, db_config, get_db
)

__all__ = [
    # Models
    'Base', 'VA', 'Post', 'MetricsHistory', 'Slide', 'ScrapingJob',
    'ContentTemplate', 'RepostCandidate', 'SystemConfig', 'DataImportLog',
    
    # Configuration
    'DatabaseConfig', 'get_database_url', 'create_database_engine',
    'get_session_factory', 'init_database', 'drop_database', 'reset_database',
    'get_table_counts', 'get_database_info', 'db_config', 'get_db'
]

# Version info
__version__ = '1.0.0'
__author__ = 'TikTok Analytics Team'
