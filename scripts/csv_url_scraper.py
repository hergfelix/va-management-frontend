#!/usr/bin/env python3
"""
TikTok CSV URL Scraper
Reads URLs from a CSV file and scrapes current TikTok metrics
"""

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TikTokScraper:
    """Scrapes TikTok video metrics using Playwright"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def scrape_video(self, url: str) -> Dict:
        """
        Scrape metrics from a single TikTok video

        Returns dict with: views, likes, comments, shares, bookmarks,
                          account_username, account_followers, error
        """
        result = {
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'bookmarks': 0,
            'account_username': 'Unknown',
            'account_followers': 0,
            'error': ''
        }

        page = self.context.new_page()

        try:
            logger.info(f"Scraping {url}")

            # Navigate to URL with timeout
            page.goto(url, wait_until='networkidle', timeout=30000)

            # Wait for video container to load
            page.wait_for_selector('[data-e2e="browse-video"]', timeout=10000)

            # Extract account username
            try:
                username_elem = page.query_selector('[data-e2e="browse-username"]')
                if username_elem:
                    result['account_username'] = username_elem.inner_text().strip().lstrip('@')
            except Exception as e:
                logger.warning(f"Could not extract username: {e}")

            # Extract follower count
            try:
                followers_elem = page.query_selector('[data-e2e="followers-count"]')
                if followers_elem:
                    followers_text = followers_elem.inner_text().strip()
                    result['account_followers'] = self._parse_count(followers_text)
            except Exception as e:
                logger.warning(f"Could not extract followers: {e}")

            # Extract views
            try:
                views_elem = page.query_selector('[data-e2e="browse-view-count"]')
                if views_elem:
                    views_text = views_elem.inner_text().strip()
                    result['views'] = self._parse_count(views_text)
            except Exception as e:
                logger.warning(f"Could not extract views: {e}")

            # Extract likes
            try:
                likes_elem = page.query_selector('[data-e2e="browse-like-count"]')
                if likes_elem:
                    likes_text = likes_elem.inner_text().strip()
                    result['likes'] = self._parse_count(likes_text)
            except Exception as e:
                logger.warning(f"Could not extract likes: {e}")

            # Extract comments
            try:
                comments_elem = page.query_selector('[data-e2e="browse-comment-count"]')
                if comments_elem:
                    comments_text = comments_elem.inner_text().strip()
                    result['comments'] = self._parse_count(comments_text)
            except Exception as e:
                logger.warning(f"Could not extract comments: {e}")

            # Extract shares
            try:
                shares_elem = page.query_selector('[data-e2e="browse-share-count"]')
                if shares_elem:
                    shares_text = shares_elem.inner_text().strip()
                    result['shares'] = self._parse_count(shares_text)
            except Exception as e:
                logger.warning(f"Could not extract shares: {e}")

            # Extract bookmarks
            try:
                bookmarks_elem = page.query_selector('[data-e2e="undefined-count"]')
                if bookmarks_elem:
                    bookmarks_text = bookmarks_elem.inner_text().strip()
                    result['bookmarks'] = self._parse_count(bookmarks_text)
            except Exception as e:
                logger.warning(f"Could not extract bookmarks: {e}")

            logger.info(f"Successfully scraped {url}: {result['views']} views")

        except PlaywrightTimeout as e:
            error_msg = f"Timeout: {str(e)}"
            result['error'] = error_msg
            logger.error(f"Timeout scraping {url}: {e}")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            result['error'] = error_msg
            logger.error(f"Error scraping {url}: {e}")

        finally:
            page.close()

        return result

    @staticmethod
    def _parse_count(text: str) -> int:
        """Parse TikTok count strings like '1.2M', '45.3K', '234' to integers"""
        text = text.strip().upper()

        # Remove any non-numeric characters except K, M, B, and decimal point
        text = ''.join(c for c in text if c.isdigit() or c in ['K', 'M', 'B', '.'])

        multiplier = 1
        if 'K' in text:
            multiplier = 1_000
            text = text.replace('K', '')
        elif 'M' in text:
            multiplier = 1_000_000
            text = text.replace('M', '')
        elif 'B' in text:
            multiplier = 1_000_000_000
            text = text.replace('B', '')

        try:
            number = float(text) if text else 0
            return int(number * multiplier)
        except ValueError:
            return 0


def process_csv(input_csv_path: str, output_csv_path: Optional[str] = None, headless: bool = True):
    """
    Read URLs from CSV, scrape each one, write results to output CSV

    Args:
        input_csv_path: Path to input CSV with 'post_url' column
        output_csv_path: Path to output CSV (auto-generated if None)
        headless: Run browser in headless mode
    """
    input_path = Path(input_csv_path)

    if not input_path.exists():
        logger.error(f"Input CSV not found: {input_csv_path}")
        return

    # Generate output filename if not provided
    if output_csv_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_csv_path = input_path.parent / f"SCRAPED_{timestamp}.csv"

    output_path = Path(output_csv_path)

    # Read input CSV
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info(f"Found {len(rows)} URLs to scrape")

    # Scrape each URL
    results = []

    with TikTokScraper(headless=headless) as scraper:
        for i, row in enumerate(rows, 1):
            url = row.get('post_url', '').strip()

            if not url:
                logger.warning(f"Row {i}: No URL found, skipping")
                continue

            logger.info(f"Processing {i}/{len(rows)}: {url}")

            # Scrape metrics
            metrics = scraper.scrape_video(url)

            # Calculate engagement
            engagement = (
                metrics['likes'] +
                metrics['comments'] +
                metrics['shares'] +
                metrics['bookmarks']
            )

            # Calculate engagement rate
            engagement_rate = (engagement / metrics['views'] * 100) if metrics['views'] > 0 else 0.0

            # Build result row
            result_row = {
                'post_url': url,
                'scraped_at': datetime.now().isoformat(),
                'views': metrics['views'],
                'likes': metrics['likes'],
                'comments': metrics['comments'],
                'shares': metrics['shares'],
                'bookmarks': metrics['bookmarks'],
                'engagement': engagement,
                'engagement_rate': round(engagement_rate, 2),
                'account_username': metrics['account_username'],
                'account_followers': metrics['account_followers'],
                'error': metrics['error']
            }

            results.append(result_row)

            logger.info(f"Completed {i}/{len(rows)}")

    # Write results to output CSV
    if results:
        fieldnames = [
            'post_url', 'scraped_at', 'views', 'likes', 'comments',
            'shares', 'bookmarks', 'engagement', 'engagement_rate',
            'account_username', 'account_followers', 'error'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        logger.info(f"Results written to {output_path}")
        logger.info(f"Successfully scraped {len([r for r in results if not r['error']])}/{len(results)} URLs")
    else:
        logger.warning("No results to write")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape TikTok metrics from CSV URLs')
    parser.add_argument('input_csv', help='Input CSV file with post_url column')
    parser.add_argument('-o', '--output', help='Output CSV file (auto-generated if not provided)')
    parser.add_argument('--no-headless', action='store_true', help='Show browser window')

    args = parser.parse_args()

    process_csv(
        input_csv_path=args.input_csv,
        output_csv_path=args.output,
        headless=not args.no_headless
    )


if __name__ == '__main__':
    main()
