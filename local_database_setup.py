#!/usr/bin/env python3
"""
Local SQLite Database Setup
Creates the same schema as Supabase but runs locally
No account needed, works immediately
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def create_local_database(db_path: str = "./tiktok_analytics.db"):
    """Create local SQLite database with production schema"""

    print("🔧 Creating local SQLite database...")
    print(f"📁 Location: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table 1: TikTok Posts (Main table)
    print("\n📊 Creating tiktok_posts table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tiktok_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        -- Core Identification
        va_url TEXT,
        post_url TEXT UNIQUE NOT NULL,
        created_date TIMESTAMP,
        creator VARCHAR(100),
        set_id INTEGER,
        set_code VARCHAR(20),
        va VARCHAR(50),
        post_type VARCHAR(10),
        platform VARCHAR(20) DEFAULT 'tiktok',
        account VARCHAR(100),

        -- Timestamps
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        first_scraped_at TIMESTAMP,
        last_scraped_at TIMESTAMP,

        -- Engagement Metrics
        views BIGINT DEFAULT 0,
        likes BIGINT DEFAULT 0,
        comments BIGINT DEFAULT 0,
        shares BIGINT DEFAULT 0,
        bookmarks BIGINT DEFAULT 0,
        engagement BIGINT DEFAULT 0,
        engagement_rate DECIMAL(5,2) DEFAULT 0,

        -- Account Information
        account_username VARCHAR(100),
        account_followers BIGINT DEFAULT 0,
        account_following BIGINT DEFAULT 0,
        account_posts BIGINT DEFAULT 0,
        account_likes BIGINT DEFAULT 0,
        account_verified BOOLEAN DEFAULT FALSE,

        -- Content Details
        post_description TEXT,
        hashtags TEXT,
        mentions TEXT,
        content_length INTEGER DEFAULT 0,

        -- Sound Information
        sound_title TEXT,
        sound_author TEXT,
        has_sound BOOLEAN DEFAULT FALSE,

        -- Slide Information (for carousel posts)
        slide_count INTEGER DEFAULT 0,

        -- Metadata
        scraped_at TIMESTAMP,
        scraping_method VARCHAR(50),
        scraping_success BOOLEAN DEFAULT FALSE,
        data_quality VARCHAR(20),
        error TEXT,

        -- Tracking
        follower_change_30d INTEGER DEFAULT 0,
        last_follower_check TIMESTAMP
    )
    """)

    # Table 2: TikTok Slides (Carousel images)
    print("🖼️  Creating tiktok_slides table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tiktok_slides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        slide_number INTEGER NOT NULL,
        slide_url TEXT,
        local_path TEXT,
        cloud_url TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (post_id) REFERENCES tiktok_posts(id) ON DELETE CASCADE,
        UNIQUE(post_id, slide_number)
    )
    """)

    # Table 3: Scraping Logs (Audit trail)
    print("📝 Creating scraping_logs table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scraping_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        total_urls INTEGER DEFAULT 0,
        successful INTEGER DEFAULT 0,
        failed INTEGER DEFAULT 0,
        source VARCHAR(50),
        status VARCHAR(20) DEFAULT 'in_progress',
        error_log TEXT
    )
    """)

    # Create indexes for performance
    print("⚡ Creating indexes...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_url ON tiktok_posts(post_url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_creator ON tiktok_posts(creator)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_va ON tiktok_posts(va)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraped_at ON tiktok_posts(scraped_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_id ON tiktok_slides(post_id)")

    conn.commit()

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("\n✅ Database created successfully!")
    print(f"\n📋 Tables created:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   - {table[0]}: {count} rows")

    conn.close()

    return db_path

def test_database(db_path: str = "./tiktok_analytics.db"):
    """Test database with sample data"""

    print("\n🧪 Testing database with sample data...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert test post
    cursor.execute("""
    INSERT INTO tiktok_posts (
        post_url, creator, account_username, views, likes, comments,
        post_description, scraped_at, scraping_success
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "https://www.tiktok.com/@test/video/123456789",
        "test_creator",
        "testuser",
        1000,
        100,
        10,
        "Test post description",
        datetime.now().isoformat(),
        True
    ))

    post_id = cursor.lastrowid

    # Insert test slides
    cursor.execute("""
    INSERT INTO tiktok_slides (post_id, slide_number, slide_url)
    VALUES (?, ?, ?)
    """, (post_id, 1, "https://example.com/slide1.jpg"))

    cursor.execute("""
    INSERT INTO tiktok_slides (post_id, slide_number, slide_url)
    VALUES (?, ?, ?)
    """, (post_id, 2, "https://example.com/slide2.jpg"))

    conn.commit()

    # Query test
    cursor.execute("""
    SELECT p.post_url, p.views, COUNT(s.id) as slide_count
    FROM tiktok_posts p
    LEFT JOIN tiktok_slides s ON p.id = s.post_id
    GROUP BY p.id
    """)

    result = cursor.fetchone()

    print(f"✅ Test insert successful!")
    print(f"   Post URL: {result[0]}")
    print(f"   Views: {result[1]}")
    print(f"   Slides: {result[2]}")

    # Clean up test data
    cursor.execute("DELETE FROM tiktok_posts WHERE post_url LIKE '%test%'")
    conn.commit()
    conn.close()

    print("✅ Test data cleaned up")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TikTok Analytics - Local Database Setup")
    print("=" * 60)

    # Create database
    db_path = create_local_database()

    # Test it
    test_database(db_path)

    print("\n" + "=" * 60)
    print("🎉 Database ready!")
    print("=" * 60)
    print(f"\n📁 Database location: {Path(db_path).absolute()}")
    print("\n📚 Next steps:")
    print("   1. Update .env to use local database")
    print("   2. Test with existing CSV files")
    print("   3. Migrate to Supabase later when ready")
    print("\n💡 To view data:")
    print("   - Install DB Browser: brew install --cask db-browser-for-sqlite")
    print("   - Or use sqlite3 CLI: sqlite3 tiktok_analytics.db")
