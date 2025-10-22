#!/usr/bin/env python3
"""
Post-Based Slide OCR
Opens TikTok POST (not direct slide URLs), screenshots slides within the post, then OCR
Similar approach to final_comment_scraper.py
"""

from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
import time
import json
from datetime import datetime
from pathlib import Path
import hashlib

class PostSlideOCR:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.screenshot_cache = self.output_dir / "post_screenshots"
        self.screenshot_cache.mkdir(exist_ok=True)

        self.results = []
        self.cookies_file = Path(__file__).parent.parent / "tiktok_cookies.json"

    def scrape_post_slides(self, page, post_url, post_data):
        """
        Open a TikTok post, wait for slides to load, screenshot them, OCR

        Returns: dict with OCR results
        """
        print(f"\n   📹 Loading post: {post_url[:60]}...")

        try:
            # Navigate to post
            page.goto(post_url, wait_until="domcontentloaded", timeout=30000)

            # Wait for content to load
            time.sleep(5)  # Give slides time to render

            # Try to find slideshow container
            # TikTok slideshows have specific selectors
            try:
                # Wait for slideshow to be visible
                page.wait_for_selector('[data-e2e="slideshow"]', timeout=5000)
                print("      ✅ Slideshow detected")
            except:
                print("      ⚠️  No slideshow found (might be video)")
                return None

            # Take screenshot of the whole post area
            post_hash = hashlib.md5(post_url.encode()).hexdigest()
            screenshot_path = self.screenshot_cache / f"{post_hash}.png"

            # Screenshot the main content area (where slides are)
            try:
                # Find the main video/slideshow container
                slideshow_element = page.locator('[data-e2e="slideshow"]').first
                if slideshow_element:
                    slideshow_element.screenshot(path=str(screenshot_path))
                    print(f"      ✅ Screenshot saved")
                else:
                    # Fallback: screenshot whole viewport
                    page.screenshot(path=str(screenshot_path))
                    print(f"      ✅ Full page screenshot saved")
            except:
                # Last resort: full screenshot
                page.screenshot(path=str(screenshot_path))
                print(f"      ⚠️  Fallback screenshot")

            # Run OCR on screenshot
            img = Image.open(screenshot_path)
            text = pytesseract.image_to_string(img)
            text = text.strip().lower()

            print(f"      📝 OCR: {len(text)} chars")
            if text:
                print(f"         Preview: \"{text[:80]}...\"")

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
            print(f"      ❌ Error: {e}")
            return None

    def normalize_text(self, text):
        """Normalize text for comparison"""
        import re
        text = re.sub(r'[^\w\s]', '', text.lower())
        text = ' '.join(text.split())
        return text

    def scrape_posts(self, posts_df, max_posts=10):
        """
        Scrape posts with slides

        posts_df: pandas DataFrame with post data
        max_posts: max number of posts to process
        """

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          🎬 POST SLIDE OCR SCRAPER                            ║
║          Opens TikTok posts → Screenshots → OCR               ║
╚════════════════════════════════════════════════════════════════╝

Processing up to {max_posts} posts...
        """)

        # Filter posts with slides (has slide URLs in CSV)
        posts_with_slides = posts_df[posts_df['slides'].notna() & (posts_df['slides'] != '')]

        if len(posts_with_slides) == 0:
            print("❌ No posts with slides found!")
            return

        print(f"✅ Found {len(posts_with_slides)} posts with slides")
        print(f"   Processing first {min(max_posts, len(posts_with_slides))}...\n")

        with sync_playwright() as p:
            # Launch browser (visible to help with debugging)
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

            for idx, row in posts_with_slides.head(max_posts).iterrows():
                processed += 1
                print(f"\n[{processed}/{min(max_posts, len(posts_with_slides))}]")

                post_data = {
                    'post_url': row['post_url'],
                    'account': row['account'],
                    'va': row['va'],
                    'views': row['views'],
                    'created_date': row['created_date']
                }

                result = self.scrape_post_slides(page, post_data['post_url'], post_data)

                if result:
                    self.results.append(result)

                # Rate limiting
                time.sleep(3)

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
        print(f"   Screenshots saved: {len(list(self.screenshot_cache.glob('*.png')))}")

        # Save results
        results_file = self.output_dir / "post_slide_ocr_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"   💾 Results: {results_file}\n")

        return self.results


def main():
    """Test with sample posts"""
    import pandas as pd

    print("Loading October data...")
    df = pd.read_csv(
        '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv',
        quotechar='"', escapechar='\\'
    )
    df['created_date'] = pd.to_datetime(df['created_date'])

    # Filter October
    oct_df = df[(df['created_date'] >= '2025-10-01') & (df['created_date'] <= '2025-10-16')]

    print(f"✅ Loaded {len(oct_df)} October posts\n")

    # Initialize scraper
    output_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/post_slide_ocr_test')
    scraper = PostSlideOCR(output_dir)

    # Test with first 5 posts
    results = scraper.scrape_posts(oct_df, max_posts=5)

    # Show results
    if results:
        print("\n📊 RESULTS:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['account']} ({result['va']})")
            print(f"   Views: {result['views']:,}")
            if result['ocr_text']:
                print(f"   Text: \"{result['ocr_text'][:100]}...\"")
            else:
                print(f"   Text: (empty)")

    print("\n✅ Test complete!\n")


if __name__ == "__main__":
    main()
