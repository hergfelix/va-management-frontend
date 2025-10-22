#!/usr/bin/env python3
"""
Video Thumbnail OCR
Downloads video thumbnail images from TikTok CDN and runs OCR to extract text overlays

Since ALL posts are videos (not slideshows), we'll use the thumbnail images instead.
"""

import pandas as pd
import requests
from PIL import Image
import pytesseract
from io import BytesIO
from pathlib import Path
import hashlib
import json
from datetime import datetime
import time

class VideoThumbnailOCR:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.thumbnail_cache = self.output_dir / "thumbnails"
        self.thumbnail_cache.mkdir(exist_ok=True)

        self.results = []

    def download_and_ocr_thumbnail(self, thumbnail_url):
        """
        Download thumbnail image and extract text

        Returns: extracted text string
        """
        # Generate cache filename
        url_hash = hashlib.md5(thumbnail_url.encode()).hexdigest()
        cache_file = self.thumbnail_cache / f"{url_hash}.txt"
        image_file = self.thumbnail_cache / f"{url_hash}.jpg"

        # Check if we already processed this
        if cache_file.exists():
            return cache_file.read_text(encoding='utf-8')

        try:
            # Download image with headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://www.tiktok.com/',
                'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
            }

            response = requests.get(thumbnail_url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Save image
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(image_file)

                # Run OCR
                text = pytesseract.image_to_string(img)
                text = text.strip()

                # Cache result
                cache_file.write_text(text, encoding='utf-8')

                return text
            else:
                print(f"      ⚠️  HTTP {response.status_code}")
                return ""

        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}")
            return ""

    def process_post_thumbnails(self, post_data):
        """
        Process all thumbnails for a single video post

        post_data: dict with post info

        Returns: dict with OCR results
        """
        slides_str = post_data.get('slides', '')
        if not slides_str or slides_str == '':
            return None

        # Extract thumbnail URLs
        thumbnail_urls = [url.strip() for url in str(slides_str).split('|') if url.strip()]

        if len(thumbnail_urls) == 0:
            return None

        print(f"\n   📸 {post_data['account']} ({post_data['va']})")
        print(f"      {len(thumbnail_urls)} thumbnails | {post_data['views']:,} views")

        # OCR all thumbnails
        thumbnail_texts = []
        for i, url in enumerate(thumbnail_urls, 1):
            print(f"      [{i}/{len(thumbnail_urls)}]", end=" ")
            text = self.download_and_ocr_thumbnail(url)
            if text:
                print(f"✅ {len(text)} chars")
                thumbnail_texts.append(text)
            else:
                print("(empty)")

        # Combine all text
        combined_text = ' '.join(thumbnail_texts)
        normalized_text = self.normalize_text(combined_text)
        text_hash = hashlib.md5(normalized_text.encode()).hexdigest()

        result = {
            'post_url': post_data['post_url'],
            'account': post_data['account'],
            'va': post_data['va'],
            'views': post_data['views'],
            'created_date': str(post_data['created_date']),
            'thumbnail_count': len(thumbnail_urls),
            'thumbnails_with_text': len(thumbnail_texts),
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

    def process_posts(self, posts_df, max_posts=100):
        """
        Process multiple posts

        posts_df: pandas DataFrame with October posts
        max_posts: max number to process
        """
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          🎬 VIDEO THUMBNAIL OCR                               ║
║          Extract text from video preview images               ║
╚════════════════════════════════════════════════════════════════╝

Processing up to {max_posts} posts...
        """)

        # Filter posts with thumbnail data
        posts_with_thumbnails = posts_df[posts_df['slides'].notna() & (posts_df['slides'] != '')]

        if len(posts_with_thumbnails) == 0:
            print("❌ No posts with thumbnails found!")
            return

        print(f"✅ Found {len(posts_with_thumbnails)} posts with thumbnails")
        print(f"   Processing first {min(max_posts, len(posts_with_thumbnails))}...\n")

        processed = 0
        for idx, row in posts_with_thumbnails.head(max_posts).iterrows():
            processed += 1
            print(f"\n[{processed}/{min(max_posts, len(posts_with_thumbnails))}]")

            post_data = {
                'post_url': row['post_url'],
                'account': row['account'],
                'va': row['va'],
                'views': row['views'],
                'created_date': row['created_date'],
                'slides': row['slides']
            }

            result = self.process_post_thumbnails(post_data)

            if result:
                self.results.append(result)

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        print(f"\n\n✅ Processing complete!")
        print(f"   Posts processed: {len(self.results)}")
        print(f"   Posts with text: {sum(1 for r in self.results if r['combined_text'])}")
        print(f"   Thumbnails cached: {len(list(self.thumbnail_cache.glob('*.jpg')))}")

        # Save results
        results_file = self.output_dir / "video_thumbnail_ocr_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"   💾 Results: {results_file}\n")

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

    print(f"✅ Loaded {len(oct_df)} October posts\n")

    # Initialize processor
    output_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/thumbnail_ocr')
    processor = VideoThumbnailOCR(output_dir)

    # Process first 20 posts (test run)
    results = processor.process_posts(oct_df, max_posts=20)

    # Show results summary
    if results:
        print("\n📊 SAMPLE RESULTS:\n")
        posts_with_text = [r for r in results if r['combined_text']]

        print(f"Posts with text: {len(posts_with_text)}/{len(results)}")

        for i, result in enumerate(posts_with_text[:5], 1):
            print(f"\n{i}. {result['account']} ({result['va']})")
            print(f"   Views: {result['views']:,}")
            print(f"   Thumbnails: {result['thumbnails_with_text']}/{result['thumbnail_count']}")
            if result['combined_text']:
                preview = result['combined_text'][:100]
                print(f"   Text: \"{preview}{'...' if len(result['combined_text']) > 100 else ''}\"")

    print("\n✅ Test complete!\n")


if __name__ == "__main__":
    main()
