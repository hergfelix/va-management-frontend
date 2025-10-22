#!/usr/bin/env python3
"""
Bulk Video OCR Downloader
Uses tiktok-downloader (snaptik) to download video thumbnails and extract text via OCR
Works on /video/ URLs (all October posts)
"""

from tiktok_downloader import snaptik
from PIL import Image
import pytesseract
import pandas as pd
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
import re

class BulkVideoOCR:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        # Create subdirectories
        self.thumbnail_dir = self.output_dir / "thumbnails"
        self.thumbnail_dir.mkdir(exist_ok=True)

        self.results = []

    def normalize_text(self, text):
        """Normalize text for comparison"""
        # Remove punctuation, lowercase, remove extra spaces
        text = re.sub(r'[^\w\s]', '', text.lower())
        text = ' '.join(text.split())
        return text

    def download_and_ocr_video(self, post_url, post_data):
        """
        Download video thumbnails using snaptik and run OCR

        Returns: dict with OCR results
        """
        print(f"\n   📹 {post_data['account']} | {post_data['views']:,} views")

        try:
            # Use snaptik to get thumbnails
            results = snaptik(post_url)

            if not results or len(results) == 0:
                print(f"      ⚠️  No results from snaptik")
                return None

            print(f"      ✅ Got {len(results)} thumbnails")

            # Download and OCR each thumbnail
            thumbnail_texts = []
            post_hash = hashlib.md5(post_url.encode()).hexdigest()

            for i, download_obj in enumerate(results, 1):
                # Download thumbnail
                thumbnail_path = self.thumbnail_dir / f"{post_hash}_thumb_{i}.jpg"
                download_obj.download(str(thumbnail_path))

                # Run OCR
                img = Image.open(thumbnail_path)
                text = pytesseract.image_to_string(img).strip()

                if text and len(text) > 5:  # Only include if meaningful text
                    thumbnail_texts.append(text)
                    print(f"      [{i}] OCR: {len(text)} chars")
                else:
                    print(f"      [{i}] (no text)")

            # Combine all text from thumbnails
            combined_text = ' '.join(thumbnail_texts)
            normalized_text = self.normalize_text(combined_text)
            text_hash = hashlib.md5(normalized_text.encode()).hexdigest()

            if normalized_text:
                preview = normalized_text[:80]
                print(f"      📝 Combined: \"{preview}...\"")

            result = {
                'post_url': post_url,
                'account': post_data['account'],
                'va': post_data['va'],
                'views': post_data['views'],
                'created_date': str(post_data['created_date']),
                'thumbnail_count': len(results),
                'thumbnails_with_text': len(thumbnail_texts),
                'ocr_text': normalized_text,
                'text_hash': text_hash,
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            print(f"      ❌ Error: {str(e)[:60]}")
            return None

    def process_posts(self, posts_df, max_posts=100):
        """
        Process October posts with OCR

        posts_df: DataFrame with October posts
        max_posts: Maximum number to process
        """

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║          🎬 BULK VIDEO OCR DOWNLOADER                         ║
║          Snaptik + Tesseract OCR                              ║
╚════════════════════════════════════════════════════════════════╝

Processing up to {max_posts} October posts...
        """)

        # Sample strategy: Mix of high and low performers
        print(f"📊 Sampling strategy:")
        print(f"   - High performers (≥10k views): 50%")
        print(f"   - Regular posts (<10k views): 50%")
        print(f"   - Diverse VA representation")
        print(f"   Total to process: {max_posts}\n")

        # Get diverse sample
        high_performers = posts_df[posts_df['views'] >= 10000]
        low_performers = posts_df[posts_df['views'] < 10000]

        n_high = min(max_posts // 2, len(high_performers))
        n_low = min(max_posts // 2, len(low_performers))

        sample_high = high_performers.sample(n=n_high, random_state=42) if n_high > 0 else pd.DataFrame()
        sample_low = low_performers.sample(n=n_low, random_state=42) if n_low > 0 else pd.DataFrame()

        sample_df = pd.concat([sample_high, sample_low]).sample(frac=1, random_state=42).head(max_posts)

        print(f"✅ Selected {len(sample_df)} posts")
        print(f"   High performers: {len(sample_df[sample_df['views'] >= 10000])}")
        print(f"   Regular posts: {len(sample_df[sample_df['views'] < 10000])}\n")

        # Process each post
        processed = 0
        successful = 0

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

            result = self.download_and_ocr_video(post_data['post_url'], post_data)

            if result:
                self.results.append(result)
                successful += 1

            # Rate limiting to avoid overloading snaptik
            time.sleep(2)

        print(f"\n\n✅ Processing complete!")
        print(f"   Posts processed: {processed}")
        print(f"   Successful OCR: {successful}")
        print(f"   Posts with text: {sum(1 for r in self.results if r['ocr_text'])}")
        print(f"   Thumbnails saved: {len(list(self.thumbnail_dir.glob('*.jpg')))}\n")

        # Save results
        results_file = self.output_dir / "bulk_video_ocr_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"   💾 Results: {results_file}")

        # Generate duplicate report
        self.generate_duplicate_report()

        return self.results

    def generate_duplicate_report(self):
        """Analyze results for duplicate content"""

        print(f"\n" + "="*70)
        print("DUPLICATE CONTENT ANALYSIS")
        print("="*70 + "\n")

        # Group by text hash
        from collections import defaultdict
        hash_groups = defaultdict(list)

        for result in self.results:
            if result['ocr_text']:  # Only consider posts with text
                hash_groups[result['text_hash']].append(result)

        # Find duplicates (same hash, multiple posts)
        duplicates = {h: posts for h, posts in hash_groups.items() if len(posts) > 1}

        print(f"📊 Total posts analyzed: {len(self.results)}")
        print(f"📝 Posts with text: {sum(1 for r in self.results if r['ocr_text'])}")
        print(f"🔄 Unique text patterns: {len(hash_groups)}")
        print(f"⚠️  Duplicate groups: {len(duplicates)}\n")

        if duplicates:
            print("DUPLICATE CONTENT GROUPS:")
            print("-" * 70)

            for i, (text_hash, posts) in enumerate(duplicates.items(), 1):
                print(f"\n{i}. Duplicate Group ({len(posts)} posts)")
                print(f"   Text: \"{posts[0]['ocr_text'][:80]}...\"")
                print(f"   Hash: {text_hash}")
                print(f"\n   Posts:")

                for post in sorted(posts, key=lambda x: x['views'], reverse=True):
                    print(f"      - {post['account']} ({post['va']}) | {post['views']:,} views")
                    print(f"        {post['created_date'][:10]} | {post['post_url']}")
        else:
            print("✅ No exact duplicates found in this sample\n")

        # Save duplicate report
        duplicate_report = {
            'summary': {
                'total_posts': len(self.results),
                'posts_with_text': sum(1 for r in self.results if r['ocr_text']),
                'unique_patterns': len(hash_groups),
                'duplicate_groups': len(duplicates)
            },
            'duplicates': [
                {
                    'text_hash': text_hash,
                    'text_preview': posts[0]['ocr_text'][:100],
                    'posts': [
                        {
                            'account': p['account'],
                            'va': p['va'],
                            'views': p['views'],
                            'date': p['created_date'][:10],
                            'url': p['post_url']
                        }
                        for p in posts
                    ]
                }
                for text_hash, posts in duplicates.items()
            ]
        }

        report_file = self.output_dir / "duplicate_content_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(duplicate_report, f, indent=2, ensure_ascii=False)

        print(f"\n   💾 Duplicate report: {report_file}")


def main():
    """Process October posts"""

    print("Loading October data...")
    df = pd.read_csv(
        '/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/MASTER_TIKTOK_DATABASE.csv',
        quotechar='"', escapechar='\\'
    )
    df['created_date'] = pd.to_datetime(df['created_date'])

    # Filter October 1-16
    oct_df = df[(df['created_date'] >= '2025-10-01') & (df['created_date'] <= '2025-10-16')]

    print(f"✅ Loaded {len(oct_df)} October posts\n")

    # Initialize processor
    output_dir = Path('/Users/felixhergenroeder/🎯 TikTok Analytics Projects/01_Master_Database_Oct_2025/analysis_reports/bulk_video_ocr')
    processor = BulkVideoOCR(output_dir)

    # Process posts (start with 50 for testing)
    results = processor.process_posts(oct_df, max_posts=200)

    print("\n✅ Processing complete!\n")


if __name__ == "__main__":
    main()
