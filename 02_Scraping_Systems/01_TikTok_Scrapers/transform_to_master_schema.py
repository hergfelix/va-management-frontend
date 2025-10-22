#!/usr/bin/env python3
"""
Transform Comprehensive Scraper Output to Master Database Schema

Converts the DOM scraper CSV output to match the master database structure
defined in master_with_snaptik.csv
"""

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class SchemaTransformer:
    """Transform scraper output to master database schema"""

    # Master schema column order (46 columns)
    MASTER_COLUMNS = [
        'va_url', 'post_url', 'created_date', 'creator', 'set_id', 'set_code',
        'va', 'post_type', 'platform', 'account', 'logged_at', 'first_scraped_at',
        'views', 'likes', 'comments', 'shares', 'engagement', 'engagement_rate',
        'followers', 'last_scraped_at', 'hashtags', 'sound', 'sound_url',
        'slide_count', 'day1_views', 'day2_views', 'day3_views', 'day4_views',
        'day5_views', 'scrape_status', 'scrape_interval', 'scrape_count',
        'days_since_posted', 'ocr_text', 'slide_1', 'slide_2', 'slide_3',
        'slide_4', 'slide_5', 'slide_6', 'slide_7', 'slide_8', 'slide_9',
        'slide_10', 'slide_11', 'slide_12'
    ]

    def __init__(self):
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'warnings': []
        }

    def transform_row(self, scraper_row: Dict[str, str]) -> Dict[str, str]:
        """
        Transform a single scraper output row to master schema

        Scraper columns:
        post_url, creator, set_id, va, type, views, likes, comments, shares,
        bookmarks, engagement, engagement_rate, account_username, account_followers,
        account_following, account_posts, account_likes, account_verified,
        post_description, hashtags, mentions, content_length, sound_title,
        sound_author, has_sound, scraped_at, scraping_method, scraping_success,
        data_quality, error
        """

        self.stats['total'] += 1

        # Skip failed scrapes
        if scraper_row.get('scraping_success') != 'True':
            self.stats['failed'] += 1
            return None

        # Extract timestamp from scraper
        scraped_at = scraper_row.get('scraped_at', '')

        # Parse post URL to extract short URL format
        post_url = scraper_row.get('post_url', '')
        va_url = self._extract_short_url(post_url)

        # Generate set_code from creator and set_id
        set_code = self._generate_set_code(
            scraper_row.get('creator', ''),
            scraper_row.get('set_id', '')
        )

        # Build master schema row
        master_row = {
            # Core identification
            'va_url': va_url,
            'post_url': post_url,
            'created_date': '',  # Not available from scraper
            'creator': scraper_row.get('creator', ''),
            'set_id': scraper_row.get('set_id', ''),
            'set_code': set_code,
            'va': scraper_row.get('va', ''),
            'post_type': scraper_row.get('type', ''),
            'platform': 'tiktok',
            'account': scraper_row.get('account_username', ''),

            # Timestamps
            'logged_at': scraped_at,
            'first_scraped_at': scraped_at,
            'last_scraped_at': scraped_at,

            # Engagement metrics
            'views': scraper_row.get('views', '0'),
            'likes': scraper_row.get('likes', '0'),
            'comments': scraper_row.get('comments', '0'),
            'shares': scraper_row.get('shares', '0'),
            'engagement': scraper_row.get('engagement', '0'),
            'engagement_rate': scraper_row.get('engagement_rate', '0'),
            'followers': scraper_row.get('account_followers', '0'),

            # Content metadata
            'hashtags': scraper_row.get('hashtags', ''),
            'sound': scraper_row.get('sound_title', ''),
            'sound_url': '',  # Not available from scraper
            'slide_count': '',  # Not available from scraper

            # Multi-day tracking (empty for first scrape)
            'day1_views': '',
            'day2_views': '',
            'day3_views': '',
            'day4_views': '',
            'day5_views': '',

            # Scraping management
            'scrape_status': 'active',
            'scrape_interval': 'daily',
            'scrape_count': '1',
            'days_since_posted': '0',

            # OCR and slides (not available from current scraper)
            'ocr_text': '',
            'slide_1': '',
            'slide_2': '',
            'slide_3': '',
            'slide_4': '',
            'slide_5': '',
            'slide_6': '',
            'slide_7': '',
            'slide_8': '',
            'slide_9': '',
            'slide_10': '',
            'slide_11': '',
            'slide_12': ''
        }

        self.stats['successful'] += 1
        return master_row

    def _extract_short_url(self, post_url: str) -> str:
        """Extract or generate short URL from full post URL"""
        if not post_url:
            return ''

        # If already a short URL (contains /t/)
        if '/t/' in post_url:
            return post_url

        # Try to extract from full URL pattern
        # https://www.tiktok.com/@username/video/1234567890
        # We don't have the short URL, so return empty for manual filling
        return ''

    def _generate_set_code(self, creator: str, set_id: str) -> str:
        """Generate set_code from creator and set_id (e.g., MARA_021)"""
        if not creator or not set_id:
            return ''

        creator_upper = creator.upper()[:4]  # First 4 chars
        set_id_padded = str(set_id).zfill(3)  # Pad to 3 digits

        return f"{creator_upper}_{set_id_padded}"

    def transform_file(self, input_path: Path, output_path: Path) -> bool:
        """
        Transform entire CSV file from scraper output to master schema

        Args:
            input_path: Path to scraper output CSV
            output_path: Path to save transformed CSV

        Returns:
            True if successful, False otherwise
        """

        try:
            print(f"Reading from: {input_path}")

            with open(input_path, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)

                transformed_rows = []
                for row in reader:
                    transformed = self.transform_row(row)
                    if transformed:
                        transformed_rows.append(transformed)

            print(f"Writing to: {output_path}")

            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=self.MASTER_COLUMNS)
                writer.writeheader()
                writer.writerows(transformed_rows)

            self._print_stats()
            return True

        except Exception as e:
            print(f"❌ Error transforming file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _print_stats(self):
        """Print transformation statistics"""
        print(f"\n{'='*60}")
        print("Transformation Complete")
        print('='*60)
        print(f"Total rows processed: {self.stats['total']}")
        print(f"✅ Successfully transformed: {self.stats['successful']}")
        print(f"❌ Failed/skipped: {self.stats['failed']}")

        if self.stats['successful'] > 0:
            success_rate = (self.stats['successful'] / self.stats['total']) * 100
            print(f"Success rate: {success_rate:.1f}%")

        if self.stats['warnings']:
            print(f"\n⚠️ Warnings:")
            for warning in self.stats['warnings']:
                print(f"  - {warning}")


def main():
    """Main execution"""

    if len(sys.argv) < 2:
        print("Usage: python transform_to_master_schema.py <input_csv> [output_csv]")
        print("\nExample:")
        print("  python transform_to_master_schema.py COMPREHENSIVE_SCRAPED_50_VIDEOS.csv")
        print("  python transform_to_master_schema.py input.csv output.csv")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        sys.exit(1)

    # Generate output filename if not provided
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        # Add _MASTER_FORMAT suffix
        output_path = input_path.parent / f"{input_path.stem}_MASTER_FORMAT.csv"

    print(f"{'='*60}")
    print("TikTok Scraper → Master Schema Transformation")
    print('='*60)

    transformer = SchemaTransformer()
    success = transformer.transform_file(input_path, output_path)

    if success:
        print(f"\n✅ Transformation complete!")
        print(f"📁 Output saved to: {output_path}")
        print(f"\n📋 Note: Some fields require manual population:")
        print(f"  - va_url (short TikTok URLs)")
        print(f"  - created_date (post creation dates)")
        print(f"  - sound_url (TikTok sound URLs)")
        print(f"  - slide_count, ocr_text, slide_* (image data)")
    else:
        print(f"\n❌ Transformation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
