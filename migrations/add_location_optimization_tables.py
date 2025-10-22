#!/usr/bin/env python3
"""
Migration: Add Location Optimization Tables
Adds all tables needed for TikTok USA audience optimization system

Tables Added:
- location_metrics: Track USA percentage over time
- warmup_sessions: Log warm-up engagement sessions
- profile_analyses: Store USA profile analysis results
- comment_management: Track comment engagement strategies
- posting_optimization: Optimal posting time tracking
- sound_verification: Sound verification for USA audience
- location_optimization_alerts: Alert management
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add the database package to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

from database.location_optimization_models import (
    LocationMetrics, WarmupSession, ProfileAnalysis, CommentManagement,
    PostingOptimization, SoundVerification, LocationOptimizationAlert
)

def run_migration():
    """Run the migration to add location optimization tables"""
    
    print("🔄 Starting Location Optimization Tables Migration")
    print("=" * 60)
    
    # Database connection
    database_url = "sqlite:///tiktok_analytics.db"
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if tables already exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        new_tables = [
            ('location_metrics', LocationMetrics),
            ('warmup_sessions', WarmupSession),
            ('profile_analyses', ProfileAnalysis),
            ('comment_management', CommentManagement),
            ('posting_optimization', PostingOptimization),
            ('sound_verification', SoundVerification),
            ('location_optimization_alerts', LocationOptimizationAlert)
        ]
        
        tables_created = 0
        tables_skipped = 0
        
        for table_name, model_class in new_tables:
            if table_name in existing_tables:
                print(f"⏭️  Table '{table_name}' already exists - skipping")
                tables_skipped += 1
                continue
            
            print(f"📊 Creating table: {table_name}")
            
            try:
                # Create the table
                model_class.__table__.create(engine, checkfirst=True)
                tables_created += 1
                print(f"   ✅ Table '{table_name}' created successfully")
                
            except Exception as e:
                print(f"   ❌ Error creating table '{table_name}': {e}")
                continue
        
        print("\n" + "=" * 60)
        print(f"📈 Migration Summary:")
        print(f"   Tables created: {tables_created}")
        print(f"   Tables skipped: {tables_skipped}")
        print(f"   Total tables: {len(new_tables)}")
        
        if tables_created > 0:
            print(f"\n✅ Migration completed successfully!")
            print(f"🎯 Location optimization system is ready to use")
        else:
            print(f"\n⚠️  No new tables were created (all tables already exist)")
        
        # Verify table creation
        print(f"\n🔍 Verifying table creation...")
        inspector = inspect(engine)
        updated_tables = inspector.get_table_names()
        
        for table_name, _ in new_tables:
            if table_name in updated_tables:
                # Get column information
                columns = inspector.get_columns(table_name)
                print(f"   ✅ {table_name}: {len(columns)} columns")
            else:
                print(f"   ❌ {table_name}: NOT FOUND")
        
        # Create initial data if needed
        print(f"\n🌱 Creating initial data...")
        await create_initial_data(session)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()

async def create_initial_data(session):
    """Create initial data for location optimization system"""
    
    try:
        # Create sample location metrics for existing accounts
        existing_accounts = session.execute(text("""
            SELECT DISTINCT account FROM posts 
            WHERE created_at >= :date
            LIMIT 5
        """), {"date": datetime.utcnow().replace(day=1)}).fetchall()
        
        if existing_accounts:
            print(f"   📊 Creating sample location metrics for {len(existing_accounts)} accounts")
            
            for row in existing_accounts:
                account = row.account
                
                # Check if location metrics already exist
                existing_metrics = session.execute(text("""
                    SELECT id FROM location_metrics WHERE account = :account
                """), {"account": account}).fetchone()
                
                if not existing_metrics:
                    # Create sample metrics
                    sample_metrics = LocationMetrics(
                        account=account,
                        usa_percentage=85.0,  # Sample starting value
                        non_usa_percentage=15.0,
                        total_audience=10000,
                        usa_engagements=8500,
                        non_usa_engagements=1500,
                        confidence_score=0.8,
                        data_source='initial_setup',
                        recorded_at=datetime.utcnow()
                    )
                    
                    session.add(sample_metrics)
                    print(f"     ✅ Created sample metrics for {account}")
        
        # Create sample warm-up session
        sample_session = WarmupSession(
            session_id="initial_setup_session",
            account="system",
            session_type="maintenance",
            duration_minutes=10,
            keywords_searched=["USA pickup truck", "blue collar USA"],
            profiles_analyzed=5,
            profiles_engaged=3,
            comments_made=8,
            follows_made=2,
            usa_signals_strengthened=4,
            success_score=0.75,
            notes="Initial system setup session",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        session.add(sample_session)
        print(f"   ✅ Created sample warm-up session")
        
        # Create sample alert
        sample_alert = LocationOptimizationAlert(
            account="system",
            alert_type="system_initialized",
            alert_level="info",
            message="Location optimization system initialized successfully",
            recommendation="Begin monitoring accounts and executing warm-up sessions",
            triggered_at=datetime.utcnow()
        )
        
        session.add(sample_alert)
        print(f"   ✅ Created system initialization alert")
        
        session.commit()
        print(f"   ✅ Initial data created successfully")
        
    except Exception as e:
        print(f"   ❌ Error creating initial data: {e}")
        session.rollback()
        raise

def verify_migration():
    """Verify that the migration was successful"""
    
    print(f"\n🔍 Verifying migration...")
    
    database_url = "sqlite:///tiktok_analytics.db"
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check table counts
        tables_to_check = [
            'location_metrics',
            'warmup_sessions', 
            'profile_analyses',
            'comment_management',
            'posting_optimization',
            'sound_verification',
            'location_optimization_alerts'
        ]
        
        for table_name in tables_to_check:
            try:
                count = session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                print(f"   ✅ {table_name}: {count} records")
            except Exception as e:
                print(f"   ❌ {table_name}: Error - {e}")
        
        # Test inserting a sample record
        print(f"\n🧪 Testing table functionality...")
        
        test_metrics = LocationMetrics(
            account="test_account",
            usa_percentage=95.0,
            non_usa_percentage=5.0,
            total_audience=5000,
            usa_engagements=4750,
            non_usa_engagements=250,
            confidence_score=0.9,
            data_source="test"
        )
        
        session.add(test_metrics)
        session.commit()
        
        # Verify insertion
        inserted = session.execute(text("""
            SELECT usa_percentage FROM location_metrics 
            WHERE account = 'test_account'
        """)).fetchone()
        
        if inserted and inserted.usa_percentage == 95.0:
            print(f"   ✅ Test record inserted and verified successfully")
        else:
            print(f"   ❌ Test record verification failed")
        
        # Clean up test record
        session.execute(text("DELETE FROM location_metrics WHERE account = 'test_account'"))
        session.commit()
        print(f"   🧹 Test record cleaned up")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        session.rollback()
    
    finally:
        session.close()

def main():
    """Main migration function"""
    
    print("🎯 TikTok USA Location Optimization - Database Migration")
    print("=" * 60)
    print(f"📅 Migration Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Database: tiktok_analytics.db")
    print()
    
    try:
        # Run the migration
        run_migration()
        
        # Verify the migration
        verify_migration()
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"🚀 Location optimization system is ready to use!")
        print(f"\n📋 Next steps:")
        print(f"   1. Run the location optimization system")
        print(f"   2. Initialize warm-up schedules for accounts")
        print(f"   3. Start monitoring USA percentage metrics")
        print(f"   4. Access the dashboard at http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"🔄 Please check the error and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
