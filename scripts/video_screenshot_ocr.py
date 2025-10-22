#!/usr/bin/env python3
"""
Video Screenshot OCR
Opens TikTok VIDEO posts in browser, screenshots the video player, runs OCR

This approach works because:
1. All posts in the database are videos (not slideshows)
2. Video URLs work in browser (unlike expired image URLs)
3. We can screenshot the video player preview/poster frame
"""

from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
import time
import json
from datetime import datetime
from pathlib import Path
import hashlib
import pandas as pd

class VideoScreenshotOCR:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.screenshot_cache = self.output_dir / "video_screenshots"
        self.screenshot_cache.mkdir(exist_ok=True)

        self.results = []
        self.cookies_file = Path(__file__).parent.parent / "tiktok_cookies.json"

    def scrape_video_text(self, page, post_url, post_data):
        """
        Open a TikTok video post, screenshot it, run OCR

        Returns: dict with OCR results
        """
        print(f"\n   📹 Loading: {post_data['account']} | {post_data['views']:,} views")

        try:
            # Navigate to post
            page.goto(post_url, wait_until="domcontentloaded", timeout=30000)

            # Wait for video to load
            time.sleep(4)

            # Try to find video element
            try:
                # Look for video player container
                video_container = page.locator('[data-e2e="browse-video"]').first
                if not video_container.is_visible():
                    # Fallback selectors
                    video_container = page.locator('video').first

                print(f"      ✅ Video loaded")
            except:
                print(f"      ⚠️  Video not found, using full page")
                video_container = None

            # Take screenshot
            post_hash = hashlib.md5(post_url.encode()).hexdigest()
            screenshot_path = self.screenshot_cache / f"{post_hash}.png"

            if video_container and video_container.is_visible():
                video_container.screenshot(path=str(screenshot_path))
            else:
                # Fallback: full page screenshot
                page.screenshot(path=str(screenshot_path), full_page=False)

            print(f"      📸 Screenshot saved")

            # Run OCR
            img = Image.open(screenshot_path)
            text = pytesseract.image_to_string(img)
            text = text.strip()

            print(f"      📝 OCR: {len(text)} chars")
            if text and len(text) > 10:
                preview = text.replace('\n', ' ')[:60]
                print(f"         \"{preview}...\"")

            # Normalize text
            normalized_text = self.normalize_text(text)
            text_hash = hashlib.md5(normalized_text.encode()).hexdigest()

            result = {
                'post_url': post_url,
                'account': post_data['account'],
                'va': post_data['va'],
                'views': post_data['views'],
                'created_date': str(post_data['created_date']),
                'ocr_text': normalized_text,
                'text_hash': text_hash,
                'screenshot_path': str(screenshot_path),
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            print(f"      ❌ Error: {str(e)[:60]}")
            return None

    def normalize_text(self, text):
        """Normalize text for comparison"""
        import re
        text = re.sub(r'[^\w\s]', '', text.lower())
        text = ' '.join(text.split())
        return text

    def scrape_posts(self, posts_df, max_posts=50):
        """
        Scrape video posts

        posts_df: pandas DataFrame with October post data
        max_posts: max number of posts to process
        """

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          🎬 VIDEO SCREENSHOT OCR                              ║
║          Browser-based video text extraction                  ║
╚════════════════════════════════════════════════════════════════╝

Processing up to {max_posts} posts from October...
        """)

        # Sample posts - mix of high and low performers
        print(f"📊 Sampling strategy:")
        print(f"   - Top performers (>10k views)")
        print(f"   - Random sample across all VAs")
        print(f"   Total to process: {max_posts}\\n")

        # Get diverse sample
        high_performers = posts_df[posts_df['views'] >= 10000].head(max_posts // 2)
        low_performers = posts_df[posts_df['views'] < 10000].sample(n=min(max_posts // 2, len(posts_df[posts_df['views'] < 10000])), random_state=42)

        sample_df = pd.concat([high_performers, low_performers]).sample(frac=1, random_state=42).head(max_posts)

        print(f"✅ Selected {len(sample_df)} posts")
        print(f"   High performers: {len(sample_df[sample_df['views'] >= 10000])}")
        print(f"   Regular posts: {len(sample_df[sample_df['views'] < 10000])}\\n")

        with sync_playwright() as p:
            # Launch browser (visible for debugging)
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
            )

            # Load cookies if available
            if self.cookies_file.exists():
                print("🍪 Loading cookies...")
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                    context.add_cookies(cookies)

            page = context.new_page()

            processed = 0

            for idx, row in sample_df.iterrows():
                processed += 1
                print(f"\n[{processed}/{len(sample_df)}]")

                post_data = {
                    'post_url': row['post_url'],
                    'account': row['account'],
                    'va': row['va'],
                    'views': row['views'],
                    'created_date': row['created_date']
                }

                result = self.scrape_video_text(page, post_data['post_url'], post_data)

                if result:
                    self.results.append(result)

                # Rate limiting
                time.sleep(2)

            # Save cookies
            cookies = context.cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)

            print("\n⏸️  Browser will close in 5 seconds...")
            time.sleep(5)

            page.close()
            context.close()
            browser.close()

        print(f"\n✅ Processing complete!")
        print(f"   Posts processed: {len(self.results)}")
        print(f"   Posts with text: {sum(1 for r in self.results if r['ocr_text'])}")
        print(f"   Screenshots saved: {len(list(self.screenshot_cache.glob('*.png')))}\\n")

        # Save results
        results_file = self.output_dir / "video_screenshot_ocr_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"   💾 Results: {results_file}\\n")

        return self.results


def main():
    """Test with October data"""
    print("Loading October data...")
    df = pd.read_csv(
        '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv',
        quotechar='"', escapechar='\\'
    )
    df['created_date'] = pd.to_datetime(df['created_date'])

    # Filter October
    oct_df = df[(df['created_date'] >= '2025-10-01') & (df['created_date'] <= '2025-10-16')]

    print(f"✅ Loaded {len(oct_df)} October posts\\n")

    # Initialize scraper
    output_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/video_screenshot_ocr')
    scraper = VideoScreenshotOCR(output_dir)

    # Test with 10 posts
    results = scraper.scrape_posts(oct_df, max_posts=10)

    # Show results
    if results:
        print("\n📊 RESULTS:")
        posts_with_text = [r for r in results if r['ocr_text']]

        print(f"\nPosts with text detected: {len(posts_with_text)}/{len(results)}")

        for i, result in enumerate(posts_with_text[:5], 1):
            print(f"\n{i}. {result['account']} ({result['va']})")
            print(f"   Views: {result['views']:,}")
            if result['ocr_text']:
                preview = result['ocr_text'][:80]
                print(f"   Text: \"{preview}{'...' if len(result['ocr_text']) > 80 else ''}\"")

    print("\n✅ Test complete!\\n")


if __name__ == "__main__":
    main()
