#!/usr/bin/env python3
"""
SQLite Database Writer
Drop-in replacement for Supabase writer
Works with local SQLite database
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLiteWriter:
    """Write scraped data to local SQLite database"""

    def __init__(self, db_path: str = "./tiktok_analytics.db"):
        self.db_path = db_path
        self.conn = None
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database if it doesn't exist"""
        if not Path(self.db_path).exists():
            logger.warning(f"Database not found. Creating at {self.db_path}")
            from local_database_setup import create_local_database
            create_local_database(self.db_path)

    def connect(self):
        """Open database connection"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def insert_post(self, post_data: Dict) -> int:
        """Insert or update a TikTok post"""
        conn = self.connect()
        cursor = conn.cursor()

        # Check if post already exists
        cursor.execute("SELECT id FROM tiktok_posts WHERE post_url = ?",
                      (post_data['post_url'],))
        existing = cursor.fetchone()

        if existing:
            logger.info(f"Updating existing post: {post_data['post_url']}")
            return self._update_post(cursor, existing[0], post_data)
        else:
            logger.info(f"Inserting new post: {post_data['post_url']}")
            return self._insert_new_post(cursor, post_data)

    def _insert_new_post(self, cursor, post_data: Dict) -> int:
        """Insert new post"""
        cursor.execute("""
        INSERT INTO tiktok_posts (
            va_url, post_url, created_date, creator, set_id, set_code, va,
            post_type, platform, account, logged_at, first_scraped_at,
            last_scraped_at, views, likes, comments, shares, bookmarks,
            engagement, engagement_rate, account_username, account_followers,
            account_following, account_posts, account_likes, account_verified,
            post_description, hashtags, mentions, content_length, sound_title,
            sound_author, has_sound, slide_count, scraped_at, scraping_method,
            scraping_success, data_quality, error
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """, (
            post_data.get('va_url'),
            post_data['post_url'],
            post_data.get('created_date'),
            post_data.get('creator'),
            post_data.get('set_id'),
            post_data.get('set_code'),
            post_data.get('va'),
            post_data.get('type'),
            post_data.get('platform', 'tiktok'),
            post_data.get('account'),
            datetime.now().isoformat(),
            post_data.get('scraped_at'),
            post_data.get('scraped_at'),
            post_data.get('views', 0),
            post_data.get('likes', 0),
            post_data.get('comments', 0),
            post_data.get('shares', 0),
            post_data.get('bookmarks', 0),
            post_data.get('engagement', 0),
            post_data.get('engagement_rate', 0.0),
            post_data.get('account_username', 'Unknown'),
            post_data.get('account_followers', 0),
            post_data.get('account_following', 0),
            post_data.get('account_posts', 0),
            post_data.get('account_likes', 0),
            post_data.get('account_verified', False),
            post_data.get('post_description', ''),
            post_data.get('hashtags', ''),
            post_data.get('mentions', ''),
            post_data.get('content_length', 0),
            post_data.get('sound_title', ''),
            post_data.get('sound_author', ''),
            post_data.get('has_sound', False),
            post_data.get('slide_count', 0),
            post_data.get('scraped_at'),
            post_data.get('scraping_method', 'unknown'),
            post_data.get('scraping_success', False),
            post_data.get('data_quality', 'Unknown'),
            post_data.get('error', '')
        ))

        post_id = cursor.lastrowid
        self.conn.commit()
        logger.info(f"✅ Inserted post ID: {post_id}")
        return post_id

    def _update_post(self, cursor, post_id: int, post_data: Dict) -> int:
        """Update existing post"""
        cursor.execute("""
        UPDATE tiktok_posts SET
            views = ?, likes = ?, comments = ?, shares = ?, bookmarks = ?,
            engagement = ?, engagement_rate = ?, account_followers = ?,
            account_following = ?, account_posts = ?, last_scraped_at = ?
        WHERE id = ?
        """, (
            post_data.get('views', 0),
            post_data.get('likes', 0),
            post_data.get('comments', 0),
            post_data.get('shares', 0),
            post_data.get('bookmarks', 0),
            post_data.get('engagement', 0),
            post_data.get('engagement_rate', 0.0),
            post_data.get('account_followers', 0),
            post_data.get('account_following', 0),
            post_data.get('account_posts', 0),
            datetime.now().isoformat(),
            post_id
        ))

        self.conn.commit()
        logger.info(f"✅ Updated post ID: {post_id}")
        return post_id

    def insert_slides(self, post_id: int, slides: List[Dict]):
        """Insert slides for a carousel post"""
        conn = self.connect()
        cursor = conn.cursor()

        for slide in slides:
            cursor.execute("""
            INSERT OR REPLACE INTO tiktok_slides
            (post_id, slide_number, slide_url, local_path, cloud_url)
            VALUES (?, ?, ?, ?, ?)
            """, (
                post_id,
                slide['slide_number'],
                slide['slide_url'],
                slide.get('local_path'),
                slide.get('cloud_url')
            ))

        conn.commit()
        logger.info(f"✅ Inserted {len(slides)} slides for post {post_id}")

    def batch_insert(self, posts: List[Dict]) -> Dict:
        """Insert multiple posts in batch"""
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for post in posts:
            try:
                post_id = self.insert_post(post)
                results['successful'] += 1

                # Insert slides if present
                slides = []
                for i in range(1, 13):
                    slide_url = post.get(f'slide_{i}')
                    if slide_url:
                        slides.append({
                            'slide_number': i,
                            'slide_url': slide_url
                        })

                if slides:
                    self.insert_slides(post_id, slides)

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'url': post.get('post_url'),
                    'error': str(e)
                })
                logger.error(f"❌ Failed to insert {post.get('post_url')}: {e}")

        return results

    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = self.connect()
        cursor = conn.cursor()

        stats = {}

        # Total posts
        cursor.execute("SELECT COUNT(*) FROM tiktok_posts")
        stats['total_posts'] = cursor.fetchone()[0]

        # Total slides
        cursor.execute("SELECT COUNT(*) FROM tiktok_slides")
        stats['total_slides'] = cursor.fetchone()[0]

        # Posts by VA
        cursor.execute("""
        SELECT va, COUNT(*) as count
        FROM tiktok_posts
        WHERE va IS NOT NULL
        GROUP BY va
        """)
        stats['posts_by_va'] = dict(cursor.fetchall())

        # Total engagement
        cursor.execute("SELECT SUM(views), SUM(likes), SUM(comments) FROM tiktok_posts")
        views, likes, comments = cursor.fetchone()
        stats['total_engagement'] = {
            'views': views or 0,
            'likes': likes or 0,
            'comments': comments or 0
        }

        return stats


def test_writer():
    """Test the SQLite writer"""
    print("🧪 Testing SQLite Writer...")

    writer = SQLiteWriter()

    # Test data
    test_post = {
        'post_url': 'https://www.tiktok.com/@test/video/999',
        'creator': 'test_creator',
        'va': 'TestVA',
        'account_username': 'testuser',
        'views': 5000,
        'likes': 500,
        'comments': 50,
        'shares': 10,
        'engagement': 560,
        'engagement_rate': 11.2,
        'post_description': 'Test post',
        'scraped_at': datetime.now().isoformat(),
        'scraping_success': True,
        'slide_count': 2,
        'slide_1': 'https://example.com/slide1.jpg',
        'slide_2': 'https://example.com/slide2.jpg'
    }

    # Insert test post
    post_id = writer.insert_post(test_post)
    print(f"✅ Inserted test post with ID: {post_id}")

    # Get stats
    stats = writer.get_stats()
    print(f"\n📊 Database Stats:")
    print(f"   Total posts: {stats['total_posts']}")
    print(f"   Total slides: {stats['total_slides']}")
    print(f"   Total views: {stats['total_engagement']['views']:,}")

    writer.close()
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_writer()
