#!/usr/bin/env python3
"""
October Content Quality Analysis
Analyzes VA content quality based on Topics_Config criteria:
- Text extraction (OCR)
- Repost detection
- Viral recycling patterns
- Strategic vs random posting
"""

import pandas as pd
import requests
from PIL import Image
import pytesseract
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from io import BytesIO
from urllib.parse import urlparse
import time

class ContentQualityAnalyzer:
    def __init__(self, database_path, output_dir):
        self.database_path = Path(database_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Cache directories
        self.image_cache = self.output_dir / "image_cache"
        self.ocr_cache = self.output_dir / "ocr_cache"
        self.image_cache.mkdir(exist_ok=True)
        self.ocr_cache.mkdir(exist_ok=True)

        # Data structures
        self.slide_texts = {}  # slide_url -> extracted_text
        self.post_metadata = []  # All post data
        self.va_analysis = defaultdict(lambda: {
            'total_posts': 0,
            'reposts_detected': 0,
            'viral_posts': [],  # Posts with >10k views
            'viral_recycled': 0,  # How many viral posts were recycled
            'sounds_used': defaultdict(int),
            'posting_gaps': [],
            'text_duplicates': [],
            'random_posting_score': 0
        })

    def load_october_data(self, start_date='2025-10-01', end_date='2025-10-16'):
        """Load October data from master database"""
        print(f"\n📊 Loading data from {start_date} to {end_date}...")

        # Read CSV in chunks (it's 32MB) with proper quoting
        chunks = []
        for chunk in pd.read_csv(self.database_path, chunksize=10000, quotechar='"', escapechar='\\'):
            # Filter October dates
            chunk['created_date'] = pd.to_datetime(chunk['created_date'])
            mask = (chunk['created_date'] >= start_date) & (chunk['created_date'] <= end_date)
            october_chunk = chunk[mask]
            if len(october_chunk) > 0:
                chunks.append(october_chunk)

        self.df = pd.concat(chunks, ignore_index=True)
        print(f"✅ Loaded {len(self.df)} posts from October 1-16")
        print(f"   VAs found: {self.df['va'].nunique()}")
        print(f"   Accounts: {self.df['account'].nunique()}")

        return self.df

    def extract_slide_urls(self, slides_field):
        """Extract individual slide URLs from pipe-separated field"""
        if pd.isna(slides_field) or slides_field == '':
            return []

        # Split by pipe
        urls = [url.strip() for url in str(slides_field).split('|') if url.strip()]
        return urls

    def download_image(self, url):
        """Download image from URL with caching"""
        # Create cache filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_file = self.image_cache / f"{url_hash}.jpg"

        if cache_file.exists():
            return cache_file

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(cache_file)
                return cache_file
        except Exception as e:
            print(f"   ⚠️  Failed to download {url[:50]}...: {e}")
            return None

        return None

    def extract_text_from_image(self, image_path):
        """Extract text using OCR (Tesseract)"""
        # Check OCR cache
        cache_file = self.ocr_cache / f"{image_path.stem}.txt"
        if cache_file.exists():
            return cache_file.read_text(encoding='utf-8')

        try:
            img = Image.open(image_path)
            # Run OCR
            text = pytesseract.image_to_string(img)
            # Clean text
            text = text.strip().lower()

            # Cache result
            cache_file.write_text(text, encoding='utf-8')
            return text
        except Exception as e:
            print(f"   ⚠️  OCR failed for {image_path.name}: {e}")
            return ""

    def normalize_text(self, text):
        """Normalize text for comparison"""
        # Remove extra whitespace, lowercase, remove punctuation
        import re
        text = re.sub(r'[^\w\s]', '', text.lower())
        text = ' '.join(text.split())
        return text

    def calculate_text_similarity(self, text1, text2):
        """Calculate similarity between two texts (0-1)"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()

    def analyze_post(self, row):
        """Analyze a single post"""
        va = row['va']
        if pd.isna(va) or va == '':
            return None

        post_data = {
            'va': va,
            'account': row['account'],
            'post_url': row['post_url'],
            'created_date': row['created_date'],
            'views': row['views'],
            'engagement_rate': row.get('engagement_rate', 0),
            'sound': row.get('sound', ''),
            'slides': [],
            'slide_texts': [],
            'is_viral': row['views'] >= 10000,
            'text_hash': None
        }

        # Extract slide URLs
        slide_urls = self.extract_slide_urls(row.get('slides', ''))

        if len(slide_urls) == 0:
            return post_data

        # Process each slide
        all_text = []
        for slide_url in slide_urls[:3]:  # Limit to first 3 slides for speed
            # Download image
            image_path = self.download_image(slide_url)
            if image_path is None:
                continue

            # Extract text
            text = self.extract_text_from_image(image_path)
            if text:
                all_text.append(text)
                post_data['slides'].append({
                    'url': slide_url,
                    'text': text
                })

        # Combine all text from slides
        combined_text = ' '.join(all_text)
        normalized_text = self.normalize_text(combined_text)

        post_data['slide_texts'] = all_text
        post_data['combined_text'] = normalized_text
        post_data['text_hash'] = hashlib.md5(normalized_text.encode()).hexdigest()

        return post_data

    def process_all_posts(self):
        """Process all October posts"""
        print(f"\n🔬 Processing {len(self.df)} posts...")
        print("   This will take a while (downloading images + OCR)...\n")

        processed = 0
        skipped = 0

        for idx, row in self.df.iterrows():
            if idx % 50 == 0:
                print(f"   Progress: {idx}/{len(self.df)} posts processed...")

            post_data = self.analyze_post(row)
            if post_data:
                self.post_metadata.append(post_data)
                processed += 1
            else:
                skipped += 1

            # Rate limiting
            time.sleep(0.1)

        print(f"\n✅ Processing complete!")
        print(f"   Processed: {processed}")
        print(f"   Skipped: {skipped}")

        # Save intermediate results
        results_file = self.output_dir / "post_metadata.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.post_metadata, f, indent=2, ensure_ascii=False, default=str)
        print(f"   💾 Saved: {results_file}")

    def detect_reposts_and_patterns(self):
        """Detect reposts, viral recycling, and posting patterns"""
        print(f"\n🔍 Analyzing repost patterns...")

        # Group posts by VA
        va_posts = defaultdict(list)
        for post in self.post_metadata:
            va = post['va']
            va_posts[va].append(post)

        # Analyze each VA
        for va, posts in va_posts.items():
            analysis = self.va_analysis[va]
            analysis['total_posts'] = len(posts)

            # Sort by date
            posts_sorted = sorted(posts, key=lambda x: x['created_date'])

            # Track text hashes
            text_hashes = defaultdict(list)
            for post in posts_sorted:
                if post['text_hash']:
                    text_hashes[post['text_hash']].append(post)

            # Find duplicates (reposts)
            for text_hash, duplicate_posts in text_hashes.items():
                if len(duplicate_posts) > 1:
                    analysis['reposts_detected'] += len(duplicate_posts) - 1
                    analysis['text_duplicates'].append({
                        'text_sample': duplicate_posts[0]['combined_text'][:100],
                        'count': len(duplicate_posts),
                        'posts': [p['post_url'] for p in duplicate_posts]
                    })

            # Find viral posts
            viral_posts = [p for p in posts if p['is_viral']]
            analysis['viral_posts'] = viral_posts

            # Check if viral posts were recycled
            for viral_post in viral_posts:
                if viral_post['text_hash'] in text_hashes:
                    if len(text_hashes[viral_post['text_hash']]) > 1:
                        analysis['viral_recycled'] += 1

            # Sound analysis
            for post in posts:
                sound = post.get('sound', '')
                if sound:
                    analysis['sounds_used'][sound] += 1

            # Posting gaps
            for i in range(1, len(posts_sorted)):
                prev_date = pd.to_datetime(posts_sorted[i-1]['created_date'])
                curr_date = pd.to_datetime(posts_sorted[i]['created_date'])
                gap_days = (curr_date - prev_date).days
                if gap_days > 1:
                    analysis['posting_gaps'].append(gap_days)

            # Random posting score (0-100, higher = more random/inconsistent)
            # Based on: repost rate, sound diversity, posting gaps
            repost_rate = (analysis['reposts_detected'] / analysis['total_posts'] * 100) if analysis['total_posts'] > 0 else 0
            sound_diversity = len(analysis['sounds_used']) / analysis['total_posts'] if analysis['total_posts'] > 0 else 0
            avg_gap = sum(analysis['posting_gaps']) / len(analysis['posting_gaps']) if analysis['posting_gaps'] else 0

            # Higher repost rate without viral recycling = random/lazy
            # Low sound diversity = not exploring
            # Large gaps = inconsistent
            random_score = 0
            if repost_rate > 30 and analysis['viral_recycled'] == 0:
                random_score += 40  # High reposts but NOT recycling viral = lazy
            if sound_diversity < 0.3:
                random_score += 30  # Using same sounds too much
            if avg_gap > 1:
                random_score += 30  # Inconsistent posting

            analysis['random_posting_score'] = min(random_score, 100)

        print(f"✅ Repost analysis complete for {len(va_posts)} VAs")

    def generate_reports(self):
        """Generate comprehensive VA reports"""
        print(f"\n📝 Generating reports...")

        # Create detailed CSV
        report_rows = []

        for va, analysis in self.va_analysis.items():
            row = {
                'VA': va,
                'Total_Posts': analysis['total_posts'],
                'Reposts_Detected': analysis['reposts_detected'],
                'Repost_Rate_%': round(analysis['reposts_detected'] / analysis['total_posts'] * 100, 1) if analysis['total_posts'] > 0 else 0,
                'Viral_Posts_10k+': len(analysis['viral_posts']),
                'Viral_Recycled': analysis['viral_recycled'],
                'Viral_Recycling_Rate_%': round(analysis['viral_recycled'] / len(analysis['viral_posts']) * 100, 1) if len(analysis['viral_posts']) > 0 else 0,
                'Unique_Sounds': len(analysis['sounds_used']),
                'Sound_Diversity': round(len(analysis['sounds_used']) / analysis['total_posts'], 2) if analysis['total_posts'] > 0 else 0,
                'Posting_Gaps_Count': len(analysis['posting_gaps']),
                'Avg_Gap_Days': round(sum(analysis['posting_gaps']) / len(analysis['posting_gaps']), 1) if analysis['posting_gaps'] else 0,
                'Random_Posting_Score': analysis['random_posting_score']
            }
            report_rows.append(row)

        # Sort by random posting score (worst first)
        df_report = pd.DataFrame(report_rows)
        df_report = df_report.sort_values('Random_Posting_Score', ascending=False)

        # Save CSV
        csv_file = self.output_dir / "02_OCTOBER_CONTENT_QUALITY_REPORT.csv"
        df_report.to_csv(csv_file, index=False)
        print(f"✅ CSV Report: {csv_file}")

        # Generate markdown report
        md_file = self.output_dir / "02_OCTOBER_CONTENT_QUALITY_REPORT.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 🔬 OCTOBER CONTENT QUALITY REPORT\n")
            f.write(f"**Period:** October 1-16, 2025\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total VAs analyzed:** {len(self.va_analysis)}\n")
            f.write(f"- **Total posts:** {sum(a['total_posts'] for a in self.va_analysis.values())}\n")
            f.write(f"- **Reposts detected:** {sum(a['reposts_detected'] for a in self.va_analysis.values())}\n")
            f.write(f"- **Viral posts (10k+):** {sum(len(a['viral_posts']) for a in self.va_analysis.values())}\n\n")

            f.write("---\n\n")
            f.write("## 🚨 VAs with HIGH Random Posting Score (>70)\n\n")
            f.write("*These VAs show signs of lazy/random posting without strategic thinking*\n\n")

            high_random = df_report[df_report['Random_Posting_Score'] >= 70]
            if len(high_random) > 0:
                f.write("| VA | Posts | Repost Rate | Viral Recycled | Random Score | Issue |\n")
                f.write("|---|---|---|---|---|---|\n")
                for _, row in high_random.iterrows():
                    issues = []
                    if row['Repost_Rate_%'] > 30 and row['Viral_Recycled'] == 0:
                        issues.append("High reposts, NO viral recycling")
                    if row['Sound_Diversity'] < 0.3:
                        issues.append("Low sound diversity")
                    if row['Avg_Gap_Days'] > 1:
                        issues.append("Inconsistent posting")

                    f.write(f"| {row['VA']} | {row['Total_Posts']} | {row['Repost_Rate_%']}% | {row['Viral_Recycled']} | {row['Random_Posting_Score']} | {', '.join(issues)} |\n")
            else:
                f.write("*None found - all VAs are posting strategically! ✅*\n")

            f.write("\n---\n\n")
            f.write("## ⚠️ VAs NOT Recycling Viral Content\n\n")

            no_recycling = df_report[(df_report['Viral_Posts_10k+'] > 0) & (df_report['Viral_Recycled'] == 0)]
            if len(no_recycling) > 0:
                f.write("| VA | Viral Posts | Recycled | Issue |\n")
                f.write("|---|---|---|---|\n")
                for _, row in no_recycling.iterrows():
                    f.write(f"| {row['VA']} | {row['Viral_Posts_10k+']} | {row['Viral_Recycled']} | Not leveraging viral content |\n")
            else:
                f.write("*All VAs are recycling their viral content! ✅*\n")

            f.write("\n---\n\n")
            f.write("## 📊 Full Report\n\n")
            f.write("| Rank | VA | Posts | Reposts | Repost % | Viral | Recycled | Sounds | Random Score |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")

            for idx, row in df_report.iterrows():
                f.write(f"| {idx+1} | {row['VA']} | {row['Total_Posts']} | {row['Reposts_Detected']} | {row['Repost_Rate_%']}% | {row['Viral_Posts_10k+']} | {row['Viral_Recycled']} | {row['Unique_Sounds']} | {row['Random_Posting_Score']} |\n")

        print(f"✅ Markdown Report: {md_file}")

        return df_report


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║     🔬 OCTOBER CONTENT QUALITY ANALYZER                       ║
║     Topics Config Compliance Check                            ║
╚════════════════════════════════════════════════════════════════╝
    """)

    # Paths
    database_path = Path(__file__).parent.parent / "MASTER_TIKTOK_DATABASE.csv"
    output_dir = Path(__file__).parent.parent / "analysis_reports"

    # Initialize analyzer
    analyzer = ContentQualityAnalyzer(database_path, output_dir)

    # Step 1: Load October data
    analyzer.load_october_data(start_date='2025-10-01', end_date='2025-10-16')

    # Step 2: Process posts (OCR + metadata extraction)
    analyzer.process_all_posts()

    # Step 3: Detect patterns
    analyzer.detect_reposts_and_patterns()

    # Step 4: Generate reports
    analyzer.generate_reports()

    print("\n✅ Analysis complete!")
    print("   Check analysis_reports/ for results\n")


if __name__ == "__main__":
    main()
