#!/usr/bin/env python3
"""
Test Comprehensive Scraper - Verify slide columns are included
Tests with 3 URLs to validate complete column structure
"""

import asyncio
import pandas as pd
from datetime import datetime
from comprehensive_scraper import ComprehensiveTikTokScraper
import sys

# Test with 3 URLs from proof log
TEST_URLS = [
    {
        'post_url': 'https://www.tiktok.com/@megannprime/video/7330716631651519786',
        'creator': 'MEGAN',
        'set_id': '1',
        'va': 'Mara',
        'type': 'NEW'
    },
    {
        'post_url': 'https://www.tiktok.com/@tyrabugged/video/7330368199887834398',
        'creator': 'TYRA',
        'set_id': '1',
        'va': 'Mara',
        'type': 'NEW'
    },
    {
        'post_url': 'https://www.tiktok.com/@sofiathighs/video/7331141479476866342',
        'creator': 'SOFIA',
        'set_id': '1',
        'va': 'Almira',
        'type': 'NEW'
    }
]


async def test_scraper():
    """Test comprehensive scraper and verify column structure"""
    print("=" * 80)
    print("🧪 TESTING COMPREHENSIVE SCRAPER - Slide Column Validation")
    print("=" * 80)
    print(f"Testing {len(TEST_URLS)} URLs")
    print()
    sys.stdout.flush()

    results = []

    async with ComprehensiveTikTokScraper(headless=True) as scraper:
        for i, test_data in enumerate(TEST_URLS, 1):
            print(f"[{i}/{len(TEST_URLS)}] Testing {test_data['post_url']}")
            result = await scraper.scrape_video_and_account(
                test_data['post_url'],
                i,
                len(TEST_URLS),
                test_data
            )
            results.append(result)

            # Rate limiting
            if i < len(TEST_URLS):
                await asyncio.sleep(3)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Validate column structure
    print()
    print("=" * 80)
    print("📊 COLUMN VALIDATION")
    print("=" * 80)

    expected_columns = 43  # Updated: 30 original + 13 new (slide_count + slide_1..slide_12)
    actual_columns = len(df.columns)

    print(f"Expected columns: {expected_columns}")
    print(f"Actual columns: {actual_columns}")
    print()

    # Check for slide columns
    slide_cols = [f'slide_{i}' for i in range(1, 13)]
    slide_cols.append('slide_count')

    missing_slides = [col for col in slide_cols if col not in df.columns]

    if missing_slides:
        print("❌ MISSING SLIDE COLUMNS:")
        for col in missing_slides:
            print(f"   - {col}")
    else:
        print("✅ ALL SLIDE COLUMNS PRESENT")

    # Display column list
    print()
    print("📋 FULL COLUMN LIST:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")

    # Save test output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"TEST_COMPREHENSIVE_SCRAPER_{timestamp}.csv"
    df.to_csv(output_file, index=False)

    # Summary
    print()
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

    successful = sum(1 for r in results if r.get('scraping_success', False))
    print(f"Successful scrapes: {successful}/{len(results)}")
    print(f"Column count: {actual_columns}")
    print(f"Slide columns: {'✅ Present' if not missing_slides else '❌ Missing'}")
    print()
    print(f"💾 Test output saved to: {output_file}")
    print("=" * 80)
    sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(test_scraper())
