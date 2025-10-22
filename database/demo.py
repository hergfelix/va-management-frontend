#!/usr/bin/env python3
"""
Database Demo Script for TikTok Analytics Master Database
Created for Issue #1: Setup Master Database Schema

This script demonstrates the complete database functionality:
- Database initialization
- Data import from CSV
- Basic queries and operations
- Data export
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.config import init_database, get_database_info, get_table_counts
from database.import_utils import DataImporter, DataExporter, import_master_database
from database.models import VA, Post, MetricsHistory, Slide


def main():
    """
    Main demo function
    """
    print("""
╔════════════════════════════════════════════════════════════════╗
║     🗄️  TIKTOK ANALYTICS DATABASE DEMO                       ║
║     Issue #1: Setup Master Database Schema                    ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize database
    print("🔧 Initializing database...")
    engine = init_database(echo=False)
    print("✅ Database initialized successfully!")
    
    # Get database info
    print("\n📊 Database Information:")
    info = get_database_info(engine)
    print(f"   Tables: {', '.join(info['tables'])}")
    print(f"   Database URL: {info['engine_url']}")
    
    # Get table counts
    print("\n📈 Current Table Counts:")
    counts = get_table_counts(engine)
    for table, count in counts.items():
        print(f"   {table}: {count} records")
    
    # Import sample data if CSV exists
    csv_path = Path(__file__).parent.parent / "MASTER_TIKTOK_DATABASE.csv"
    if csv_path.exists():
        print(f"\n📥 Importing data from {csv_path.name}...")
        
        # Create session
        from database.config import get_session_factory
        SessionLocal = get_session_factory(engine)
        session = SessionLocal()
        
        try:
            # Import first 100 rows as demo
            print("   (Importing first 100 rows as demo...)")
            
            # Read first 100 rows
            import pandas as pd
            df = pd.read_csv(csv_path, nrows=100, quotechar='"', escapechar='\\')
            
            # Create importer
            importer = DataImporter(session)
            
            # Import data
            results = importer.import_csv_data(str(csv_path))
            
            print(f"✅ Import completed!")
            print(f"   Processed: {results['processed']} records")
            print(f"   Imported: {results['imported']} records")
            print(f"   Skipped: {results['skipped']} records")
            print(f"   Failed: {results['failed']} records")
            
            # Show updated counts
            print("\n📈 Updated Table Counts:")
            counts = get_table_counts(engine)
            for table, count in counts.items():
                print(f"   {table}: {count} records")
            
            # Demo queries
            print("\n🔍 Demo Queries:")
            
            # Top VAs by post count
            from sqlalchemy import func
            top_vas = session.query(
                VA.name,
                func.count(Post.id).label('post_count'),
                func.sum(Post.views).label('total_views')
            ).join(Post).group_by(VA.id).order_by(func.count(Post.id).desc()).limit(5).all()
            
            print("\n   Top 5 VAs by Post Count:")
            for va_name, post_count, total_views in top_vas:
                print(f"   - {va_name}: {post_count} posts, {total_views:,} total views")
            
            # Top posts by views
            top_posts = session.query(Post).order_by(Post.views.desc()).limit(5).all()
            
            print("\n   Top 5 Posts by Views:")
            for post in top_posts:
                va_name = post.va.name if post.va else "No VA"
                print(f"   - {post.account} ({va_name}): {post.views:,} views")
            
            # Posts with slides
            posts_with_slides = session.query(Post).filter(
                Post.slides.isnot(None)
            ).count()
            
            print(f"\n   Posts with slides: {posts_with_slides}")
            
            # Export demo
            print("\n📤 Export Demo:")
            exporter = DataExporter(session)
            
            # Export VA performance
            va_report_path = Path(__file__).parent.parent / "analysis_reports" / "va_performance_demo.csv"
            va_report_path.parent.mkdir(exist_ok=True)
            
            exported_count = exporter.export_va_performance(str(va_report_path))
            print(f"   Exported VA performance report: {exported_count} VAs")
            print(f"   File: {va_report_path}")
            
        finally:
            session.close()
    
    else:
        print(f"\n⚠️  CSV file not found: {csv_path}")
        print("   Skipping data import demo...")
    
    print("\n🎉 Database demo completed successfully!")
    print("\nNext steps:")
    print("   1. Run tests: python -m pytest tests/test_models.py -v")
    print("   2. Import full data: python database/import_utils.py")
    print("   3. Create migrations: alembic revision --autogenerate -m 'description'")
    print("   4. Apply migrations: alembic upgrade head")


if __name__ == "__main__":
    main()
