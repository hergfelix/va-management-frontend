#!/usr/bin/env python3
"""
Browser-Based Slide OCR Scraper
Uses Playwright to load slide images directly in browser, screenshot them, then OCR

Similar to final_comment_scraper.py but for slides instead of comments
"""

from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
import time
import json
from datetime import datetime
from pathlib import Path
import hashlib

class BrowserSlideOCR:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.screenshot_cache = self.output_dir / "screenshots"
        self.ocr_cache = self.output_dir / "ocr_results"
        self.screenshot_cache.mkdir(exist_ok=True)
        self.ocr_cache.mkdir(exist_ok=True)

        self.results = []

    def extract_text_from_slide_url(self, browser_context, slide_url):
        """
        Load a slide URL in browser, screenshot it, run OCR

        Returns: extracted text string
        """
        # Check OCR cache first
        url_hash = hashlib.md5(slide_url.encode()).hexdigest()
        cache_file = self.ocr_cache / f"{url_hash}.txt"

        if cache_file.exists():
            return cache_file.read_text(encoding='utf-8')

        try:
            # Open new page
            page = browser_context.new_page()

            # Navigate to slide URL directly
            print(f"      Loading: {slide_url[:60]}...")
            page.goto(slide_url, wait_until="networkidle", timeout=15000)

            # Wait a bit for image to fully load
            time.sleep(1)

            # Take screenshot
            screenshot_path = self.screenshot_cache / f"{url_hash}.png"
            page.screenshot(path=str(screenshot_path), full_page=False)

            # Close page
            page.close()

            # Run OCR on screenshot
            img = Image.open(screenshot_path)
            text = pytesseract.image_to_string(img)
            text = text.strip().lower()

            # Cache result
            cache_file.write_text(text, encoding='utf-8')

            print(f"      ✅ OCR: {len(text)} chars")
            if text:
                print(f"         Preview: \"{text[:60]}...\"")

            return text

        except Exception as e:
            print(f"      ❌ Error: {e}")
            return ""

    def process_post_slides(self, post_data, browser_context):
        """
        Process all slides for a single post

        post_data: dict with 'post_url', 'account', 'va', 'slides' (pipe-separated URLs)

        Returns: dict with OCR results
        """

        slides_str = post_data.get('slides', '')
        if not slides_str or slides_str == '':
            return None

        # Extract slide URLs
        slide_urls = [url.strip() for url in str(slides_str).split('|') if url.strip()]

        if len(slide_urls) == 0:
            return None

        print(f"\n   📸 Processing {len(slide_urls)} slides for {post_data['account']}")
        print(f"      Post: {post_data['post_url']}")

        slide_texts = []
        for i, url in enumerate(slide_urls[:5], 1):  # Limit to first 5 slides for speed
            print(f"\n      Slide {i}/{min(len(slide_urls), 5)}:")
            text = self.extract_text_from_slide_url(browser_context, url)
            if text:
                slide_texts.append(text)

        # Combine all text
        combined_text = ' '.join(slide_texts)
        normalized_text = self.normalize_text(combined_text)
        text_hash = hashlib.md5(normalized_text.encode()).hexdigest()

        result = {
            'post_url': post_data['post_url'],
            'account': post_data['account'],
            'va': post_data['va'],
            'views': post_data['views'],
            'created_date': str(post_data['created_date']),
            'slide_count': len(slide_urls),
            'slides_processed': len(slide_texts),
            'slide_texts': slide_texts,
            'combined_text': normalized_text,
            'text_hash': text_hash,
            'timestamp': datetime.now().isoformat()
        }

        return result

    def normalize_text(self, text):
        """Normalize text for comparison"""
        import re
        text = re.sub(r'[^\w\s]', '', text.lower())
        text = ' '.join(text.split())
        return text

    def scrape_posts(self, posts_df, max_posts=100):
        """
        Scrape slides for multiple posts

        posts_df: pandas DataFrame with post data
        max_posts: max number of posts to process (default: 100)
        """

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          🖼️  BROWSER SLIDE OCR SCRAPER                        ║
║          Playwright + Tesseract OCR                           ║
╚════════════════════════════════════════════════════════════════╝

Processing up to {max_posts} posts with slides...
        """)

        # Filter posts with slides
        posts_with_slides = posts_df[posts_df['slides'].notna() & (posts_df['slides'] != '')]

        if len(posts_with_slides) == 0:
            print("❌ No posts with slides found!")
            return

        print(f"✅ Found {len(posts_with_slides)} posts with slides")
        print(f"   Processing first {min(max_posts, len(posts_with_slides))}...\n")

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)  # Headless for speed
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
            )

            processed = 0

            for idx, row in posts_with_slides.head(max_posts).iterrows():
                processed += 1
                print(f"\n[{processed}/{min(max_posts, len(posts_with_slides))}] Processing post...")

                post_data = {
                    'post_url': row['post_url'],
                    'account': row['account'],
                    'va': row['va'],
                    'views': row['views'],
                    'created_date': row['created_date'],
                    'slides': row['slides']
                }

                result = self.process_post_slides(post_data, context)

                if result:
                    self.results.append(result)

                # Rate limiting
                time.sleep(1)

            context.close()
            browser.close()

        print(f"\n✅ Processing complete!")
        print(f"   Posts processed: {len(self.results)}")
        print(f"   Screenshots saved: {len(list(self.screenshot_cache.glob('*.png')))}")

        # Save results
        results_file = self.output_dir / "slide_ocr_results.json"
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
    output_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/slide_ocr_test')
    scraper = BrowserSlideOCR(output_dir)

    # Test with first 10 posts
    results = scraper.scrape_posts(oct_df, max_posts=10)

    # Show sample results
    if results:
        print("\n📊 SAMPLE RESULTS:")
        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. {result['account']} ({result['va']})")
            print(f"   Views: {result['views']:,}")
            print(f"   Slides: {result['slides_processed']}")
            if result['combined_text']:
                print(f"   Text: \"{result['combined_text'][:100]}...\"")
            else:
                print(f"   Text: (empty)")

    print("\n✅ Test complete!\n")


if __name__ == "__main__":
    main()
