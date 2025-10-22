#!/usr/bin/env python3
"""
Database Configuration for TikTok Analytics Master Database
Created for Issue #1: Setup Master Database Schema
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pathlib import Path

# Database configuration
DATABASE_CONFIG = {
    # SQLite configuration (for development and testing)
    'sqlite': {
        'url': 'sqlite:///tiktok_analytics.db',
        'echo': False,
        'poolclass': StaticPool,
        'connect_args': {'check_same_thread': False}
    },
    
    # PostgreSQL configuration (for production)
    'postgresql': {
        'url': os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/tiktok_analytics'),
        'echo': False,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True
    },
    
    # Supabase configuration (recommended for production)
    'supabase': {
        'url': os.getenv('SUPABASE_DATABASE_URL', 'postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres'),
        'echo': False,
        'pool_size': 5,
        'max_overflow': 10,
        'pool_pre_ping': True
    }
}

# Default database type
DEFAULT_DB_TYPE = os.getenv('DB_TYPE', 'sqlite')

def get_database_url(db_type=None):
    """
    Get database URL for the specified type
    """
    if db_type is None:
        db_type = DEFAULT_DB_TYPE
    
    if db_type not in DATABASE_CONFIG:
        raise ValueError(f"Unknown database type: {db_type}")
    
    config = DATABASE_CONFIG[db_type]
    return config['url']

def create_database_engine(db_type=None, echo=None):
    """
    Create SQLAlchemy engine for the specified database type
    """
    if db_type is None:
        db_type = DEFAULT_DB_TYPE
    
    if db_type not in DATABASE_CONFIG:
        raise ValueError(f"Unknown database type: {db_type}")
    
    config = DATABASE_CONFIG[db_type].copy()
    
    # Override echo setting if provided
    if echo is not None:
        config['echo'] = echo
    
    # Remove 'url' from config and use it separately
    url = config.pop('url')
    
    return create_engine(url, **config)

def get_session_factory(engine):
    """
    Create session factory for the given engine
    """
    return sessionmaker(bind=engine)

def get_database_path():
    """
    Get the path to the SQLite database file
    """
    project_root = Path(__file__).parent.parent
    return project_root / 'tiktok_analytics.db'

def setup_database_directory():
    """
    Ensure database directory exists
    """
    db_path = get_database_path()
    db_path.parent.mkdir(exist_ok=True)
    return db_path

# Environment-specific configurations
class DatabaseConfig:
    """
    Database configuration class
    """
    
    def __init__(self, db_type=None):
        self.db_type = db_type or DEFAULT_DB_TYPE
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self, echo=None):
        """
        Initialize database connection
        """
        self.engine = create_database_engine(self.db_type, echo)
        self.SessionLocal = get_session_factory(self.engine)
        return self.engine
    
    def get_session(self):
        """
        Get database session
        """
        if self.SessionLocal is None:
            self.initialize()
        return self.SessionLocal()
    
    def close(self):
        """
        Close database connection
        """
        if self.engine:
            self.engine.dispose()

# Global database configuration instance
db_config = DatabaseConfig()

def get_db():
    """
    Dependency to get database session
    """
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

# Database initialization functions
def init_database(db_type=None, echo=None):
    """
    Initialize database with all tables
    """
    from .models import Base
    
    engine = create_database_engine(db_type, echo)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    return engine

def drop_database(db_type=None):
    """
    Drop all database tables (use with caution!)
    """
    from .models import Base
    
    engine = create_database_engine(db_type)
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    return engine

def reset_database(db_type=None, echo=None):
    """
    Reset database by dropping and recreating all tables
    """
    print("⚠️  Dropping all tables...")
    drop_database(db_type)
    
    print("✅ Creating all tables...")
    engine = init_database(db_type, echo)
    
    print("🎉 Database reset complete!")
    return engine

# Utility functions for database operations
def get_table_counts(engine):
    """
    Get row counts for all tables
    """
    from .models import Base
    from sqlalchemy import text
    
    counts = {}
    for table in Base.metadata.tables.values():
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table.name}"))
            counts[table.name] = result.scalar()
    
    return counts

def get_database_info(engine):
    """
    Get database information and statistics
    """
    from .models import Base
    
    info = {
        'tables': list(Base.metadata.tables.keys()),
        'table_counts': get_table_counts(engine),
        'engine_url': str(engine.url).replace(engine.url.password or '', '***') if engine.url.password else str(engine.url)
    }
    
    return info
